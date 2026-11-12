import argparse
import json

from .config import ROOT, paths
from .database import build, query
from .dataset import fetch, read_csv
from .quality import audit
from .transform import to_wide


def main():
    parser = argparse.ArgumentParser(description='NK historical oil-well analytics')
    parser.add_argument('command', choices=['fetch', 'prepare', 'inspect', 'init-db'])
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample')
    parser.add_argument('--phase1', action='store_true', help='Use bounded first source slice')
    args = parser.parse_args()
    if args.command == 'fetch':
        fetch()
        return
    target = paths(args.mode)
    source = ROOT / 'data/sample/phase1_source.csv'
    df = read_csv(source)
    report = audit(df)
    print(json.dumps(report, indent=2))
    if args.command != 'inspect':
        df.to_parquet(target / 'long.parquet', index=False)
        to_wide(df).to_parquet(target / 'wide.parquet', index=False)
        build(df, target / 'analysis.sqlite')
        report['sql_rows'] = int(query(target / 'analysis.sqlite', 'SELECT COUNT(*) n FROM observations').iloc[0, 0])
        (target / 'quality.json').write_text(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
