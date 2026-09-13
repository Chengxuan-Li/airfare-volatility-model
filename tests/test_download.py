import hashlib
import json
from pathlib import Path
import zipfile

import pytest

import src.acquisition.download as download


def fake_transfer(monkeypatch, payload):
    monkeypatch.setattr(download.shutil, 'which', lambda name: 'curl')

    def run(command, *, check, timeout):
        output = command[command.index('--output') + 1]
        Path(output).write_bytes(payload)

    monkeypatch.setattr(download.subprocess, 'run', run)


def recorded_manifest(payload, *, url='https://example.test/data.json', params=None):
    return {
        'source': 'Recorded source',
        'url': url,
        'query_parameters': params,
        'retrieved_at_utc': '2026-01-02T03:04:05+00:00',
        'local_path': 'original/location.json',
        'bytes': len(payload),
        'sha256': hashlib.sha256(payload).hexdigest(),
        'review_note': 'preserve this metadata exactly',
    }


def test_matching_reacquisition_preserves_recorded_manifest_bytes(tmp_path, monkeypatch):
    payload = b'{"daily": {"time": []}}\n'
    target = tmp_path / 'data.json'
    manifest = tmp_path / 'manifest.json'
    original = json.dumps(recorded_manifest(payload), separators=(',', ':')).encode() + b'\n'
    manifest.write_bytes(original)
    fake_transfer(monkeypatch, payload)

    assert download.fetch('https://example.test/data.json', target, manifest) == target

    assert target.read_bytes() == payload
    assert manifest.read_bytes() == original
    assert not (tmp_path / 'data.json.part').exists()


def test_changed_reacquisition_is_quarantined_before_promotion(tmp_path, monkeypatch):
    recorded = b'{"daily": {"time": ["2024-01-01"]}}\n'
    changed = b'{"daily": {"time": ["2024-01-02"]}}\n'
    target = tmp_path / 'data.json'
    partial = tmp_path / 'data.json.part'
    manifest = tmp_path / 'manifest.json'
    original = json.dumps(recorded_manifest(recorded), indent=4).encode() + b'\n'
    manifest.write_bytes(original)
    fake_transfer(monkeypatch, changed)

    with pytest.raises(ValueError, match='checksum'):
        download.fetch('https://example.test/data.json', target, manifest)

    assert not target.exists()
    assert partial.read_bytes() == changed
    assert manifest.read_bytes() == original


def test_changed_request_is_rejected_when_target_is_missing(tmp_path, monkeypatch):
    payload = b'{"daily": {"time": []}}\n'
    target = tmp_path / 'data.json'
    partial = tmp_path / 'data.json.part'
    manifest = tmp_path / 'manifest.json'
    original = json.dumps(recorded_manifest(
        payload, url='https://example.test/old.json', params={'year': 2024}
    ), indent=2).encode() + b'\n'
    manifest.write_bytes(original)
    monkeypatch.setattr(
        download.shutil, 'which', lambda name: pytest.fail('request mismatch started a transfer')
    )

    with pytest.raises(ValueError, match='request'):
        download.fetch(
            'https://example.test/new.json', target, manifest, params={'year': 2025}
        )

    assert not target.exists()
    assert not partial.exists()
    assert manifest.read_bytes() == original


def test_legacy_db1b_manifest_accepts_matching_top_level_period(tmp_path):
    target = tmp_path / 'db1b.zip'
    with zipfile.ZipFile(target, 'w') as archive:
        archive.writestr('Market.csv', 'Year,Quarter\n2024,1\n')
    url = 'https://example.test/db1b.zip'
    manifest = tmp_path / 'manifest.json'
    original = json.dumps({
        'source': 'BTS DB1B',
        'url': url,
        'year': 2024,
        'quarter': 1,
        'sha256': download.digest(target),
        'retrieved_at_utc': '2026-01-02T03:04:05+00:00',
    }, indent=4).encode() + b'\n'
    manifest.write_bytes(original)

    assert download.fetch(url, target, manifest, params={'year': 2024, 'quarter': 1}) == target
    assert manifest.read_bytes() == original


def test_legacy_db1b_manifest_allows_matching_reacquisition(tmp_path, monkeypatch):
    payload = b'{"quarter": 1}\n'
    target = tmp_path / 'db1b.json'
    manifest = tmp_path / 'manifest.json'
    url = 'https://example.test/db1b.json'
    original = json.dumps({
        'source': 'BTS DB1B',
        'url': url,
        'year': 2024,
        'quarter': 1,
        'sha256': hashlib.sha256(payload).hexdigest(),
        'retrieved_at_utc': '2026-01-02T03:04:05+00:00',
    }, separators=(',', ':')).encode() + b'\n'
    manifest.write_bytes(original)
    fake_transfer(monkeypatch, payload)

    assert download.fetch(
        url, target, manifest, params={'year': 2024, 'quarter': 1}
    ) == target
    assert target.read_bytes() == payload
    assert manifest.read_bytes() == original


def test_prevalidated_local_post_response_can_be_registered(tmp_path, monkeypatch):
    target = tmp_path / 't100.zip'
    with zipfile.ZipFile(target, 'w') as archive:
        archive.writestr('T100.csv', 'YEAR\n2024\n')
    manifest = tmp_path / 'manifest.json'
    monkeypatch.setattr(download.subprocess, 'run', lambda *args, **kwargs: pytest.fail('network transfer'))

    download.fetch(
        'https://example.test/form', target, manifest,
        source='BTS T100', params={'method': 'POST', 'year': 2024},
    )

    record = json.loads(manifest.read_text(encoding='utf-8'))
    assert record['sha256'] == download.digest(target)
    assert record['query_parameters'] == {'method': 'POST', 'year': 2024}
    assert record['zip_crc_valid'] is True
