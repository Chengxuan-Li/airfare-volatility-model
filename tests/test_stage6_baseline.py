import hashlib
import json

import pandas as pd
import pytest

from src.stage6 import baseline


def frozen_fixture(tmp_path, monkeypatch):
    folder = tmp_path/'baseline'
    folder.mkdir()
    monkeypatch.setattr(baseline, 'BASELINE_DIRECTORY', folder)
    ranking = pd.DataFrame({'AirportID': [100,200,300], 'codes': ['AAA','BBB','CCC'],
        'passengers': [10,9,1], 'rank': [1,2,3], 'selected': [True,True,False]})
    ranking.to_csv(folder/'airport_ranking.csv',index=False)
    for name in baseline.CSV_FILES:
        if name != 'airport_ranking.csv':
            pd.DataFrame({'Year':[2010], 'RPCarrier':['01']}).to_csv(folder/name,index=False)
    (folder/'quality_audit.json').write_text(json.dumps({'selection':{'year':2010,'quarter':1}}))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
    verification=folder/'verification.json'
    verification.write_text(json.dumps({'output_sha256':hashes}))
    manifest=tmp_path/'frozen.json'
    manifest.write_text(json.dumps({'baseline_year':2010,'baseline_directory':str(folder),
        'verification_sha256':hashlib.sha256(verification.read_bytes()).hexdigest(),
        'ranking_sha256':hashes['airport_ranking.csv'],'expected_selected_airports':2}))
    return folder,manifest


def test_frozen_sample_uses_verified_selection_and_preserves_code_tokens(tmp_path,monkeypatch):
    folder,manifest=frozen_fixture(tmp_path,monkeypatch)
    ranking,audit,tables=baseline.load_baseline(manifest)
    assert ranking.loc[ranking.selected,'AirportID'].tolist()==[100,200]
    assert audit=={'year':2010,'quarter':1}
    assert tables['fare_carrier_cells.csv'].RPCarrier.tolist()==['01']


@pytest.mark.parametrize('name',['airport_ranking.csv','fare_carrier_cells.csv','verification.json'])
def test_changed_baseline_is_rejected_before_use(tmp_path,monkeypatch,name):
    folder,manifest=frozen_fixture(tmp_path,monkeypatch)
    with (folder/name).open('a') as f: f.write('\nchanged')
    with pytest.raises(ValueError,match='checksum'):
        baseline.load_baseline(manifest)
