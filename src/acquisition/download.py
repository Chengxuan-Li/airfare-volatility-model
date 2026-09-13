"""Bounded public downloads and verified local caches; no credential loading."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate_zip(path):
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f'ZIP CRC failed: {bad}')
        return [{'name': x.filename, 'uncompressed_bytes': x.file_size}
                for x in archive.infolist()]


def _request_mismatch(record, url, params):
    if record.get('url') != url:
        return True
    if 'query_parameters' in record:
        return record['query_parameters'] != params
    legacy_params = {key: record[key] for key in ('year', 'quarter') if key in record}
    return bool(legacy_params) and legacy_params != params


def fetch(url, target, manifest_path, *, source='BTS', params=None):
    target, manifest_path = Path(target), Path(manifest_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    if target.exists():
        checksum = digest(target)
        if previous and previous['sha256'] != checksum:
            raise ValueError(f'Cached checksum mismatch: {target.name}')
        if previous:
            if _request_mismatch(previous, url, params):
                raise ValueError(f'Cached request identity mismatch: {target.name}')
            if target.suffix == '.zip':
                validate_zip(target)
            elif target.suffix == '.json':
                payload = json.loads(target.read_text(encoding='utf-8'))
                if isinstance(payload, dict) and payload.get('error'):
                    raise ValueError('Cached JSON contains source error')
            print(f'Cache verified: {target.name}', flush=True)
            return target
    else:
        if previous and _request_mismatch(previous, url, params):
            raise ValueError(f'Download request identity mismatch: {target.name}')
        partial = target.with_suffix(target.suffix + '.part')
        curl = shutil.which('curl.exe') or shutil.which('curl')
        if curl is None:
            raise RuntimeError('curl executable is required for bounded transfers')
        subprocess.run([curl, '--fail', '--silent', '--show-error',
                        '--connect-timeout', '20', '--max-time', '240',
                        '--speed-time', '30', '--speed-limit', '1024',
                        '--output', str(partial), url], check=True, timeout=260)
        if target.suffix == '.zip':
            validate_zip(partial)
        elif target.suffix == '.json':
            payload = json.loads(partial.read_text(encoding='utf-8'))
            if isinstance(payload, dict) and payload.get('error'):
                raise ValueError(f'Source error: {payload.get("reason")}')
        checksum = digest(partial)
        if previous and previous['sha256'] != checksum:
            raise ValueError(f'Downloaded checksum mismatch: {target.name}')
        if previous and _request_mismatch(previous, url, params):
            raise ValueError(f'Downloaded request identity mismatch: {target.name}')
        partial.rename(target)
        if previous:
            print(f'Reacquisition verified: {target.name}', flush=True)
            return target
    record = {'source': source, 'url': url, 'query_parameters': params,
              'retrieved_at_utc': datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat(),
              'local_path': target.as_posix(), 'bytes': target.stat().st_size,
              'sha256': checksum, 'transformations': 'None; original response retained.',
              'license_notes': 'See docs/data/09_data_legal_technical_constraints.md; raw files not committed.'}
    if target.suffix == '.zip':
        record['members'] = validate_zip(target)
        record['zip_crc_valid'] = True
    manifest_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Acquired: {target.name} ({record["bytes"]:,} bytes)', flush=True)
    return target
