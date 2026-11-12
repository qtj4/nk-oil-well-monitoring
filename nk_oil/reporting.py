import html
import json
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px

from .charts import break_gaps


def diagnostic(data, events, comparison, manifest, well, parameter, begin, finish):
    selected = data[(data.well_id == well) & (data.timestamp >= pd.Timestamp(begin))
                    & (data.timestamp < pd.Timestamp(finish))].copy()
    if selected.empty:
        raise ValueError('No observations for diagnostic period')
    visible = events[(events.well_id == well) & (pd.to_datetime(events.timestamp) >= pd.Timestamp(begin))
                     & (pd.to_datetime(events.timestamp) < pd.Timestamp(finish))] if len(events) else events
    signal = selected[selected.parameter == parameter].sort_values('timestamp')
    unit = str(signal.unit.iloc[0]) if len(signal) else ''
    chart = px.line(break_gaps(signal, ['value']), x='timestamp', y='value', title=f'{well} · {parameter} ({unit})')
    chart.update_traces(connectgaps=False)
    stats = selected.groupby(['parameter', 'unit'], observed=True).value.agg(['count', 'mean', 'median', 'std', 'min', 'max'])
    flags = selected.groupby(['parameter', 'flag'], observed=True).size().reset_index(name='records')
    coverage = selected.groupby('parameter', observed=True).agg(records=('timestamp', 'size'),
                                                               distinct_hours=('timestamp', 'nunique'),
                                                               nonnull_values=('value', 'count'))
    coverage['expected_hours_in_requested_period'] = int((pd.Timestamp(finish) - pd.Timestamp(begin)).total_seconds() / 3600)
    coverage['absent_hours'] = coverage.expected_hours_in_requested_period - coverage.distinct_hours
    coverage['null_values'] = coverage.records - coverage.nonnull_values
    time_start, time_end = selected.timestamp.min(), selected.timestamp.max()
    body = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>NK diagnostic · {html.escape(well)}</title>
<style>body{{font:16px system-ui;max-width:1200px;margin:40px auto;color:#18323e;padding:20px}}
table{{border-collapse:collapse;font-size:12px;display:block;overflow:auto}}td,th{{padding:7px;border:1px solid #d6e0e4}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere}}h1,h2{{color:#136e74}}</style>
<h1>Historical well diagnostic · {html.escape(well)}</h1>
<p>Generated UTC: {datetime.now(timezone.utc).isoformat()}<br>Requested period: {html.escape(str(begin))} — {html.escape(str(finish))} (end exclusive).</p>
<h2>Provenance</h2><pre>{html.escape(json.dumps(manifest, indent=2))}</pre>
<h2>Coverage</h2><p>{len(selected):,} parameter observations; {selected.timestamp.nunique():,} distinct hours;
observed scope {time_start} — {time_end}. {int(selected.value.isna().sum())} NULL sensor values.
Missing records differ from NULLs; sample selection and edge truncation reduce coverage. Hourly slots are expected for each observed parameter; fountain sensors may report asynchronously.</p>{coverage.to_html(escape=True)}
<h2>Sensor summaries and units</h2>{stats.to_html(escape=True)}
<h2>Time series</h2>{chart.to_html(full_html=False, include_plotlyjs=True)}
<h2>Data quality</h2>{flags.to_html(index=False, escape=True)}
<p>May area scale change may reflect calibration; June NK-7 behavior is not verified equipment failure. Values are not imputed or automatically corrected.</p>
<h2>Candidate events and analyst reviews</h2>{visible.to_html(index=False, escape=True)}
<h2>Method comparison</h2>{comparison.to_html(index=False, escape=True)}
<h2>Limitations</h2><p>No verified failure labels; counts are not accuracy. Daily candidate timestamp labels the bin start and becomes available next day.
Before/after descriptions use future context solely for retrospective interpretation.
Analyst "confirmed" means the analyst confirmed a candidate for review purposes, not official failure ground truth.
Historical single-user decision support, no equipment-control actions. Source: Arailym Tleubayeva / Galaz and Company LLP, NK v2, Apache-2.0; source revision above.</p></html>'''
    return body
