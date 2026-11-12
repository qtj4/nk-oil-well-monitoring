import plotly.express as px

from .analytics import correlation, daily_patterns


def figures(df, well, parameter):
    selected = df[(df.well_id == well) & (df.parameter == parameter)].sort_values('timestamp').copy()
    unit = str(selected.unit.iloc[0]) if len(selected) else ''
    selected['prior_24_records_mean'] = selected.value.shift(1).rolling(24, min_periods=6).mean()
    trend = px.line(selected, x='timestamp', y=['value', 'prior_24_records_mean'],
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
