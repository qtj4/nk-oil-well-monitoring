import json

import pandas as pd

from .config import ROOT, paths
from .events import characterize, ingest, queue
from .performance import measure
from .reporting import diagnostic


def enhance(mode):
    target = paths(mode)
    run = (target / 'latest_run.txt').read_text().strip()
    output = ROOT / 'results' / run
    manifest = json.loads((output / 'run_manifest.json').read_text())
    data = pd.read_parquet(target / 'long.parquet')
    candidates = pd.read_csv(output / 'events.csv', parse_dates=['timestamp'])
    review_db = ROOT / 'data/reviews.sqlite'
    ingest(review_db, candidates, manifest)
    explanations, perf = measure(characterize, candidates, data)
    explanations.to_csv(output / 'event_characterization.csv', index=False)
    (output / 'characterization_benchmark.json').write_text(json.dumps(perf, indent=2))
    comparison = pd.read_csv(output / 'methods_comparison.csv')
    report = diagnostic(data, queue(review_db, run, 'NK-7'), comparison, manifest,
                        'NK-7', 'SPM', '2026-05-01', '2026-07-01')
    (output / 'NK7_diagnostic.html').write_text(report, encoding='utf-8')
    print(f'Indexed {len(candidates)} candidate events for {run}; characterization and offline HTML report saved.')
