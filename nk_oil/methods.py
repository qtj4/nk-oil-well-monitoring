"""Daily causal candidate regime shifts. No supervised accuracy claims."""
import hashlib
import json

import numpy as np
import pandas as pd

from .config import CUTOFF
from .performance import measure

METHODS = ['no_change', 'rolling_shift', 'cusum']
EVENT_COLUMNS = ['event_id', 'well_id', 'parameter', 'timestamp', 'split', 'method', 'score',
                 'threshold', 'value', 'data_hash', 'config']


def daily_data(df, include_area=False, clean=True):
    data = df.copy()
    if not include_area:
        data = data[data.parameter != 'dynamometer_area']
    if clean:
        data = data[data.flag == '']
    data['day'] = data.timestamp.dt.floor('D')
    # The supplied split cuts through Aug 8; never merge that day's train and test rows.
    data = data[data.day != pd.Timestamp(CUTOFF).floor('D')]
    grouped = data.groupby(['well_id', 'parameter', 'day', 'split'], observed=True)
    daily = grouped.value.agg(value='median', count='count').reset_index().rename(columns={'day': 'timestamp'})
    return daily[daily['count'] >= 12].sort_values(['well_id', 'parameter', 'timestamp'])


def training_reference(series):
    train = series[series.split == 'train'].value.dropna()
    if len(train) < 3:
        return None
    center = float(train.median())
    scale = float((train - center).abs().median() * 1.4826)
    if not np.isfinite(scale) or scale <= 1e-12:
        scale = max(float(train.std()), abs(center) * .01, 1e-6)
    return center, scale


def detect(daily, method, data_hash, multiplier=1.):
    if method not in METHODS:
        raise ValueError('Unknown method')
    config = json.dumps({'version': 1, 'window_days': 3, 'cooldown_days': 7, 'multiplier': multiplier,
                         'normalizer': 'train_median_MAD', 'minimum_daily_records': 12}, sort_keys=True)
    events = []
    if method == 'no_change':
        return pd.DataFrame(columns=EVENT_COLUMNS)
    for (well, parameter), series in daily.groupby(['well_id', 'parameter'], observed=True):
        series = series.sort_values('timestamp')
        reference = training_reference(series)
        if reference is None:
            continue
        center, scale = reference
        past = []
        last_time = None
        last_event = None
        positive = negative = 0.
        for row in series.itertuples():
            if last_time is not None and (row.timestamp - last_time).days > 1:
                past = []
                positive = negative = 0.
            z = (row.value - center) / scale
            if method == 'rolling_shift':
                # Reference contains only earlier days; train fit is frozen for test evaluation.
                score = abs(row.value - np.mean(past[-3:])) / scale if len(past) >= 3 else 0.
                threshold = 3. * multiplier
            else:
                positive = max(0., positive + z - .5)
                negative = min(0., negative + z + .5)
                score = max(positive, -negative)
                threshold = 5. * multiplier
            cooled = last_event is None or (row.timestamp - last_event).days >= 7
            if score > threshold and cooled:
                ident = f'{data_hash}|{config}|{method}|{well}|{parameter}|{row.timestamp.isoformat()}'
                events.append(dict(zip(EVENT_COLUMNS, [hashlib.sha256(ident.encode()).hexdigest(),
                    well, parameter, row.timestamp, row.split, method, float(score), threshold,
                    row.value, data_hash, config])))
                last_event = row.timestamp
                positive = negative = 0.
            past.append(row.value)
            last_time = row.timestamp
    return pd.DataFrame(events, columns=EVENT_COLUMNS)


def compare(df, data_hash):
    daily = daily_data(df)
    all_events, comparison = [], []
    for method in METHODS:
        events, perf = measure(detect, daily, method, data_hash)
        low = detect(daily, method, data_hash, .8)
        high = detect(daily, method, data_hash, 1.2)
        units = int((daily.split == 'test').sum())
        count = int((events.split == 'test').sum())
        comparison.append({'method': method, 'test_events': count, 'train_events': len(events) - count,
                           'test_daily_units': units, 'test_events_per_100_days': 100 * count / max(units, 1),
                           'test_events_threshold_80pct': int((low.split == 'test').sum()),
                           'test_events_threshold_120pct': int((high.split == 'test').sum()),
                           'accuracy': 'not identifiable: no reference labels', **perf})
        all_events.append(events)
    return pd.concat(all_events, ignore_index=True), pd.DataFrame(comparison), daily
