import plotly.express as px
import pandas as pd

from .analytics import correlation, daily_patterns


def break_gaps(frame, values):
    """Insert chart-only NULL separators; never alter source values or analytical tables."""
    ordered = frame.sort_values('timestamp').copy()
    gaps = ordered.timestamp.diff() > pd.Timedelta(hours=1)
    if not gaps.any():
        return ordered
    separators = ordered.loc[gaps].copy()
    separators['timestamp'] = ordered.timestamp.shift().loc[gaps] + pd.Timedelta(hours=1)
    for name in values:
        separators[name] = float('nan')
    return pd.concat([ordered, separators], ignore_index=True).sort_values('timestamp')


def figures(df, well, parameter):
    selected = df[(df.well_id == well) & (df.parameter == parameter)].sort_values('timestamp').copy()
    unit = str(selected.unit.iloc[0]) if len(selected) else ''
    selected['prior_24_records_mean'] = selected.value.shift(1).rolling(24, min_periods=6).mean()
    plot_data = break_gaps(selected, ['value', 'prior_24_records_mean'])
    trend = px.line(plot_data, x='timestamp', y=['value', 'prior_24_records_mean'],
                    title=f'{well} · {parameter} ({unit}) · source observations')
    trend.update_yaxes(title=f'{parameter} ({unit})')
    group = df[df.parameter == parameter]
    distribution = px.box(group, x='well_type', y='value', color='well_id',
                          title=f'{parameter} ({unit}) by well and type; unequal coverage')
    hourly = daily_patterns(group)
    pattern = px.line(hourly, x='hour', y='mean', color='well_type',
                      title=f'Hour-of-day mean · {parameter} ({unit}); pooled observations', hover_data=['count'])
    corr, pairs = correlation(df[df.well_id == well])
    heatmap = px.imshow(corr, zmin=-1, zmax=1, color_continuous_scale='RdBu_r',
                        title=f'{well} · pairwise Pearson r · at least 24 shared timestamps')
    quality = (df.assign(flagged=df.flag != '').groupby(['well_id', 'parameter'], observed=True)
               .flagged.mean().reset_index())
    flags = px.density_heatmap(quality, x='parameter', y='well_id', z='flagged', histfunc='avg',
                               title='Source-flagged observation fraction; blank ≠ zero coverage')
    return {'trend': trend, 'distribution': distribution, 'daily_pattern': pattern,
            'correlation': heatmap, 'quality': flags}, pairs
