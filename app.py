import json

import pandas as pd
import streamlit as st

from nk_oil.charts import figures
from nk_oil.config import ROOT, paths
from nk_oil.database import query

st.set_page_config(page_title='NK Well Monitoring', layout='wide')
st.title('NK Well Monitoring · historical data')
st.caption('Galaz and Company LLP · NK field v2 · analytical decision support · no verified failure labels')
mode = st.sidebar.selectbox('Data mode', ['sample', 'full'])
target = paths(mode)
if not (target / 'latest_run.txt').exists():
    st.info(f'Prepare cached data: python -m nk_oil.cli fetch; python -m nk_oil.cli prepare --mode {mode}')
    st.stop()
run_id = (target / 'latest_run.txt').read_text().strip()
output = ROOT / 'results' / run_id
db = target / 'analysis.sqlite'
manifest = json.loads((output / 'run_manifest.json').read_text())
summary = json.loads((output / 'dataset_summary.json').read_text())
st.sidebar.caption(f'{mode.upper()} · {run_id}\nSource revision {manifest["source_revision"][:12]}')
if mode == 'sample':
    st.sidebar.warning('First 10 days of each month. Selection gaps are not source outages.')


@st.cache_data(max_entries=32)
def sql_cached(database, sql, params, version):
    return query(database, sql, params)


@st.cache_data(max_entries=8)
def parquet_cached(path, version):
    return pd.read_parquet(path)


version = manifest['data_hash']
wells = sql_cached(db, 'SELECT * FROM wells ORDER BY well_id', (), version)
well = st.sidebar.selectbox('Well', wells.well_id.tolist(), index=wells.well_id.tolist().index('NK-7'))
parameters = sql_cached(db, 'SELECT DISTINCT parameter FROM observations WHERE well_id=? ORDER BY parameter', (well,), version)
parameter = st.sidebar.selectbox('Parameter', parameters.parameter.tolist())
start, end = pd.Timestamp(summary['start']).date(), pd.Timestamp(summary['end']).date()
dates = st.sidebar.date_input('Period', (start, end), min_value=start, max_value=end)
if len(dates) != 2:
    st.info('Select both start and end dates.')
    st.stop()
clean = st.sidebar.checkbox('Only rows without source quality flags', False)
begin, finish = str(dates[0]), str(pd.Timestamp(dates[1]) + pd.Timedelta(days=1))
where = 'WHERE o.well_id=? AND o.timestamp>=? AND o.timestamp<?'
if clean:
    where += " AND o.flag=''"
selected = sql_cached(db, f'''SELECT o.*,w.well_type,p.unit FROM observations o
JOIN wells w USING(well_id) JOIN parameters p USING(parameter) {where} ORDER BY timestamp''',
                      (well, begin, finish), version)
if selected.empty:
    st.info('No observations in this period. Choose a covered date or another well.')
    st.stop()
selected['timestamp'] = pd.to_datetime(selected.timestamp)
signal = selected[selected.parameter == parameter]
if signal.empty:
    st.info('This parameter has no records in the selected period.')
    st.stop()
all_data = parquet_cached(target / 'long.parquet', version)
figs, pairs = figures(selected, well, parameter)
tabs = st.tabs(['Overview', 'Well explorer', 'Data quality', 'EDA', 'Regime changes', 'SQL & reports'])
with tabs[0]:
    columns = st.columns(4)
    for col, label, value in zip(columns, ['Source rows', 'Wells', 'Null sensor values', 'Duplicate keys'],
                                  [summary['rows'], summary['wells'], summary['null_values'], summary['duplicates']]):
        col.metric(label, f'{value:,}')
    st.write(f"Coverage: {summary['start']} — {summary['end']}. Mode: {mode}. Official train/test cutoff: {manifest['cutoff']}.")
    st.write(f"Source revision: `{manifest['source_revision']}` · data SHA-256: `{version}`")
    st.info('Dataset size is below the coursework recommendation. Instructor exception/additional legitimate data remains external.')
    st.dataframe(pd.read_csv(output / 'sql/01_coverage.csv'))
with tabs[1]:
    st.plotly_chart(figs['trend'], key='explorer_trend')
    st.caption('Rolling mean uses preceding 24 records, not necessarily 24 clock hours. No interpolation.')
    st.dataframe(signal[['timestamp', 'value', 'unit', 'flag', 'n_obs', 'split']])
    st.download_button('Download selected observations', signal.to_csv(index=False), f'{well}_{parameter}.csv', 'text/csv')
    st.download_button('Download interactive trend', figs['trend'].to_html(include_plotlyjs=True), 'trend.html', 'text/html')
with tabs[2]:
    st.warning('May area scaling is a possible calibration artifact; NK-7 June behavior has several possible explanations. Neither is a verified fault.')
    st.dataframe(pd.read_csv(output / 'known_issues.csv'))
    st.dataframe(pd.read_csv(output / 'quality_report.csv'))
    st.plotly_chart(figs['quality'], key='quality_heatmap')
    gaps = pd.read_csv(output / 'sql/04_gaps.csv')
    st.caption('LAG gaps are absent hour slots, distinct from NULL values. Sample gaps include intentionally omitted dates.')
    st.dataframe(gaps[gaps.well_id == well])
with tabs[3]:
    group_figs, _ = figures(all_data, well, parameter)
    st.plotly_chart(group_figs['distribution'], key='group_box')
    st.plotly_chart(group_figs['daily_pattern'], key='daily_pattern')
    st.caption('Types have different sensors and units. Box plots pool observations with unequal coverage; no causal comparison.')
    st.plotly_chart(figs['correlation'], key='correlation')
    st.write('Pairwise shared-hour counts (selected well and period):')
    st.dataframe(pairs)
    st.caption('Correlations use at least 24 shared timestamps. Available pairs and coverage differ; season/calibration may confound association.')
with tabs[4]:
    st.write('Daily medians with at least 12 unflagged readings; area excluded. Fixed training median/MAD reference. Aug 8 excluded because it straddles the source split.')
    comparison = pd.read_csv(output / 'methods_comparison.csv')
    st.dataframe(comparison)
    method = st.selectbox('Detector', ['no_change', 'rolling_shift', 'cusum'])
    sensitivity = st.selectbox('Threshold sensitivity (precomputed)', ['100%', '80%', '120%'])
    st.caption('Frozen thresholds: rolling 3 scaled units; CUSUM h=5, drift=0.5; cooldown 7 days. Counts are not accuracy.')
    event_file = 'events.csv' if sensitivity == '100%' else f'events_threshold_{sensitivity[:-1]}.csv'
    events = pd.read_csv(output / event_file, parse_dates=['timestamp'])
    chosen = events[(events.well_id == well) & (events.parameter == parameter) & (events.method == method)
                    & (events.timestamp >= pd.Timestamp(begin)) & (events.timestamp < pd.Timestamp(finish))]
    event_fig = figs['trend']
    for event in chosen.itertuples():
        event_fig.add_vline(x=event.timestamp.timestamp() * 1000, line_dash='dot', line_color='#d85925')
    st.plotly_chart(event_fig, key='event_trend')
    st.dataframe(chosen)
    st.caption('Training-era markers are retrospective descriptions using a training-wide reference; test markers use frozen reference. Threshold sensitivity exports are descriptive, never tuned to test outcomes.')
with tabs[5]:
    queries = sorted((ROOT / 'sql/queries').glob('*.sql'))
    query_name = st.selectbox('Analytical SQL', [p.stem for p in queries])
    sql_file = next(p for p in queries if p.stem == query_name)
    sql_text = sql_file.read_text()
    st.code(sql_text, language='sql')
    table = sql_cached(db, sql_text, (), version)
    st.dataframe(table)
    st.download_button('Download SQL result', table.to_csv(index=False), f'{query_name}.csv', 'text/csv')
    st.caption('Eight predefined queries return real SQLite results to Pandas; arbitrary user SQL is not executed.')
