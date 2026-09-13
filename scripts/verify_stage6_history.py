"""Certify the complete Stage 6 history from raw inputs through summary proofs."""

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
from importlib import metadata
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import zipfile

import pandas as pd

from src.acquisition.download import digest
from src.stage6.annual import input_records
from src.stage6.history import COMMON_FILES, CONTINUITY_FILES, build_history
from src.stage6.operations import KEYS, NON_KEY_CONSUMED
from src.stage6.periods import periods_for_year


EXPECTED_PYTHON = '3.13.9'
DEFAULT_YEARS = tuple(range(2010, 2026))
DEFAULT_PREVIOUS_OUTPUT_REFERENCE = 'db0cd7b'
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
ANNUAL_SOURCE_BASE = {
    f'src/stage6/{name}.py' for name in (
        '__init__', 'annual', 'annual_fares', 'annual_panel', 'bootstrap',
        'inventory', 'operations')
}


class CertificationError(RuntimeError):
    """Raised when evidence is incomplete or does not reconcile."""


def _require(condition, message):
    if not condition:
        raise CertificationError(message)


def _json(path):
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise CertificationError(f'Cannot read JSON evidence {path}: {exc}') from exc
    _require(isinstance(value, dict), f'JSON evidence must be an object: {path}')
    return value


def _lf_sha256(data):
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def lf_digest(path):
    """Hash text metadata after normalizing checkout line endings to LF."""
    return _lf_sha256(Path(path).read_bytes())


def _valid_sha256(value):
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def canonical_parameters(parameters):
    """Return a stable, type-preserving request-parameter representation."""
    return json.dumps(parameters, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False)


def inventory_records(records):
    """Derive source-type counts while enforcing request and manifest uniqueness."""
    records = list(records)
    identities = {
        (record['url'], canonical_parameters(record['params'])) for record in records
    }
    manifests = {Path(record['manifest']).as_posix() for record in records}
    _require(len(identities) == len(records),
             'Source request identities (URL plus canonical parameters) are not unique')
    _require(len(manifests) == len(records), 'Source manifest paths are not unique')

    counts = Counter()
    for record in records:
        kind = record.get('kind')
        name = Path(record['target']).name.lower()
        if kind == 'operations':
            counts['operations'] += 1
        elif kind == 'fare' and 'db1bmarket' in name:
            counts['market'] += 1
        elif kind == 'fare' and 'db1bticket' in name:
            counts['ticket'] += 1
        else:
            raise CertificationError(f'Unclassified source record: {record!r}')
    return {
        'source_identity_count': len(identities),
        'source_manifest_count': len(manifests),
        'fare_archive_count': counts['market'] + counts['ticket'],
        'market_archive_count': counts['market'],
        'ticket_archive_count': counts['ticket'],
        'operations_archive_count': counts['operations'],
    }


def verify_manifest(target, manifest, url, parameters, repo_root):
    """Verify one manifest identity without depending on the process working directory."""
    record = _json(manifest)
    recorded_path = Path(record.get('local_path', ''))
    if not recorded_path.is_absolute():
        recorded_path = Path(repo_root) / recorded_path
    _require(recorded_path.resolve() == Path(target).resolve(),
             f'Manifest path differs from consumed input: {manifest}')
    recorded_parameters = (
        record['query_parameters'] if 'query_parameters' in record
        else {key: record[key] for key in ('year', 'quarter') if key in record}
    )
    _require(record.get('url') == url and recorded_parameters == parameters,
             f'Manifest request identity differs: {manifest}')
    _require(record.get('sha256') == digest(target),
             f'Manifest raw input checksum differs: {manifest}')


def _git(repo_root, *args, text=False):
    try:
        return subprocess.check_output(
            ['git', '-C', str(repo_root), *args], text=text,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        output = exc.output.strip() if isinstance(exc.output, str) else ''
        raise CertificationError(
            f'Git evidence command failed ({" ".join(args)}): {output}') from exc


def git_commit_exists(repo_root, commit):
    try:
        subprocess.run(
            ['git', '-C', str(repo_root), 'cat-file', '-e', f'{commit}^{{commit}}'],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def read_git_blob(repo_root, commit, path):
    return _git(repo_root, 'show', f'{commit}:{path}')


def required_annual_sources(year):
    required = set(ANNUAL_SOURCE_BASE)
    if year >= 2011:
        required.update({'src/stage6/baseline.py', 'src/stage6/continuity.py'})
    if year >= 2012:
        required.update({'src/stage6/periods.py', 'src/acquisition/download.py',
                         'src/config.py'})
    return required


def verify_recorded_sources(proof, year, repo_root, *,
                            commit_exists=git_commit_exists,
                            read_blob=read_git_blob):
    """Verify an immutable annual proof against source blobs at its own commit."""
    commit = proof.get('implementation_commit')
    _require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit),
             f'{year} verification has invalid implementation_commit')
    _require(commit_exists(repo_root, commit),
             f'{year} implementation commit does not exist: {commit}')
    hashes = proof.get('source_sha256_lf_normalized')
    _require(isinstance(hashes, dict) and hashes,
             f'{year} verification lacks recorded source hashes')
    missing_sources = required_annual_sources(year) - set(hashes)
    _require(not missing_sources,
             f'{year} verification lacks required source hashes: '
             f'{sorted(missing_sources)}')
    for path, expected in sorted(hashes.items()):
        _require(_valid_sha256(expected), f'{year} has invalid source SHA-256: {path}')
        actual = _lf_sha256(read_blob(repo_root, commit, path))
        _require(actual == expected,
                 f'{year} historical source hash mismatch at {commit}: {path}')
    return commit


def current_source_hashes(paths, repo_root, head, *, read_blob=read_git_blob):
    """Bind final proof only when current source bytes equal their HEAD blobs."""
    result = {}
    root = Path(repo_root).resolve()
    for source in sorted((Path(path).resolve() for path in paths), key=str):
        try:
            relative = source.relative_to(root).as_posix()
        except ValueError as exc:
            raise CertificationError(f'Certification source is outside repository: {source}') from exc
        working_hash = _lf_sha256(source.read_bytes())
        head_hash = _lf_sha256(read_blob(repo_root, head, relative))
        _require(working_hash == head_hash,
                 f'Current certification source differs from HEAD: {relative}')
        result[relative] = working_hash
    return result


def validate_annual_metadata(proof, quality, year, quarters, months,
                             expected_output_names, expected_input_paths, *,
                             require_baseline, expected_baseline_paths,
                             baseline_hashes):
    """Validate modern annual proof fields while accepting immutable 2010/11 schema."""
    common = {
        'scope', 'successful_full_raw_builds', 'compared_output_files',
        'byte_identical', 'output_sha256', 'input_sha256',
        'source_sha256_lf_normalized', 'implementation_commit', 'python',
        'requirements_pins_verified', 'offline_tests_passed', 'fr24_calls',
        'fr24_credits',
    }
    _require(common.issubset(proof), f'{year} verification lacks required fields')
    _require(isinstance(proof['scope'], str) and proof['scope'].strip(),
             f'{year} verification has empty scope')
    _require(proof['successful_full_raw_builds'] == 2,
             f'{year} verification does not record two successful raw builds')
    _require(proof['byte_identical'] is True,
             f'{year} verification does not record byte-identical builds')
    _require(proof['compared_output_files'] == len(expected_output_names),
             f'{year} compared output count is wrong')
    _require(isinstance(proof['output_sha256'], dict)
             and set(proof['output_sha256']) == set(expected_output_names),
             f'{year} verification output set is wrong')
    _require(all(_valid_sha256(value) for value in proof['output_sha256'].values()),
             f'{year} verification has invalid output SHA-256')
    _require(isinstance(proof['input_sha256'], dict)
             and set(proof['input_sha256']) == set(expected_input_paths),
             f'{year} verification input set is wrong')
    _require(all(_valid_sha256(value) for value in proof['input_sha256'].values()),
             f'{year} verification has invalid input SHA-256')
    _require(proof['python'] == EXPECTED_PYTHON,
             f'{year} verification Python pin is wrong')
    _require(proof['requirements_pins_verified'] is True,
             f'{year} verification lacks positive requirement-pin evidence')
    tests = proof['offline_tests_passed']
    _require(isinstance(tests, int) and not isinstance(tests, bool) and tests > 0,
             f'{year} verification lacks positive offline-test evidence')
    _require(proof['fr24_calls'] == 0 and proof['fr24_credits'] == 0,
             f'{year} verification does not record zero FR24 use')

    if year >= 2012:
        modern = {'year', 'expected_quarters', 'expected_months', 'partial_year',
                  'offline_test_scope', 'offline_test_command'}
        _require(modern.issubset(proof), f'{year} verification lacks modern proof fields')
        _require(proof['year'] == year, f'{year} verification year is wrong')
        _require(proof['expected_quarters'] == list(quarters),
                 f'{year} verification quarter declaration is wrong')
        _require(proof['expected_months'] == list(months),
                 f'{year} verification month declaration is wrong')
        _require(proof['partial_year'] is (year == 2025),
                 f'{year} verification partial-year declaration is wrong')
        _require(proof['offline_test_scope'] == 'full offline test suite'
                 and proof['offline_test_command'] == 'python -m pytest -q',
                 f'{year} verification test procedure is wrong')
    else:
        optional = {
            'year': year, 'expected_quarters': list(quarters),
            'expected_months': list(months), 'partial_year': False,
        }
        for field, expected in optional.items():
            if field in proof:
                _require(proof[field] == expected,
                         f'{year} legacy verification has wrong optional {field}')

    expected_fares = [(year, quarter) for quarter in quarters]
    expected_operations = [(year, month) for month in months]
    actual_fares = [(item.get('year'), item.get('quarter'))
                    for item in quality.get('fares', [])]
    actual_operations = [(item.get('year'), item.get('month'))
                         for item in quality.get('operations', [])]
    _require(quality.get('year') == year and actual_fares == expected_fares,
             f'{year} quality audit has wrong fare period identities')
    _require(actual_operations == expected_operations,
             f'{year} quality audit has wrong operations period identities')
    _require(quality.get('verified_input_count') == len(expected_input_paths)
             and quality.get('source_months_complete') is True,
             f'{year} quality audit is not source-complete')

    recorded_baseline = proof.get('baseline_artifact_sha256', {})
    if require_baseline:
        _require(set(recorded_baseline) == set(expected_baseline_paths),
                 f'{year} baseline artifact set is wrong')
        _require(recorded_baseline == baseline_hashes,
                 f'{year} baseline artifact SHA-256 evidence is wrong')
    else:
        _require(not recorded_baseline,
                 f'{year} development-year proof unexpectedly claims a baseline')


EXCEPTION_FIELDS = (
    'year', 'month', 'raw_rows', 'retained_rows', 'selected_rows',
    'repeated_key_rows_removed_national', 'repeated_key_rows_removed_selected',
    'repeated_key_groups_national', 'repeated_key_groups_selected',
    'repeat_resolution_policy',
    'ambiguous_key_rows_excluded_national', 'ambiguous_key_rows_excluded_selected',
    'ambiguous_key_groups_national', 'ambiguous_key_groups_selected',
    'ambiguous_complete_key_groups', 'ambiguity_policy',
    'missing_scheduled_departure_national', 'missing_scheduled_departure_selected',
    'incomplete_key_policy',
    'missing_flight_number_national', 'missing_flight_number_selected',
    'missing_flight_number_policy',
)


def _positive_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _validate_ambiguity_details(month, year):
    groups = month.get('ambiguous_complete_key_groups')
    national_groups = month.get('ambiguous_key_groups_national')
    selected_groups = month.get('ambiguous_key_groups_selected')
    selected_rows = month.get('ambiguous_key_rows_excluded_selected')
    _require(_positive_integer(national_groups)
             and isinstance(selected_groups, int) and not isinstance(selected_groups, bool)
             and 0 <= selected_groups <= national_groups
             and isinstance(selected_rows, int) and not isinstance(selected_rows, bool)
             and selected_rows >= 0
             and isinstance(groups, list) and len(groups) == national_groups
             and isinstance(month.get('ambiguity_policy'), str)
             and month['ambiguity_policy'].strip(),
             f'{year} ambiguous-key evidence is incomplete')
    selected_airports = month.get('selected_airport_ids')
    _require(isinstance(selected_airports, list) and selected_airports
             and all(isinstance(value, int) and not isinstance(value, bool)
                     for value in selected_airports)
             and len(selected_airports) == len(set(selected_airports)),
             f'{year} ambiguity scope lacks selected airport IDs')
    selected_airports = set(selected_airports)

    key_order = []
    scoped_group_count = scoped_row_count = total_rows = 0
    for group in groups:
        _require(isinstance(group, dict) and set(group) == {
            'key', 'rows', 'consumed_variant_count', 'consumed_variants'},
            f'{year} ambiguous group has wrong schema')
        key = group['key']
        _require(isinstance(key, dict) and set(key) == set(KEYS)
                 and all(value is not None for value in key.values()),
                 f'{year} ambiguous group has incomplete flight key')
        try:
            flight_date = date.fromisoformat(key['FlightDate'])
        except (TypeError, ValueError) as exc:
            raise CertificationError(
                f'{year} ambiguous group has invalid FlightDate') from exc
        integer_keys = [column for column in KEYS if column != 'FlightDate']
        _require(flight_date.year == year and flight_date.month == month.get('month')
                 and all(isinstance(key[column], int)
                         and not isinstance(key[column], bool)
                         for column in integer_keys),
                 f'{year} ambiguous group key has wrong type or period')
        key_identity = canonical_parameters(key)
        key_order.append(key_identity)

        variants = group['consumed_variants']
        _require(_positive_integer(group['rows'])
                 and isinstance(group['consumed_variant_count'], int)
                 and not isinstance(group['consumed_variant_count'], bool)
                 and group['consumed_variant_count'] >= 2
                 and isinstance(variants, list)
                 and len(variants) == group['consumed_variant_count'],
                 f'{year} ambiguous group has invalid variant counts')
        variant_order = []
        variant_rows = 0
        for variant in variants:
            _require(isinstance(variant, dict) and set(variant) == {'values', 'rows'}
                     and _positive_integer(variant['rows']),
                     f'{year} ambiguous variant has wrong schema or row count')
            values = variant['values']
            _require(isinstance(values, dict)
                     and set(values) == set(NON_KEY_CONSUMED),
                     f'{year} ambiguous variant lacks consumed fields')
            delay = values['ArrDelay']
            delay_valid = (delay is None or (
                isinstance(delay, (int, float)) and not isinstance(delay, bool)
                and math.isfinite(delay)))
            _require(values['Year'] == year and values['Month'] == month.get('month')
                     and values['Cancelled'] in (0, 1)
                     and values['Diverted'] in (0, 1)
                     and values['Flights'] == 1 and delay_valid
                     and isinstance(values['Reporting_Airline'], str)
                     and values['Reporting_Airline']
                     and isinstance(values['Origin'], str) and values['Origin']
                     and isinstance(values['Dest'], str) and values['Dest'],
                     f'{year} ambiguous variant has invalid consumed values')
            variant_order.append(canonical_parameters(values))
            variant_rows += variant['rows']
        _require(variant_order == sorted(variant_order)
                 and len(variant_order) == len(set(variant_order)),
                 f'{year} ambiguous variants are duplicate or nondeterministic')
        _require(variant_rows == group['rows'],
                 f'{year} ambiguous group row total does not reconcile')
        total_rows += group['rows']
        if (key['OriginAirportID'] in selected_airports
                and key['DestAirportID'] in selected_airports
                and key['OriginAirportID'] != key['DestAirportID']):
            scoped_group_count += 1
            scoped_row_count += group['rows']

    _require(key_order == sorted(key_order) and len(key_order) == len(set(key_order)),
             f'{year} ambiguous groups are duplicate or nondeterministic')
    _require(total_rows == month['ambiguous_key_rows_excluded_national'],
             f'{year} ambiguous national row total does not reconcile')
    _require(scoped_group_count == selected_groups and scoped_row_count == selected_rows,
             f'{year} ambiguous scoped counts do not reconcile to selected airport IDs')


def reconcile_operations(quality, national, scoped, year):
    operations = quality.get('operations')
    _require(isinstance(operations, list) and operations,
             f'{year} quality audit lacks operations months')
    raw = repeats = ambiguous = selected = 0
    exceptions = []
    for month in operations:
        month_raw = month.get('raw_rows')
        month_repeats = month.get('repeated_key_rows_removed_national', 0)
        month_ambiguous = month.get('ambiguous_key_rows_excluded_national', 0)
        missing_flight_number = month.get('missing_flight_number_national', 0)
        missing_flight_number_selected = month.get('missing_flight_number_selected', 0)
        _require(all(isinstance(value, int) and not isinstance(value, bool) and value >= 0
                     for value in (month_raw, month_repeats, month_ambiguous,
                                   month.get('selected_rows'), missing_flight_number,
                                   missing_flight_number_selected)),
                 f'{year} operations audit has invalid row counts')
        _require(missing_flight_number_selected <= missing_flight_number,
                 f'{year} missing-flight-number scoped count exceeds national count')
        if missing_flight_number:
            _require(isinstance(month.get('missing_flight_number_policy'), str)
                     and month['missing_flight_number_policy'].strip(),
                     f'{year} missing-flight-number evidence lacks its policy')
        expected_retained = month_raw - month_repeats - month_ambiguous
        _require(expected_retained >= 0, f'{year} operations exclusions exceed raw rows')
        _require(missing_flight_number <= expected_retained,
                 f'{year} missing flight-number rows exceed retained national rows')
        _require(missing_flight_number_selected <= month['selected_rows'],
                 f'{year} missing flight-number rows exceed retained selected rows')
        if month_repeats or month_ambiguous:
            _require(month.get('retained_rows') == expected_retained,
                     f'{year} operations retained_rows does not reconcile')
        if month_repeats:
            _require(isinstance(month.get('repeated_key_groups_national'), int)
                     and month['repeated_key_groups_national'] > 0
                     and isinstance(month.get('repeated_key_groups_selected'), int)
                     and 0 <= month['repeated_key_groups_selected']
                     <= month['repeated_key_groups_national']
                     and isinstance(month.get('repeat_resolution_policy'), str),
                     f'{year} equivalent-repeat evidence is incomplete')
        if month_ambiguous:
            _validate_ambiguity_details(month, year)
        raw += month_raw
        repeats += month_repeats
        ambiguous += month_ambiguous
        selected += month['selected_rows']
        if (month.get('missing_scheduled_departure_national', 0)
                or missing_flight_number or month_repeats or month_ambiguous):
            exceptions.append({key: month[key] for key in EXCEPTION_FIELDS if key in month})
    def whole_flight_sum(frame, label):
        _require('flights' in frame, f'{year} {label} lacks flights')
        values = pd.to_numeric(frame['flights'], errors='coerce')
        _require(not values.isna().any() and values.ge(0).all()
                 and (values % 1).eq(0).all(),
                 f'{year} {label} flights are not nonnegative whole counts')
        return int(values.sum())

    retained = whole_flight_sum(national, 'national operations')
    scoped_flights = whole_flight_sum(scoped, 'scoped operations')
    _require(retained == raw - repeats - ambiguous,
             f'{year} national operations totals do not reconcile')
    _require(scoped_flights == selected,
             f'{year} scoped operations totals do not reconcile')
    return ({
        'operations_raw_rows': raw,
        'operations_retained_flights': retained,
        'repeated_rows_removed': repeats,
        'ambiguous_rows_excluded': ambiguous,
        'scoped_flights': scoped_flights,
    }, exceptions)


def verify_fr24_zero(manifest_root, summary_path, annual_inputs, summary_years, *,
                     evidence_root=None):
    """Corroborate zero FR24 use in access summary and every acquisition ledger."""
    manifest_root, summary_path = Path(manifest_root), Path(summary_path)
    summary = _json(summary_path)
    summary_years = list(summary_years)
    expected_summary_requests = sum(
        len(annual_inputs[year]) for year in summary_years)
    _require(summary.get('years') == summary_years
             and summary.get('request_count') == expected_summary_requests
             and summary.get('success_count') == expected_summary_requests,
             'Full-history access summary does not cover its declared sources')
    _require(summary.get('fr24_calls') == 0 and summary.get('fr24_credits') == 0,
             'Full-history access summary does not corroborate zero FR24 use')
    evidence_root = Path(evidence_root or manifest_root.parent).resolve()

    def evidence_name(path):
        try:
            return Path(path).resolve().relative_to(evidence_root).as_posix()
        except ValueError as exc:
            raise CertificationError(f'FR24 evidence is outside its root: {path}') from exc

    evidence = {evidence_name(summary_path): lf_digest(summary_path)}

    for year, expected in sorted(annual_inputs.items()):
        ledgers = sorted(manifest_root.glob(f'stage6_{year}_acquisition_*.json'))
        _require(ledgers, f'Missing {year} acquisition ledger for FR24 corroboration')
        observed = {}
        for ledger_path in ledgers:
            ledger = _json(ledger_path)
            _require(ledger.get('fr24_calls') == 0 and ledger.get('fr24_credits') == 0,
                     f'{year} acquisition ledger does not record zero FR24 use')
            evidence[evidence_name(ledger_path)] = lf_digest(ledger_path)
            for result in ledger.get('results', []):
                observed.setdefault(result.get('local_path'), set()).add(result.get('sha256'))
        for path, checksum in expected.items():
            _require(checksum in observed.get(path, set()),
                     f'{year} acquisition ledgers do not corroborate {path}')
    return evidence


def _baseline_hashes(repo_root, proof_2010):
    paths = {'data/manifests/stage6_frozen_sample_2010.json',
             'outputs/stage6/annual_2010/verification.json'}
    paths.update(f'outputs/stage6/annual_2010/{name}'
                 for name in proof_2010['output_sha256'])
    hashes = {}
    for relative in sorted(paths):
        path = Path(repo_root) / relative
        _require(path.is_file(), f'Missing frozen baseline artifact: {relative}')
        hashes[relative] = digest(path)
    return hashes


def _verify_requirements(repo_root):
    lines = (Path(repo_root) / 'requirements.txt').read_text(encoding='utf-8').splitlines()
    pins = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        _require(line.count('==') == 1, f'Unpinned requirement: {line}')
        name, expected = line.split('==')
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError as exc:
            raise CertificationError(f'Missing pinned requirement: {name}') from exc
        _require(actual == expected,
                 f'Requirement pin mismatch for {name}: {actual} != {expected}')
        pins[name] = expected
    _require(pins, 'requirements.txt contains no exact pins')
    return pins


def _previous_outputs(repo_root, reference):
    _require(git_commit_exists(repo_root, reference),
             f'Previous-output reference does not exist: {reference}')
    listing = _git(repo_root, 'ls-tree', '-r', reference, '--', 'outputs', text=True)
    expected = {}
    for line in listing.splitlines():
        metadata_value, path = line.split('\t', 1)
        expected[path] = metadata_value.split()[2]
    _require(expected, f'No prior outputs found at {reference}')
    for path, oid in expected.items():
        current = Path(repo_root) / path
        _require(current.is_file(), f'Previous output is missing: {path}')
        actual = _git(repo_root, 'hash-object', f'--path={path}', str(current),
                      text=True).strip()
        _require(actual == oid, f'Previous output changed: {path}')
    return expected


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n',
                    encoding='utf-8', newline='\n')


def certify_history(tests_passed, *, repo_root=Path('.'), years=DEFAULT_YEARS,
                    previous_output_reference=DEFAULT_PREVIOUS_OUTPUT_REFERENCE):
    """Run the complete local certification and publish its compact proof files."""
    _require(isinstance(tests_passed, int) and not isinstance(tests_passed, bool)
             and tests_passed > 0, '--tests-passed must be a positive integer')
    repo_root = Path(repo_root).resolve()
    years = tuple(years)
    _require(years == DEFAULT_YEARS,
             f'Final certification requires declared years {list(DEFAULT_YEARS)}')
    _require(platform.python_version() == EXPECTED_PYTHON,
             f'Python must be exactly {EXPECTED_PYTHON}')
    requirement_pins = _verify_requirements(repo_root)
    previous_outputs = _previous_outputs(repo_root, previous_output_reference)
    head = _git(repo_root, 'rev-parse', 'HEAD', text=True).strip()
    _require(git_commit_exists(repo_root, head), f'Current HEAD is not a commit: {head}')
    sources = [*sorted((repo_root / 'src/stage6').glob('*.py')),
               repo_root / 'src/acquisition/download.py', repo_root / 'src/config.py',
               repo_root / 'requirements.txt', Path(__file__).resolve()]
    source_hashes = current_source_hashes(sources, repo_root, head)

    all_records = []
    records_by_year = {}
    expected_quarter_count = expected_month_count = 0
    for year in years:
        periods = periods_for_year(year)
        records = input_records(year)
        records_by_year[year] = records
        all_records.extend(records)
        expected_quarter_count += len(periods.quarters)
        expected_month_count += len(periods.months)
        operation_periods = sorted(record['month'] for record in records
                                   if record['kind'] == 'operations')
        fare_periods = Counter(record['quarter'] for record in records
                               if record['kind'] == 'fare')
        _require(operation_periods == list(periods.months),
                 f'{year} operations records do not match declared months')
        _require(fare_periods == Counter({quarter: 2 for quarter in periods.quarters}),
                 f'{year} fare records do not contain Market and Ticket per quarter')
    inventory = inventory_records(all_records)
    _require(inventory['market_archive_count'] == expected_quarter_count
             and inventory['ticket_archive_count'] == expected_quarter_count
             and inventory['operations_archive_count'] == expected_month_count,
             'Derived source-type counts do not match declared periods')

    proof_2010 = _json(repo_root / 'outputs/stage6/annual_2010/verification.json')
    baseline_hashes = _baseline_hashes(repo_root, proof_2010)
    annual_inputs = {}
    year_rows = []
    identity_rows = []
    exceptions = []
    for year in years:
        periods = periods_for_year(year)
        directory = repo_root / f'outputs/stage6/annual_{year}'
        proof = _json(directory / 'verification.json')
        quality = _json(directory / 'quality_audit.json')
        expected_outputs = COMMON_FILES if year == 2010 else COMMON_FILES | CONTINUITY_FILES
        records = records_by_year[year]
        expected_inputs = {Path(record['target']).as_posix() for record in records}
        validate_annual_metadata(
            proof, quality, year, periods.quarters, periods.months,
            expected_outputs, expected_inputs, require_baseline=year > 2010,
            expected_baseline_paths=set(baseline_hashes),
            baseline_hashes=baseline_hashes)
        verify_recorded_sources(proof, year, repo_root)
        for name, checksum in proof['output_sha256'].items():
            _require(digest(directory / name) == checksum,
                     f'{year} output hash mismatch: {name}')

        annual_inputs[year] = {}
        input_rows = []
        for record in records:
            target = repo_root / record['target']
            manifest = repo_root / record['manifest']
            verify_manifest(target, manifest, record['url'], record['params'], repo_root)
            with zipfile.ZipFile(target) as archive:
                _require(archive.testzip() is None, f'ZIP CRC failed: {record["target"]}')
            checksum = digest(target)
            relative_target = Path(record['target']).as_posix()
            _require(checksum == proof['input_sha256'][relative_target],
                     f'{year} raw input hash mismatch: {relative_target}')
            annual_inputs[year][relative_target] = checksum
            input_rows.append({
                'year': year, 'kind': record['kind'],
                'parameters': record['params'], 'url': record['url'],
                'local_path': relative_target,
                'manifest_path': Path(record['manifest']).as_posix(),
                'manifest_sha256_lf_normalized': lf_digest(manifest),
                'bytes': target.stat().st_size, 'sha256': checksum,
                'zip_crc_reverified': True,
            })
        identity_rows.extend(input_rows)

        national = pd.read_csv(directory / 'operations_national_month.csv')
        scoped = pd.read_csv(directory / 'operations_carrier_month.csv')
        operation_totals, year_exceptions = reconcile_operations(
            quality, national, scoped, year)
        exceptions.extend(year_exceptions)
        year_rows.append({
            'year': year, 'quarters': len(periods.quarters),
            'months': len(periods.months),
            'market_rows_scanned': sum(item['market_rows_scanned']
                                       for item in quality['fares']),
            'ticket_rows_scanned': sum(item['ticket_rows_scanned']
                                       for item in quality['fares']),
            **operation_totals,
            'verification_sha256': digest(directory / 'verification.json'),
        })
        print(f'FINAL RAW/CRC/ARTIFACT VERIFICATION {year}', flush=True)

    summary_years = list(years[2:])
    fr24_evidence = verify_fr24_zero(
        repo_root / 'data/manifests',
        repo_root / 'data/manifests/stage6_full_history_access_summary.json',
        annual_inputs, summary_years, evidence_root=repo_root)

    history_output = repo_root / 'outputs/stage6/history'
    builds = []
    for _ in range(2):
        audit = build_history(history_root=repo_root / 'outputs/stage6',
                              output=history_output, expected_years=years)
        hashes = {path.name: digest(path) for path in sorted(history_output.iterdir())
                  if path.is_file() and path.name != 'verification.json'}
        _require(len(hashes) == 4, 'History build must produce four summary artifacts')
        builds.append(hashes)
    _require(builds[0] == builds[1], 'History summary builds are not byte-identical')
    _require(audit.get('full_horizon_complete') is True
             and audit.get('verified_years') == list(years)
             and audit.get('quarter_count') == expected_quarter_count,
             'History audit does not certify the declared horizon')
    _require(audit['horizon_totals']['national_flights']
             == sum(row['operations_retained_flights'] for row in year_rows),
             'History national flights do not reconcile to annual proofs')
    _require(audit['horizon_totals']['scoped_flights']
             == sum(row['scoped_flights'] for row in year_rows),
             'History scoped flights do not reconcile to annual proofs')

    coverage = {
        'declared_horizon': audit['declared_horizon'],
        'verified_at_utc': datetime.now(timezone.utc).isoformat(),
        **inventory,
        'fare_quarter_count': expected_quarter_count,
        'operations_month_count': expected_month_count,
        'total_compressed_bytes': sum(item['bytes'] for item in identity_rows),
        'all_request_identities_sha256_and_zip_crc_reverified': True,
        'year_totals': year_rows,
        'operations_source_exceptions': exceptions,
        'inputs': identity_rows,
        'fr24_calls': 0, 'fr24_credits': 0,
        'fr24_evidence_sha256_lf_normalized': fr24_evidence,
    }
    coverage_path = repo_root / 'data/manifests/stage6_full_history_consumed_inputs.json'
    _write_json(coverage_path, coverage)

    final_proof = {
        'declared_horizon': audit['declared_horizon'],
        'full_horizon_complete': True, 'verified_years': list(years),
        'partial_year': 2025, 'quarter_count': expected_quarter_count,
        'operations_month_count': expected_month_count,
        'annual_raw_builds_per_year': 2, 'successful_summary_builds': 2,
        'byte_identical': True, 'output_sha256': builds[-1],
        'annual_verification_sha256': audit['verification_sha256'],
        'consumed_input_manifest_sha256': digest(coverage_path),
        'previous_output_reference': previous_output_reference,
        'previous_output_files_unchanged': len(previous_outputs),
        'previous_output_git_oids': previous_outputs,
        'implementation_commit': head,
        'source_sha256_lf_normalized': source_hashes,
        'python': platform.python_version(),
        'requirements_pins_verified': True,
        'requirements_pins': requirement_pins,
        'offline_tests_passed': tests_passed,
        'offline_test_command': 'python -m pytest -q',
        'fr24_calls': 0, 'fr24_credits': 0,
        'fr24_evidence_sha256_lf_normalized': fr24_evidence,
    }
    _write_json(history_output / 'verification.json', final_proof)
    print(
        'FULL HORIZON VERIFIED: '
        f'{inventory["source_identity_count"]} unique sources, {len(years)} years, '
        f'{expected_quarter_count} quarters, {expected_month_count} months; '
        f'four identical summary outputs; {len(previous_outputs)} earlier outputs unchanged',
        flush=True)
    return coverage, final_proof


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-passed', required=True, type=int)
    parser.add_argument('--repo-root', type=Path, default=Path('.'))
    parser.add_argument('--previous-output-reference',
                        default=DEFAULT_PREVIOUS_OUTPUT_REFERENCE)
    args = parser.parse_args(argv)
    certify_history(args.tests_passed, repo_root=args.repo_root,
                    previous_output_reference=args.previous_output_reference)


if __name__ == '__main__':
    main()
