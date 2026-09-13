import hashlib
import json
from pathlib import Path
from copy import deepcopy

import pandas as pd
import pytest


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _proof(year, quarters, months):
    output_count = 11 if year > 2010 else 8
    output_names = ['quality_audit.json'] + [
        f'output-{index}.csv' for index in range(output_count - 1)]
    proof = {
        'scope': 'descriptive annual panel',
        'successful_full_raw_builds': 2,
        'compared_output_files': output_count,
        'byte_identical': True,
        'output_sha256': {name: 'a' * 64 for name in output_names},
        'input_sha256': {f'raw-{index}': 'b' * 64
                         for index in range(len(quarters) * 2 + len(months))},
        'source_sha256_lf_normalized': {'src/example.py': _sha(b'x\n')},
        'implementation_commit': '1' * 40,
        'python': '3.13.9',
        'requirements_pins_verified': True,
        'offline_tests_passed': 5,
        'fr24_calls': 0,
        'fr24_credits': 0,
    }
    if year >= 2012:
        proof.update({
            'year': year,
            'expected_quarters': list(quarters),
            'expected_months': list(months),
            'partial_year': year == 2025,
            'offline_test_scope': 'full offline test suite',
            'offline_test_command': 'python -m pytest -q',
        })
    return proof


def _quality(year, quarters, months):
    return {
        'year': year,
        'fares': [{'year': year, 'quarter': quarter} for quarter in quarters],
        'operations': [{'year': year, 'month': month, 'raw_rows': 1,
                        'selected_rows': 1} for month in months],
        'verified_input_count': len(quarters) * 2 + len(months),
        'source_months_complete': True,
    }


@pytest.mark.parametrize('year', [2010, 2011])
def test_legacy_annual_metadata_accepts_absent_modern_period_fields(year):
    from scripts.verify_stage6_history import validate_annual_metadata
    quarters, months = (1, 2, 3, 4), tuple(range(1, 13))
    proof = _proof(year, quarters, months)
    if year > 2010:
        proof['baseline_artifact_sha256'] = {'baseline': 'c' * 64}
    validate_annual_metadata(
        proof, _quality(year, quarters, months), year, quarters, months,
        set(proof['output_sha256']), set(proof['input_sha256']),
        require_baseline=year > 2010,
        expected_baseline_paths=set() if year == 2010 else {'baseline'},
        baseline_hashes={} if year == 2010 else {'baseline': 'c' * 64})


def test_modern_annual_metadata_requires_exact_year_period_partial_and_test_evidence():
    from scripts.verify_stage6_history import CertificationError, validate_annual_metadata
    quarters, months = (1, 2), tuple(range(1, 7))
    proof = _proof(2025, quarters, months)
    proof['baseline_artifact_sha256'] = {'baseline': 'c' * 64}
    kwargs = dict(
        quality=_quality(2025, quarters, months), year=2025,
        quarters=quarters, months=months,
        expected_output_names=set(proof['output_sha256']),
        expected_input_paths=set(proof['input_sha256']), require_baseline=True,
        expected_baseline_paths={'baseline'}, baseline_hashes={'baseline': 'c' * 64})
    validate_annual_metadata(proof, **kwargs)

    for field, bad_value in [
            ('year', 2024), ('expected_quarters', [1, 2, 3]),
            ('expected_months', [1]), ('partial_year', False),
            ('offline_tests_passed', 0), ('requirements_pins_verified', False)]:
        invalid = dict(proof)
        invalid[field] = bad_value
        with pytest.raises(CertificationError):
            validate_annual_metadata(invalid, **kwargs)


def test_recorded_source_proof_uses_commit_blob_and_lf_normalization(tmp_path):
    from scripts.verify_stage6_history import (
        CertificationError, required_annual_sources, verify_recorded_sources)
    paths = required_annual_sources(2012)
    proof = {
        'implementation_commit': '1' * 40,
        'source_sha256_lf_normalized': {path: _sha(b'a\nb\n') for path in paths},
    }
    blobs = {('1' * 40, path): b'a\r\nb\r\n' for path in paths}
    verify_recorded_sources(
        proof, 2012, tmp_path,
        commit_exists=lambda root, commit: True,
        read_blob=lambda root, commit, path: blobs[(commit, path)])

    changed_path = sorted(paths)[0]
    blobs[('1' * 40, changed_path)] = b'changed\n'
    with pytest.raises(CertificationError, match='historical source hash mismatch'):
        verify_recorded_sources(
            proof, 2012, tmp_path,
            commit_exists=lambda root, commit: True,
            read_blob=lambda root, commit, path: blobs[(commit, path)])

    incomplete = deepcopy(proof)
    incomplete['source_sha256_lf_normalized'].pop(changed_path)
    with pytest.raises(CertificationError, match='required source hashes'):
        verify_recorded_sources(
            incomplete, 2012, tmp_path,
            commit_exists=lambda root, commit: True,
            read_blob=lambda root, commit, path: blobs[(commit, path)])


def test_current_source_hashes_require_worktree_to_match_head(tmp_path):
    from scripts.verify_stage6_history import CertificationError, current_source_hashes
    source = tmp_path/'src'/'example.py'
    source.parent.mkdir()
    source.write_bytes(b'a\r\nb\r\n')
    reader = lambda root, commit, path: b'a\nb\n'
    hashes = current_source_hashes(
        [source], tmp_path, '2' * 40, read_blob=reader)
    assert hashes == {'src/example.py': _sha(b'a\nb\n')}

    source.write_text('changed\n', encoding='utf-8')
    with pytest.raises(CertificationError, match='differs from HEAD'):
        current_source_hashes([source], tmp_path, '2' * 40, read_blob=reader)


def test_inventory_derives_counts_and_rejects_duplicate_identity_or_manifest():
    from scripts.verify_stage6_history import CertificationError, inventory_records
    records = [
        {'kind': 'fare', 'url': 'u-market', 'params': {'b': 2, 'a': 1},
         'target': Path('DB1BMarket.zip'), 'manifest': Path('market.json'), 'quarter': 1},
        {'kind': 'fare', 'url': 'u-ticket', 'params': {'a': 1, 'b': 2},
         'target': Path('DB1BTicket.zip'), 'manifest': Path('ticket.json'), 'quarter': 1},
        {'kind': 'operations', 'url': 'u-ops', 'params': {'month': 1},
         'target': Path('operations.zip'), 'manifest': Path('ops.json'), 'month': 1},
    ]
    counts = inventory_records(records)
    assert counts == {
        'source_identity_count': 3, 'source_manifest_count': 3,
        'fare_archive_count': 2, 'market_archive_count': 1,
        'ticket_archive_count': 1, 'operations_archive_count': 1,
    }

    with pytest.raises(CertificationError, match='request identities'):
        inventory_records(records + [dict(records[0], manifest=Path('other.json'))])
    with pytest.raises(CertificationError, match='manifest paths'):
        inventory_records(records + [dict(records[0], url='other')])


def _ambiguity_group():
    return {
        'key': {
            'FlightDate': '2018-01-01',
            'DOT_ID_Reporting_Airline': 19977,
            'Flight_Number_Reporting_Airline': 1,
            'OriginAirportID': 13930,
            'DestAirportID': 12892,
            'CRSDepTime': 1000,
        },
        'rows': 2,
        'consumed_variant_count': 2,
        'consumed_variants': [
            {'values': {
                'ArrDelay': -12.0, 'Cancelled': 0, 'Dest': 'LAX',
                'Diverted': 0, 'Flights': 1, 'Month': 1, 'Origin': 'ORD',
                'Reporting_Airline': 'UA', 'Year': 2018,
            }, 'rows': 1},
            {'values': {
                'ArrDelay': -5.0, 'Cancelled': 0, 'Dest': 'LAX',
                'Diverted': 0, 'Flights': 1, 'Month': 1, 'Origin': 'ORD',
                'Reporting_Airline': 'UA', 'Year': 2018,
            }, 'rows': 1},
        ],
    }


def _quality_with_ambiguity():
    return {
        'operations': [
            {'year': 2018, 'month': 1, 'raw_rows': 10, 'retained_rows': 7,
             'selected_rows': 5, 'selected_airport_ids': [12892, 13930],
             'repeated_key_rows_removed_national': 1,
             'repeated_key_rows_removed_selected': 1,
             'repeated_key_groups_national': 1,
             'repeated_key_groups_selected': 1,
             'repeat_resolution_policy': 'coalesce equivalent complete keys',
             'ambiguous_key_rows_excluded_national': 2,
             'ambiguous_key_rows_excluded_selected': 2,
             'ambiguous_key_groups_national': 1,
             'ambiguous_key_groups_selected': 1,
             'ambiguous_complete_key_groups': [_ambiguity_group()],
             'ambiguity_policy': 'exclude all variants'},
        ]
    }


def test_operations_reconciliation_accounts_for_repeats_and_ambiguous_quarantine():
    from scripts.verify_stage6_history import reconcile_operations
    audit = _quality_with_ambiguity()
    national = pd.DataFrame({'flights': [7]})
    scoped = pd.DataFrame({'flights': [5]})
    totals, exceptions = reconcile_operations(audit, national, scoped, 2018)
    assert totals == {
        'operations_raw_rows': 10, 'operations_retained_flights': 7,
        'repeated_rows_removed': 1, 'ambiguous_rows_excluded': 2,
        'scoped_flights': 5,
    }
    assert exceptions[0]['ambiguous_key_rows_excluded_national'] == 2
    assert exceptions[0]['ambiguous_complete_key_groups'] == [_ambiguity_group()]


@pytest.mark.parametrize('mutation', [
    'missing_key_field', 'duplicate_variant', 'zero_variant_rows',
    'bad_group_sum', 'bad_month_sum', 'bad_scoped_count',
])
def test_operations_reconciliation_rejects_malformed_ambiguity_evidence(mutation):
    from scripts.verify_stage6_history import CertificationError, reconcile_operations
    audit = deepcopy(_quality_with_ambiguity())
    month = audit['operations'][0]
    group = month['ambiguous_complete_key_groups'][0]
    if mutation == 'missing_key_field':
        group['key'].pop('CRSDepTime')
    elif mutation == 'duplicate_variant':
        group['consumed_variants'][1]['values'] = deepcopy(
            group['consumed_variants'][0]['values'])
    elif mutation == 'zero_variant_rows':
        group['consumed_variants'][0]['rows'] = 0
    elif mutation == 'bad_group_sum':
        group['rows'] = 3
    elif mutation == 'bad_month_sum':
        month['ambiguous_key_rows_excluded_national'] = 3
        month['retained_rows'] = 6
    elif mutation == 'bad_scoped_count':
        month['ambiguous_key_rows_excluded_selected'] = 0

    with pytest.raises(CertificationError):
        reconcile_operations(
            audit, pd.DataFrame({'flights': [7]}),
            pd.DataFrame({'flights': [5]}), 2018)


def test_fr24_zero_requires_summary_and_every_annual_acquisition_ledger(tmp_path):
    from scripts.verify_stage6_history import CertificationError, verify_fr24_zero
    manifests = tmp_path/'manifests'
    manifests.mkdir()
    summary = manifests/'summary.json'
    summary.write_text(json.dumps({
        'years': [2012], 'request_count': 1, 'success_count': 1,
        'fr24_calls': 0, 'fr24_credits': 0}), encoding='utf-8')
    ledger = manifests/'stage6_2012_acquisition_test.json'
    ledger.write_text(json.dumps({
        'fr24_calls': 0, 'fr24_credits': 0,
        'results': [{'local_path': 'raw.zip', 'sha256': 'd' * 64}]}),
        encoding='utf-8')
    evidence = verify_fr24_zero(
        manifests, summary, {2012: {'raw.zip': 'd' * 64}}, [2012])
    assert set(evidence) == {'manifests/summary.json',
                             'manifests/stage6_2012_acquisition_test.json'}

    ledger.write_text(json.dumps({
        'fr24_calls': 1, 'fr24_credits': 0,
        'results': [{'local_path': 'raw.zip', 'sha256': 'd' * 64}]}),
        encoding='utf-8')
    with pytest.raises(CertificationError, match='FR24'):
        verify_fr24_zero(
            manifests, summary, {2012: {'raw.zip': 'd' * 64}}, [2012])
