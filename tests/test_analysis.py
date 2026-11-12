import numpy as np
import pandas as pd
import pytest

from nk_oil.analytics import known_issues
from nk_oil.config import ROOT
from nk_oil.database import build, query
from nk_oil.dataset import validate
from nk_oil.methods import daily_data, detect, training_reference
from nk_oil.pipeline import run_queries


def test_all_eight_sql_queries(tmp_path):
    # Synthetic tests only: known gap, NULL value, flagged group and two well types.
    records = []
    for well, kind in [('A', 'fountain'), ('B', 'sucker_rod_pump')]:
        for hour in [0, 1, 3]:
            records.append([well, kind, f'2026-01-01 {hour:02d}:00:00', 'p',
                            None if hour == 1 else hour + 1., 'u', 1, 'custom' if hour == 3 else ''])
    df = validate(pd.DataFrame(records, columns=['well_id', 'well_type', 'timestamp', 'parameter', 'value', 'unit', 'n_obs', 'flag']))
    db = tmp_path / 'fixture.sqlite'
    build(df, db)
    tables = run_queries(db)
    assert len(tables) == 8
    assert tables['01_coverage'].records.sum() == 6
    assert tables['01_coverage'].valid_values.sum() == 4
    assert tables['04_gaps'].missing_hours.tolist() == [1, 1]
    assert len(tables['08_latest']) == 2
    assert set(tables['08_latest'].value) == {4.}
    assert len(tables['03_flagged_groups']) == 2
    assert tables['07_type_summary'].null_values.sum() == 2
    rolling = tables['05_causal_rolling']
    assert rolling[rolling.timestamp.str.endswith('00:00:00')].preceding_24_records_mean.isna().all()
    assert rolling[rolling.timestamp.str.endswith('03:00:00')].preceding_24_records_mean.tolist() == [1., 1.]
    assert tables['06_flags'].records.sum() == 6
    assert query(db, 'PRAGMA foreign_key_check').empty


@pytest.fixture
def daily():
    n = 80
    return pd.DataFrame({'well_id': ['NK-7'] * n, 'parameter': ['SPM'] * n,
                         'timestamp': pd.date_range('2026-06-20', periods=n, freq='D'),
                         'value': np.r_[np.tile([1., 1.1], 30), np.repeat(4., 20)],
                         'split': ['train'] * 50 + ['test'] * 30, 'count': [24] * n})


def test_detectors_synthetic_change(daily):
    assert detect(daily, 'no_change', 'fixture').empty
    for method in ['rolling_shift', 'cusum']:
        events = detect(daily, method, 'fixture')
        assert ((events.timestamp >= '2026-08-19') & (events.timestamp <= '2026-08-22')).any()
        assert events.event_id.is_unique
        assert events.event_id.tolist() == detect(daily, method, 'fixture').event_id.tolist()
    with pytest.raises(ValueError):
        detect(daily, 'unknown', 'fixture')


def test_no_future_or_test_normalizer_leak(daily):
    changed = daily.copy()
    changed.loc[changed.index >= 75, 'value'] = 10000.
    assert training_reference(daily) == training_reference(changed)
    for method in ['rolling_shift', 'cusum']:
        before = detect(daily, method, 'fixture')
        after = detect(changed, method, 'fixture')
        bound = daily.timestamp.iloc[75]
        assert before[before.timestamp < bound].event_id.tolist() == after[after.timestamp < bound].event_id.tolist()


def test_daily_split_boundary_and_low_coverage():
    timestamps = pd.date_range('2026-08-07', periods=72, freq='h')
    df = pd.DataFrame({'well_id': 'X', 'parameter': 'p', 'timestamp': timestamps, 'value': 1., 'flag': '',
                       'split': np.where(timestamps < pd.Timestamp('2026-08-08 23:00'), 'train', 'test')})
    result = daily_data(df)
    assert not (result.timestamp == '2026-08-08').any()
    assert result.split.tolist() == ['train', 'test']
    df.loc[df.timestamp >= '2026-08-09 02:00', 'flag'] = 'unknown'
    assert len(daily_data(df)) == 1


def test_measured_issue_boundaries():
    df = pd.DataFrame({'well_id': ['NK-7'] * 4, 'parameter': ['dynamometer_area'] * 2 + ['SPM'] * 2,
                       'timestamp': pd.to_datetime(['2026-04-15', '2026-05-15', '2026-05-15', '2026-06-15']),
                       'value': [10., 200., 4., 1.]})
    issues = known_issues(df)
    assert issues.iloc[0].ratio == 20.
    assert issues.iloc[2].after_median == 1.


def test_sql_files_are_individual():
    assert len(list((ROOT / 'sql/queries').glob('*.sql'))) == 8
