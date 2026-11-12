import shutil
import urllib.request

import pytest

from nk_oil import pipeline
from nk_oil.config import ROOT


def test_offline_bundled_monthly_sample(tmp_path, monkeypatch):
    target = tmp_path / 'data/sample'
    target.mkdir(parents=True)
    shutil.copy2(ROOT / 'data/sample/monthly_source.parquet', target / 'monthly_source.parquet')
    monkeypatch.setattr(pipeline, 'ROOT', tmp_path)

    def no_network(*args, **kwargs):
        raise AssertionError('Offline test attempted network access')

    monkeypatch.setattr(urllib.request, 'urlopen', no_network)
    df = pipeline.load_source('sample')
    assert len(df) == 85423
    assert df.well_id.nunique() == 10
    assert set(df.split) == {'train', 'test'}
    assert df.timestamp.dt.month.nunique() == 9


def test_source_archive_without_git(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, 'ROOT', tmp_path)
    assert 'unavailable' in pipeline.git_revision()
    with pytest.raises(FileNotFoundError, match='fetch'):
        pipeline.load_source('full')
