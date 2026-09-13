from pathlib import Path
import json
import zipfile

import pandas as pd
import pytest

from src.stage6 import annual
from src.acquisition.download import digest


def test_2011_requests_are_complete_without_2010_data_paths():
    records=annual.input_records(2011)
    assert len(records)==20 and len({r['url'] for r in records})==20
    assert all(r['year']==2011 and '_2011_' in r['url'] for r in records)
    assert {r['month'] for r in records if r['kind']=='operations'}==set(range(1,13))
    assert {(r['table'],r['quarter']) for r in records if r['kind']=='fare'}=={
        (t,q) for t in ('Market','Ticket') for q in range(1,5)}


@pytest.mark.parametrize('year',[2009,2012,2025,True,2011.0])
def test_undeclared_annual_years_reject_before_acquisition(year):
    with pytest.raises(ValueError,match='year'):
        annual.input_records(year)


def test_source_completeness_uses_requested_year():
    annual.validate_months([{'year':2011,'month':m} for m in range(1,13)],year=2011)
    with pytest.raises(ValueError,match='twelve'):
        annual.validate_months([{'year':2010,'month':m} for m in range(1,13)],year=2011)


def test_2011_refuses_output_overlapping_frozen_baseline():
    with pytest.raises(ValueError,match='overlap'):
        annual.main(['--year','2011','--output','outputs/stage6/annual_2010'])


def test_2011_processing_uses_frozen_airport_ids_without_reranking(tmp_path,monkeypatch):
    from src.stage6 import baseline, annual_fares
    ranking=pd.DataFrame({'AirportID':[101,202,303],'selected':[True,False,True]})
    monkeypatch.setattr(baseline,'load_baseline',lambda:(ranking,{'year':2010},{}))
    monkeypatch.setattr(annual,'input_records',lambda year:[])
    def forbidden(*args,**kwargs):
        raise AssertionError('Later year attempted airport reselection')
    monkeypatch.setattr(annual_fares,'select_airports',forbidden)
    def capture(*args,**kwargs):
        assert kwargs['year']==2011
        assert kwargs['airport_ids']==[101,303]
        raise RuntimeError('reached frozen-scope fare processing')
    monkeypatch.setattr(annual_fares,'process_fares',capture)
    with pytest.raises(RuntimeError,match='frozen-scope'):
        annual.main(['--year','2011','--output',str(tmp_path/'output')])


def test_annual_requests_cover_exactly_twelve_months_and_four_fare_pairs():
    records = annual.input_records()
    assert len(records) == 20
    assert len({str(r['target']) for r in records}) == 20
    assert {r['month'] for r in records if r['kind'] == 'operations'} == set(range(1, 13))
    assert {(r['table'], r['quarter']) for r in records if r['kind'] == 'fare'} == {
        (t, q) for t in ('Market', 'Ticket') for q in range(1, 5)}
    assert all(r['year'] == 2010 for r in records)
    january = next(r for r in records if r.get('month') == 1)
    assert january['manifest'].name == 'bts_ontime_2010_01.json'
    assert january['url'].endswith('1987_present_2010_1.zip')


def test_missing_input_stops_before_replacing_annual_outputs(tmp_path, monkeypatch):
    output = tmp_path / 'output'
    output.mkdir()
    original = b'previous verified panel\n'
    (output / 'route_quarter_panel.csv').write_bytes(original)
    monkeypatch.setattr(annual, 'input_records', lambda: [{
        'target': tmp_path / 'missing.zip', 'manifest': tmp_path / 'missing.json',
        'url': 'https://example.test/a.zip', 'params': {'year': 2010},
    }])
    with pytest.raises(FileNotFoundError):
        annual.main(['--output', str(output)])
    assert (output / 'route_quarter_panel.csv').read_bytes() == original


def test_source_month_completeness_rejects_missing_and_repeated_months():
    for months in [list(range(1, 12)), list(range(1, 12)) + [11]]:
        with pytest.raises(ValueError, match='twelve'):
            annual.validate_months([{'year': 2010, 'month': m} for m in months])


def test_annual_access_checks_reject_missing_inventory_identity():
    with pytest.raises(ValueError, match='access'):
        annual.advertised_bytes([{'url': 'https://example.test/missing.zip'}], [])


def test_annual_access_checks_sum_only_requested_successful_identities():
    inventory = {'requests': [{'url': 'a'}, {'url': 'b'}], 'results': [
        {'request_index': 0, 'success': True, 'headers': {'content_length': 50}},
        {'request_index': 1, 'success': False, 'headers': {'content_length': 99}}]}
    assert annual.advertised_bytes([{'url': 'a'}], [inventory]) == 50
    with pytest.raises(ValueError, match='access'):
        annual.advertised_bytes([{'url': 'b'}], [inventory])


def test_acquisition_rejects_orphan_raw_before_claiming_provenance(tmp_path, monkeypatch):
    target, manifest = tmp_path/'orphan.zip', tmp_path/'manifest.json'
    with zipfile.ZipFile(target, 'w') as archive:
        archive.writestr('unrelated.csv', 'Year\n1999\n')
    original = target.read_bytes()
    monkeypatch.setattr(annual, 'MANIFESTS', tmp_path)
    inventory = {'requests': [{'url': 'https://example.test/2010.zip'}],
        'results': [{'request_index': 0, 'success': True,
                     'headers': {'content_length': 1000}}]}
    for name in ['stage6_access_inventory.json', 'stage6_operations_access_correction.json',
                 'stage6_2010_access_inventory.json']:
        (tmp_path/name).write_text(json.dumps(inventory), encoding='utf-8')
    with pytest.raises(ValueError, match='manifest'):
        annual.acquire_inputs([{'target': target, 'manifest': manifest,
            'url': 'https://example.test/2010.zip', 'source': 'BTS fixture',
            'params': {'year': 2010}}])
    assert target.read_bytes() == original
    assert not manifest.exists()


def test_publish_failure_restores_every_previous_output(tmp_path, monkeypatch):
    output, staging = tmp_path/'output', tmp_path/'staging'
    output.mkdir()
    staging.mkdir()
    (output/'panel.csv').write_bytes(b'old panel')
    (output/'verification.json').write_bytes(b'old verification')
    (staging/'panel.csv').write_bytes(b'new panel')
    original_rename = Path.rename

    def fail_new_publish(self, target):
        if self == staging:
            raise PermissionError('injected publication failure')
        return original_rename(self, target)

    monkeypatch.setattr(Path, 'rename', fail_new_publish)
    with pytest.raises(PermissionError, match='injected'):
        annual.publish_directory(staging, output)
    assert {p.name: p.read_bytes() for p in output.iterdir()} == {
        'panel.csv': b'old panel', 'verification.json': b'old verification'}


def test_publish_replaces_exact_set_and_retains_previous_directory(tmp_path):
    output, staging = tmp_path/'output', tmp_path/'staging'
    output.mkdir()
    staging.mkdir()
    (output/'stale.json').write_bytes(b'previous evidence')
    (staging/'panel.csv').write_bytes(b'new panel')
    backup = annual.publish_directory(staging, output)
    assert {p.name for p in output.iterdir()} == {'panel.csv'}
    assert (backup/'stale.json').read_bytes() == b'previous evidence'


def test_full_annual_runner_joins_twenty_real_fixture_archives(tmp_path, monkeypatch):
    codes = ['ORD', 'DEN', 'DFW', 'ATL', 'LAX', 'JFK', 'SEA']
    records = annual.input_records()
    for record in records:
        record['target'] = tmp_path / record['target'].name
        record['manifest'] = tmp_path / record['manifest'].name
        rows = []
        for i, origin in enumerate(codes):
            dest_index = (i + 1) % 7
            common = {'Year': 2010, 'Origin': origin, 'Dest': codes[dest_index],
                      'OriginAirportID': 100+i, 'DestAirportID': 100+dest_index}
            if record['kind'] == 'operations':
                month = record['month']
                rows.append({**common, 'Month': month, 'FlightDate': f'2010-{month:02d}-01',
                    'Reporting_Airline': 'OP', 'DOT_ID_Reporting_Airline': 99,
                    'Flight_Number_Reporting_Airline': i+1, 'CRSDepTime': 800,
                    'Cancelled': 0, 'Diverted': 0, 'ArrDelay': 20, 'Flights': 1})
            elif record['table'] == 'Market':
                rows.append({**common, 'Quarter': record['quarter'], 'ItinID': i+1,
                    'MktID': i+1, 'OriginCountry': 'US', 'DestCountry': 'US',
                    'RPCarrier': 'FA', 'MktCoupons': 1, 'BulkFare': 0,
                    'Passengers': 10, 'MktFare': 100})
            else:
                rows.append({'Year': 2010, 'Quarter': record['quarter'],
                             'ItinID': i+1, 'DollarCred': 1})
        with zipfile.ZipFile(record['target'], 'w') as archive:
            archive.writestr('fixture.csv', pd.DataFrame(rows).to_csv(index=False))
        record['manifest'].write_text(json.dumps({'local_path': str(record['target']),
            'url': record['url'], 'query_parameters': record['params'],
            'sha256': digest(record['target'])}), encoding='utf-8')
    monkeypatch.setattr(annual, 'input_records', lambda: records)
    monkeypatch.setattr(annual, 'bts_path', lambda table, year, quarter: next(
        r['target'] for r in records if r.get('table') == table and r.get('quarter') == quarter))
    output = tmp_path / 'results'
    annual.main(['--output', str(output)])
    panel = pd.read_csv(output / 'route_quarter_panel.csv')
    assert len(panel) == 56  # seven routes, four quarters, two fare bounds
    assert panel.coverage.eq('matched').all()
    assert panel.passengers.eq(10).all()
    assert panel.fare_mean.eq(100).all()
    assert panel.flights.eq(3).all()
    assert panel.months_observed.eq(3).all()
    assert panel.delay_15_rate.eq(1).all()
    assert panel.delay_60_rate.eq(0).all()
    audit = json.loads((output / 'quality_audit.json').read_text())
    assert audit['verified_input_count'] == 20
    assert audit['source_months_complete'] is True
    assert len(audit['operations']) == 12
    assert len(audit['fares']) == 4
