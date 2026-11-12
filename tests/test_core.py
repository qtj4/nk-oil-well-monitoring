import pandas as pd
import pytest

from nk_oil.database import build, query
from nk_oil.dataset import validate
from nk_oil.transform import to_wide


@pytest.fixture
def frame():
    return validate(pd.DataFrame([
        ['A', 'fountain', '2026-01-01 01:00', 'pressure', 2., 'atm', 1, ''],
        ['A', 'fountain', '2026-01-01 00:00', 'pressure', 1., 'atm', 1, ''],
        ['B', 'sucker_rod_pump', '2026-01-01 00:00', 'pressure', 9., 'atm', 1, ''],
    ], columns=['well_id', 'well_type', 'timestamp', 'parameter', 'value', 'unit', 'n_obs', 'flag']))


def test_pivot_independence(frame):
    wide = to_wide(frame)
    assert wide[wide.well_id == 'B'].pressure.iloc[0] == 9
    assert wide[wide.well_id == 'A'].pressure.tolist() == [1, 2]


def test_duplicate_rejected(frame):
    with pytest.raises(ValueError, match='Duplicate'):
        to_wide(pd.concat([frame, frame]))


def test_validation(frame):
    with pytest.raises(ValueError):
        validate(frame.drop(columns='unit'))
    bad = frame.copy()
    bad['timestamp'] = 'invalid'
    with pytest.raises(ValueError):
        validate(bad)


def test_db_roundtrip(frame, tmp_path):
    path = tmp_path / 'test.sqlite'
    build(frame, path)
    build(frame, path)
    assert query(path, 'SELECT COUNT(*) n FROM observations').iloc[0, 0] == 3


def test_empty_and_unknown_flags(frame):
    assert validate(frame.iloc[:0]).empty
    unknown = frame.copy()
    unknown['flag'] = 'undocumented_flag'
    assert str(validate(unknown).flag.iloc[0]) == 'undocumented_flag'


def test_conflicting_dimension(frame, tmp_path):
    bad = frame.copy()
    bad['unit'] = ['atm', 'kg', 'atm']
    with pytest.raises(ValueError, match='Conflicting'):
        build(bad, tmp_path / 'bad.sqlite')
