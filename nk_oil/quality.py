from .dataset import KEY


def audit(df):
    return {
        'rows': len(df), 'wells': int(df.well_id.nunique()),
        'duplicates': int(df.duplicated(KEY).sum()),
        'null_values': int(df.value.isna().sum()),
        'start': str(df.timestamp.min()), 'end': str(df.timestamp.max()),
        'flags': {str(k): int(v) for k, v in df.flag.value_counts().items()},
    }


def coverage(df):
    groups = df.groupby(['well_id', 'parameter'], observed=True)
    rows = []
    for (well, parameter), group in groups:
        expected = int((group.timestamp.max() - group.timestamp.min()).total_seconds() / 3600) + 1
        values = group.value.dropna()
        q1, q3 = values.quantile([.25, .75]) if len(values) else (float('nan'), float('nan'))
        iqr = q3 - q1
        invalid = (values < 0) if parameter != 'dynamometer_area' else values < float('-inf')
        if parameter == 'pump_fillage':
            invalid |= values > 100
        rows.append({'well_id': well, 'parameter': parameter, 'records': len(group),
                     'expected_hour_slots': expected, 'absent_slots': expected - group.timestamp.nunique(),
                     'null_values': int(group.value.isna().sum()),
                     'flagged': int((group.flag != '').sum()),
                     'iqr_outliers': int(((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)).sum()),
                     'domain_range_violations': int(invalid.sum()),
                     'zero_values': int((group.value == 0).sum())})
    import pandas as pd
    return pd.DataFrame(rows)
