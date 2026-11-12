"""Coverage-aware descriptive statistics; no cross-well correlation mixing."""
import pandas as pd


def summaries(df):
    return df.groupby(['well_type', 'well_id', 'parameter', 'unit'], observed=True).value.describe().reset_index()


def daily_patterns(df):
    return (df.assign(hour=df.timestamp.dt.hour)
            .groupby(['well_type', 'parameter', 'unit', 'hour'], observed=True)
            .value.agg(['mean', 'count', 'std']).reset_index())


def correlation(df, min_pairs=24):
    wide = df.pivot(index='timestamp', columns='parameter', values='value')
    valid = wide.notna().astype(int)
    pairs = valid.T @ valid
    return wide.corr(min_periods=min_pairs), pairs


def known_issues(df):
    rows = []
    for well, group in df[df.parameter == 'dynamometer_area'].groupby('well_id', observed=True):
        before = group[(group.timestamp >= '2026-04-01') & (group.timestamp < '2026-05-01')].value
        after = group[(group.timestamp >= '2026-05-01') & (group.timestamp < '2026-06-01')].value
        rows.append({'well_id': well, 'issue': 'May area scale', 'before_n': before.count(),
                     'after_n': after.count(), 'before_median': before.median(), 'after_median': after.median(),
                     'ratio': after.median() / before.median() if before.median() else None})
    nk7 = df[(df.well_id == 'NK-7') & (df.parameter == 'SPM')]
    for label, mask in [('May', (nk7.timestamp >= '2026-05-01') & (nk7.timestamp < '2026-06-01')),
                        ('June', (nk7.timestamp >= '2026-06-01') & (nk7.timestamp < '2026-07-01'))]:
        values = nk7[mask].value.dropna()
        rows.append({'well_id': 'NK-7', 'issue': f'SPM {label}', 'after_n': len(values),
                     'after_median': values.median(), 'zero_fraction': float((values == 0).mean())})
    return pd.DataFrame(rows)
