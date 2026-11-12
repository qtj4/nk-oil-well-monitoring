import hashlib
import json

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from nk_oil.config import ROOT, paths
from nk_oil.database import query
from nk_oil.dataset import KEY, fingerprint

pytestmark = pytest.mark.skipif(not (paths('full') / 'latest_run.txt').exists(), reason='Full artifacts not prepared')


def test_actual_full_source_and_artifact_integrity():
    target = paths('full')
    run_id = (target / 'latest_run.txt').read_text().strip()
    output = ROOT / 'results' / run_id
    manifest = json.loads((output / 'run_manifest.json').read_text())
    summary = json.loads((output / 'dataset_summary.json').read_text())
    df = pd.read_parquet(target / 'long.parquet')
    assert len(df) == summary['rows'] == 258387
    assert summary['train_rows'] == 206706
    assert summary['test_rows'] == 51681
    assert not df.duplicated(KEY).any()
    assert df[df.split == 'train'].timestamp.max() < df[df.split == 'test'].timestamp.min()
    assert fingerprint(target / 'long.parquet') == manifest['data_hash']
    assert query(target / 'analysis.sqlite', 'SELECT COUNT(*) n FROM observations').iloc[0, 0] == len(df)
    assert query(target / 'analysis.sqlite', 'PRAGMA foreign_key_check').empty
    tree = json.loads((ROOT / 'data/raw/source_tree.json').read_text())
    for file in ['train.csv', 'test.csv']:
        path = ROOT / 'data/raw' / file
        info = next(f for f in tree if f['path'] == file)
        assert path.stat().st_size == info['size']
        if 'lfs' in info:
            assert fingerprint(path) == info['lfs']['oid']
        else:
            content = path.read_bytes()
            assert hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest() == info['oid']


def test_full_ui_filters_and_report(tmp_path, monkeypatch):
    monkeypatch.setenv('NK_REVIEW_DB', str(tmp_path / 'full_ui_reviews.sqlite'))
    at = AppTest.from_file(ROOT / 'app.py', default_timeout=40).run()
    next(w for w in at.selectbox if w.label == 'Data mode').select('full').run()
    assert not at.exception
    assert len(at.tabs) == 7
    for well in ['NK-82', 'NK-75', 'NK-7']:
        next(w for w in at.selectbox if w.label == 'Well').select(well).run()
        assert not at.exception
    next(w for w in at.checkbox if w.label == 'Only rows without source quality flags').check().run()
    assert not at.exception
    next(w for w in at.selectbox if w.label == 'Threshold sensitivity (precomputed)').select('120%').run()
    assert not at.exception
    next(w for w in at.button if w.label == 'Generate well diagnostic report').click().run()
    assert not at.exception
    assert 'full' in at.session_state['diagnostic'][1]
