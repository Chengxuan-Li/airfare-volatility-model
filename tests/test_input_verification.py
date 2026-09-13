import hashlib
import json
from pathlib import Path

import pytest


@pytest.fixture
def pilot_inputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifests = Path('data/manifests')
    manifests.mkdir(parents=True)
    inputs = [('ourairports.json', 'data/raw/ourairports.csv'),
              ('bts_delay_causes.json', 'data/raw/bts_delay_causes_2022_2024.zip')]
    for year in (2023, 2024):
        for quarter in (1, 2, 3, 4):
            for table in ('Market', 'Ticket'):
                inputs.append((f'bts_db1b_{table.lower()}_{year}_q{quarter}.json',
                               f'data/raw/bts_db1b/Origin_and_Destination_Survey_DB1B{table}_{year}_{quarter}.zip'))
    for airport in ('ORD', 'DEN', 'DFW', 'ATL', 'LAX', 'JFK', 'SEA'):
        inputs.append((f'weather_{airport}.json', f'data/raw/weather/{airport}_2020_2024.json'))
    for name, raw in inputs:
        target = Path(raw)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'fixture bytes for checksum verification')
        (manifests/name).write_text(json.dumps({
            'local_path': raw, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}))
    return manifests


def test_original_input_verification_ignores_missing_extension_inputs(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    (pilot_inputs/'t100_2025.json').write_text(json.dumps({
        'local_path': 'data/raw/t100/not-downloaded.zip', 'sha256': 'unused'}))
    assert verify_pilot_inputs() == 25


def test_original_runner_reaches_analysis_with_only_its_own_inputs(pilot_inputs, monkeypatch, capsys):
    import sys
    import src.run as run
    # Only downstream computations are replaced; input verification is real.
    (pilot_inputs/'t100_2025.json').write_text(json.dumps({
        'local_path': 'data/raw/t100/not-downloaded.zip', 'sha256': 'unused'}))
    Path('outputs/tables').mkdir(parents=True)
    Path('outputs/tables/fare_cells.csv').write_text('sample,fare_mean\nprimary,100\n')
    monkeypatch.setattr(sys, 'argv', ['src.run', '--analysis-only'])
    monkeypatch.setattr(run, 'build_weather_panel', lambda: None)
    monkeypatch.setattr(run, 'attach_weather', lambda cells, weather: cells)
    monkeypatch.setattr(run, 'analyze', lambda panel, weather: {'rows': len(panel)})
    run.main()
    assert json.loads(capsys.readouterr().out)['rows'] == 1


def test_required_manifest_cannot_be_silently_omitted(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    (pilot_inputs/'weather_ORD.json').unlink()
    with pytest.raises(FileNotFoundError, match='weather_ORD'):
        verify_pilot_inputs()


def test_required_raw_input_must_exist(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    Path('data/raw/weather/ORD_2020_2024.json').unlink()
    with pytest.raises(FileNotFoundError, match='ORD_2020_2024'):
        verify_pilot_inputs()


def test_changed_raw_content_is_rejected(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    Path('data/raw/weather/ORD_2020_2024.json').write_bytes(b'changed')
    with pytest.raises(ValueError, match='checksum'):
        verify_pilot_inputs()


def test_manifest_cannot_redirect_verification_to_identical_other_file(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    manifest = pilot_inputs/'weather_ORD.json'
    record = json.loads(manifest.read_text())
    record['local_path'] = 'data/raw/weather/DEN_2020_2024.json'
    manifest.write_text(json.dumps(record))
    with pytest.raises(ValueError, match='path'):
        verify_pilot_inputs()


def test_required_checksum_cannot_be_silently_skipped(pilot_inputs):
    from src.acquisition.verify import verify_pilot_inputs
    manifest = pilot_inputs/'weather_ORD.json'
    record = json.loads(manifest.read_text())
    del record['sha256']
    manifest.write_text(json.dumps(record))
    with pytest.raises(ValueError, match='sha256'):
        verify_pilot_inputs()
