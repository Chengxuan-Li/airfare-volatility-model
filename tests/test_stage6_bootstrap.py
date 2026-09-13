import json
import zipfile

import pandas as pd
import pytest


def ticket_archive(tmp_path, quarter=1):
    rows = pd.DataFrame({'Year': [2010, 2010], 'Quarter': [quarter, quarter],
        'ItinID': [1, 2], 'DollarCred': [1, 1], 'RoundTrip': [0, 1],
        'ItinFare': [100., 200.], 'Coupons': [1, 2], 'OriginAirportID': [13930, 12892]})
    path = tmp_path/'ticket.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('readme.html', 'fixture documentation')
        archive.writestr('ticket.csv', rows.to_csv(index=False))
    return path


def test_historical_fare_schema_audit_streams_the_entire_period(tmp_path):
    from src.stage6.bootstrap import inspect_fare
    result = inspect_fare(ticket_archive(tmp_path), 'Ticket', 2010, 1, chunksize=1)
    assert result['rows'] == 2
    assert result['required_columns_present'] is True
    assert result['csv_member'] == 'ticket.csv'
    assert result['missing_itinerary_ids'] == 0


def test_historical_fare_schema_rejects_wrong_quarter(tmp_path):
    from src.stage6.bootstrap import inspect_fare
    with pytest.raises(ValueError, match='period'):
        inspect_fare(ticket_archive(tmp_path, quarter=2), 'Ticket', 2010, 1, chunksize=1)


def test_bootstrap_verifies_consumed_path_against_manifest(tmp_path):
    from src.stage6.bootstrap import verify_input
    from src.acquisition.download import digest
    path = ticket_archive(tmp_path)
    manifest = tmp_path/'manifest.json'
    record = {'local_path': str(path), 'url': 'https://example.test/ticket.zip',
              'query_parameters': {'year': 2010, 'quarter': 1}, 'sha256': digest(path)}
    manifest.write_text(json.dumps(record))
    verify_input(path, manifest, record['url'], record['query_parameters'])
    record['local_path'] = str(tmp_path/'other.zip')
    manifest.write_text(json.dumps(record))
    with pytest.raises(ValueError, match='path'):
        verify_input(path, manifest, record['url'], record['query_parameters'])


def test_legacy_fare_manifest_verifies_without_rewriting_provenance(tmp_path):
    from src.stage6.bootstrap import verify_input
    from src.acquisition.download import digest
    path = ticket_archive(tmp_path)
    manifest = tmp_path/'legacy.json'
    record = {'local_path': str(path), 'url': 'https://example.test/ticket.zip',
              'year': 2010, 'quarter': 1, 'sha256': digest(path),
              'retrieved_at_utc': '2026-09-12T09:54:03Z'}
    manifest.write_text(json.dumps(record))
    original = manifest.read_bytes()
    verify_input(path, manifest, record['url'], {'year': 2010, 'quarter': 1})
    assert manifest.read_bytes() == original
    for params in ({'year': 2010, 'quarter': 2}, {'year': 2010, 'month': 1}):
        with pytest.raises(ValueError, match='identity'):
            verify_input(path, manifest, record['url'], params)


def test_missing_legacy_period_identity_is_rejected(tmp_path):
    from src.stage6.bootstrap import verify_input
    from src.acquisition.download import digest
    path = ticket_archive(tmp_path)
    manifest = tmp_path/'incomplete.json'
    record = {'local_path': str(path), 'url': 'https://example.test/ticket.zip',
              'year': 2010, 'sha256': digest(path)}
    manifest.write_text(json.dumps(record))
    with pytest.raises(ValueError, match='identity'):
        verify_input(path, manifest, record['url'], {'year': 2010, 'quarter': 1})
