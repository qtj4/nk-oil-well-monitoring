import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from nk_oil.charts import figures
from nk_oil.config import ROOT, paths
from nk_oil.database import query
from nk_oil.events import STATUSES, ingest, queue, review
from nk_oil.reporting import diagnostic

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
presets = {'NK-7 June transition': ('NK-7', 'SPM', '2026-05-01', '2026-07-01'),
           'May area scale investigation': ('NK-82', 'dynamometer_area', '2026-04-01', '2026-06-10'),
           'Fountain pressure comparison': ('NK-75', 'line_pressure', '2026-01-01', '2026-09-10')}


def apply_scenario():
    preset = presets.get(st.session_state.scenario)
    if preset:
        st.session_state.well_choice = preset[0]
        st.session_state.parameter_choice = preset[1]
        st.session_state.date_choice = (max(pd.Timestamp(preset[2]).date(), pd.Timestamp(summary['start']).date()),
                                        min(pd.Timestamp(preset[3]).date(), pd.Timestamp(summary['end']).date()))


available_presets = [name for name, spec in presets.items() if spec[0] in wells.well_id.tolist()
                     and pd.Timestamp(spec[2]) <= pd.Timestamp(summary['end'])
                     and pd.Timestamp(spec[3]) >= pd.Timestamp(summary['start'])]
st.sidebar.selectbox('Demo scenario', ['Custom'] + available_presets, key='scenario', on_change=apply_scenario)
well = st.sidebar.selectbox('Well', wells.well_id.tolist(), index=wells.well_id.tolist().index('NK-7'), key='well_choice')
parameters = sql_cached(db, 'SELECT DISTINCT parameter FROM observations WHERE well_id=? ORDER BY parameter', (well,), version)
if st.session_state.get('parameter_choice') not in parameters.parameter.tolist():
    st.session_state.parameter_choice = parameters.parameter.iloc[0]
parameter = st.sidebar.selectbox('Parameter', parameters.parameter.tolist(), key='parameter_choice')
start, end = pd.Timestamp(summary['start']).date(), pd.Timestamp(summary['end']).date()
dates = st.sidebar.date_input('Period', (start, end), min_value=start, max_value=end, key='date_choice')
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
tabs = st.tabs(['Overview', 'Well explorer', 'Data quality', 'EDA', 'Regime changes', 'SQL & reports', 'Review workbench'])
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
    st.caption('Daily timestamps label the bin start; the daily median and its candidate become available after the day closes.')
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
    report_key = f'{run_id}:{well}:{parameter}:{begin}:{finish}:{clean}'
    if st.button('Generate well diagnostic report'):
        review_db = Path(os.getenv('NK_REVIEW_DB', str(ROOT / 'data/reviews.sqlite')))
        candidates = pd.read_csv(output / 'events.csv', parse_dates=['timestamp'])
        ingest(review_db, candidates, manifest)
        reviewed = queue(review_db, run_id, well)
        report_manifest = {**manifest, 'ui_quality_filter_unflagged_only': clean,
                           'report_scope': {'well': well, 'parameter': parameter, 'begin': begin, 'finish': finish}}
        st.session_state.diagnostic = (report_key, diagnostic(selected, reviewed, comparison, report_manifest,
                                                            well, parameter, begin, finish))
    if st.session_state.get('diagnostic', (None,))[0] == report_key:
        st.download_button('Download self-contained HTML diagnostic', st.session_state.diagnostic[1],
                           f'{well}_diagnostic.html', 'text/html')
with tabs[6]:
    review_db = Path(os.getenv('NK_REVIEW_DB', str(ROOT / 'data/reviews.sqlite')))
    main_candidates = pd.read_csv(output / 'events.csv', parse_dates=['timestamp'])
    ingest(review_db, main_candidates, manifest)
    reviewed = queue(review_db, run_id, well)
    statuses = st.multiselect('Review status filter', STATUSES, default=STATUSES)
    queue_methods = st.multiselect('Review method filter', ['rolling_shift', 'cusum'], default=['rolling_shift', 'cusum'])
    visible = reviewed[(reviewed.status.isin(statuses)) & (reviewed.method.isin(queue_methods))
                       & (reviewed.parameter == parameter) & (pd.to_datetime(reviewed.timestamp) >= pd.Timestamp(begin))
                       & (pd.to_datetime(reviewed.timestamp) < pd.Timestamp(finish))]
    st.caption('Candidate events use the frozen 100% threshold. A confirmed review is an analyst decision, never an official failure label. History from other runs is retained separately.')
    if visible.empty:
        st.info('No candidate events match these filters. Try NK-7 / SPM, all dates, or broaden review status.')
    else:
        st.dataframe(visible)
        event_id = st.selectbox('Candidate event', visible.event_id.tolist(),
                                format_func=lambda ident: ' · '.join(str(visible.set_index('event_id').loc[ident, c])
                                                                   for c in ['timestamp', 'method', 'status']))
        current = visible[visible.event_id == event_id].iloc[0]
        st.write(f'Daily value {current.value:.4g}; score {current.score:.3g}; threshold {current.threshold:.3g}.')
        features_path = output / 'event_characterization.csv'
        if features_path.exists():
            features = pd.read_csv(features_path)
            detail = features[features.event_id == event_id]
            st.dataframe(detail)
            if not detail.empty:
                import plotly.express as px
                shifts = pd.DataFrame({'window': ['preceding 7 days', 'following 7 days'],
                                       'median': [detail.before_median.iloc[0], detail.after_median.iloc[0]]})
                st.plotly_chart(px.bar(shifts, x='window', y='median',
                                      title=f'{well} · {parameter} · retrospective event context'), key='event_context')
                st.caption('Before/after context includes future observations for explanation only; not a detector input. Missingness includes sample selection and scope edges.')
        else:
            st.info(f'Generate explanations and offline report: python -m nk_oil.cli enhance --mode {mode}')
        with st.form('review_form'):
            status = st.selectbox('Decision', STATUSES, index=STATUSES.index(current.status))
            note = st.text_area('Analyst note', current.note, max_chars=4000)
            submitted = st.form_submit_button('Save review')
        if submitted:
            review(review_db, event_id, well, status, note)
            st.rerun()
        st.download_button('Export filtered reviews CSV', visible.to_csv(index=False), 'reviews.csv', 'text/csv')
        st.download_button('Export filtered reviews JSON', visible.to_json(orient='records'), 'reviews.json', 'application/json')
