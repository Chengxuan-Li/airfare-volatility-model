"""Verify the exact raw paths consumed by the original pilot, not other stages."""
import json
from pathlib import Path

from src.acquisition.download import digest
from src.config import AIRPORTS, MANIFESTS, PERIODS, RAW, bts_path


def verify_pilot_inputs():
    expected = [('ourairports.json', RAW/'ourairports.csv'),
                ('bts_delay_causes.json', RAW/'bts_delay_causes_2022_2024.zip')]
    for year, quarter in PERIODS:
        for table in ('Market', 'Ticket'):
            expected.append((f'bts_db1b_{table.lower()}_{year}_q{quarter}.json',
                             bts_path(table, year, quarter)))
    expected.extend((f'weather_{airport}.json', RAW/'weather'/f'{airport}_2020_2024.json')
                    for airport in AIRPORTS)
    for name, target in expected:
        manifest = MANIFESTS/name
        record = json.loads(manifest.read_text(encoding='utf-8'))
        for field in ('local_path', 'sha256'):
            if not isinstance(record.get(field), str) or not record[field]:
                raise ValueError(f'Missing or invalid {field}: {name}')
        if Path(record['local_path']).resolve() != target.resolve():
            raise ValueError(f'Manifest path differs from consumed input: {name}')
        if digest(target) != record['sha256']:
            raise ValueError(f'Raw input checksum mismatch: {name}')
    return len(expected)
