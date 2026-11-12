import importlib.metadata
import json
import platform
import sqlite3
import subprocess
from datetime import datetime, timezone

import pandas as pd

from .analytics import known_issues, summaries, daily_patterns, nk7_monthly
from .charts import figures
from .config import ROOT, CUTOFF, paths
from .database import build, query
from .dataset import read_csv, fingerprint, KEY
from .methods import compare, daily_data, detect
from .performance import measure
from .quality import audit, coverage
from .transform import to_wide


def git_revision():
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else 'unavailable (source archive)'
    except OSError:
        return 'unavailable (git not installed)'


def load_source(mode, phase1=False):
    if phase1:
        return read_csv(ROOT / 'data/sample/phase1_source.csv')
    cached = ROOT / 'data/sample/monthly_source.parquet'
    if mode == 'sample' and not (ROOT / 'data/raw/train.csv').exists() and cached.exists():
        from .dataset import validate
        return validate(pd.read_parquet(cached))
    frames = []
    for split in ['train', 'test']:
        df = read_csv(ROOT / f'data/raw/{split}.csv', sample=mode == 'sample')
        df['split'] = split
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True).sort_values(KEY).reset_index(drop=True)
    if combined.empty:
        raise ValueError('No rows selected')
    if combined.duplicated(KEY).any():
        raise ValueError('Duplicate observation identity across source files')
    if not (combined[combined.split == 'train'].timestamp < pd.Timestamp(CUTOFF)).all():
        raise ValueError('Source train split boundary violated')
    if not (combined[combined.split == 'test'].timestamp >= pd.Timestamp(CUTOFF)).all():
        raise ValueError('Source test split boundary violated')
    return combined


def run_queries(db, output=None):
    tables = {}
    for sql in sorted((ROOT / 'sql/queries').glob('*.sql')):
        tables[sql.stem] = query(db, sql.read_text())
        if output:
            output.mkdir(parents=True, exist_ok=True)
            tables[sql.stem].to_csv(output / f'{sql.stem}.csv', index=False)
    return tables


def execute(mode, phase1=False):
    target = paths(mode)
    now = datetime.now(timezone.utc)
    run_id = now.strftime('%Y%m%dT%H%M%S%fZ') + '_' + mode
    output = ROOT / 'results' / run_id
    output.mkdir(parents=True)
    benchmarks = []
    df, perf = measure(load_source, mode, phase1)
    benchmarks.append({'operation': 'chunked_csv_ingest_validation', **perf})
    if 'split' not in df:
        df['split'] = 'train'
    wide, perf = measure(to_wide, df)
    benchmarks.append({'operation': 'long_to_wide', **perf})
    # Reconcile all nonnull numeric cells with the original grain.
    melted = wide.melt(id_vars=['well_id', 'timestamp'], var_name='parameter').dropna(subset='value')
    original = df.dropna(subset='value')[KEY + ['value']]
    reconciled = original.merge(melted, on=KEY, suffixes=('_long', '_wide'), validate='one_to_one')
    if len(reconciled) != len(original) or not (reconciled.value_long == reconciled.value_wide).all():
        raise ValueError('Pivot reconciliation failed')
    df.to_parquet(target / 'long.parquet', index=False)
    if mode == 'sample' and not phase1:
        df.to_parquet(ROOT / 'data/sample/monthly_source.parquet', index=False)
    wide.to_parquet(target / 'wide.parquet', index=False)
    _, perf = measure(build, df, target / 'analysis.sqlite', replace_snapshot=True)
    benchmarks.append({'operation': 'sqlite_upsert', **perf})
    sql, perf = measure(run_queries, target / 'analysis.sqlite', output / 'sql')
    benchmarks.append({'operation': 'eight_sql_queries_pandas', **perf})
    reread, perf = measure(pd.read_parquet, target / 'long.parquet')
    benchmarks.append({'operation': 'parquet_read', **perf})
    assert len(reread) == len(df)
    data_hash = fingerprint(target / 'long.parquet')
    summary = audit(df)
    summary.update({'mode': mode, 'sample_selection': 'first 10 days of each month' if mode == 'sample' else 'all source rows',
                    'train_rows': int((df.split == 'train').sum()), 'test_rows': int((df.split == 'test').sum()),
                    'long_memory_mb': float(df.memory_usage(deep=True).sum() / 1e6),
                    'wide_rows': len(wide), 'reconciled_nonnull_values': len(reconciled),
                    'sql_rows': int(sql['01_coverage'].records.sum()),
                    'parquet_bytes': (target / 'long.parquet').stat().st_size,
                    'source_bytes': sum((ROOT / f'data/raw/{s}.csv').stat().st_size for s in ['train', 'test'])
                    if not phase1 and all((ROOT / f'data/raw/{s}.csv').exists() for s in ['train', 'test'])
                    else (ROOT / 'data/sample/phase1_source.csv').stat().st_size if phase1
                    else (ROOT / 'data/sample/monthly_source.parquet').stat().st_size,
                    'missing_slot_note': 'Sample gaps include intentionally excluded dates' if mode == 'sample' else 'Source missing hours',
                    'timezone': 'naive; undocumented by provider'})
    (output / 'dataset_summary.json').write_text(json.dumps(summary, indent=2))
    (target / 'quality.json').write_text(json.dumps(summary, indent=2))
    coverage(df).to_csv(output / 'quality_report.csv', index=False)
    known_issues(df).to_csv(output / 'known_issues.csv', index=False)
    nk7_monthly(df).to_csv(output / 'nk7_monthly_evidence.csv', index=False)
    summaries(df).to_csv(output / 'descriptive_statistics.csv', index=False)
    daily_patterns(df).to_csv(output / 'daily_patterns.csv', index=False)
    events, comparison, daily = compare(df, data_hash)
    events.to_csv(output / 'events.csv', index=False)
    comparison.to_csv(output / 'methods_comparison.csv', index=False)
    daily.to_parquet(output / 'daily.parquet', index=False)
    for multiplier in [.8, 1.2]:
        pd.concat([detect(daily, method, data_hash, multiplier) for method in ['no_change', 'rolling_shift', 'cusum']])\
            .to_csv(output / f'events_threshold_{int(multiplier * 100)}.csv', index=False)
    for scope, include_area, clean in [('area_included', True, True), ('flags_retained', False, False)]:
        sensitivity = daily_data(df, include_area=include_area, clean=clean)
        for method in ['rolling_shift', 'cusum']:
            detected = detect(sensitivity, method, data_hash)
            detected.to_csv(output / f'sensitivity_{scope}_{method}.csv', index=False)
    figs, pairs = figures(df, 'NK-7', 'SPM')
    for name, fig in figs.items():
        fig.write_html(output / f'{name}.html', include_plotlyjs=True)
    pairs.to_csv(output / 'correlation_pair_counts.csv')
    pd.DataFrame(benchmarks).to_csv(output / 'processing_benchmarks.csv', index=False)
    metadata = json.loads((ROOT / 'data/raw/source_metadata.json').read_text())
    manifest = {'run_id': run_id, 'generated_utc': now.isoformat(), 'mode': mode,
                'data_hash': data_hash, 'source_revision': metadata['sha'],
                'source_hashes': {s: fingerprint(ROOT / f'data/raw/{s}.csv') for s in ['train', 'test']}
                if not phase1 and all((ROOT / f'data/raw/{s}.csv').exists() for s in ['train', 'test'])
                else {'cached_slice': fingerprint(ROOT / 'data/sample/phase1_source.csv' if phase1 else
                                                  'data/sample/monthly_source.parquet')},
                'commit': git_revision(),
                'code_hashes': {str(p.relative_to(ROOT)): fingerprint(p)
                                for p in [ROOT / 'app.py', *sorted((ROOT / 'nk_oil').glob('*.py')),
                                          *sorted((ROOT / 'sql/queries').glob('*.sql'))]},
                'python': platform.python_version(), 'platform': platform.platform(), 'sqlite': sqlite3.sqlite_version,
                'packages': {name: importlib.metadata.version(name) for name in ['pandas', 'numpy', 'pyarrow', 'streamlit', 'plotly']},
                'cutoff': CUTOFF, 'excluded_daily_bin': '2026-08-08', 'random_seed': 0,
                'gpu_used': False, 'config': {'daily_min_records': 12, 'rolling_days': 3, 'cooldown_days': 7,
                                             'rolling_threshold': 3, 'cusum_threshold': 5, 'cusum_drift': .5},
                'memory_measurement': '10 ms process RSS polling; absolute peak includes runtime; may miss short peaks'}
    (output / 'run_manifest.json').write_text(json.dumps(manifest, indent=2))
    (target / 'latest_run.txt').write_text(run_id)
    (output / 'findings.md').write_text(
        f'# Measured run {run_id}\n\n{summary["rows"]:,} source rows; {summary["wells"]} wells. '
        f'{summary["train_rows"]:,} train and {summary["test_rows"]:,} test records. '
        'All eight SQL queries ran and pivot numeric values reconciled exactly. '
        'Known-issue evidence: known_issues.csv. Methods: methods_comparison.csv. '
        'No supervised accuracy is identifiable without ground truth. '
        'Sample selection gaps are not source outages. Area is excluded from main detector runs; '
        'sensitivity exports retain it or retain flags. '
        'Training-era events use training-wide reference statistics and are descriptive; only test-era events '
        'support frozen-reference temporal evaluation. No physical cause is established.\n')
    print(json.dumps({'run_id': run_id, 'rows': len(df), 'output': str(output)}, indent=2))
    return output
