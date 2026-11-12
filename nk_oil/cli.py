import argparse
import json

from .config import MODE, ROOT, paths
from .dataset import fetch
from .pipeline import execute, load_source, run_queries
from .quality import audit
from .performance import measure


def main():
    parser = argparse.ArgumentParser(description='NK historical oil-well analytics')
    parser.add_argument('command', choices=['fetch', 'prepare', 'inspect', 'init-db', 'queries', 'analyze', 'enhance'])
    parser.add_argument('--mode', choices=['sample', 'full'], default=MODE)
    parser.add_argument('--phase1', action='store_true', help='Use bounded first source slice')
    args = parser.parse_args()
    if args.command == 'fetch':
        fetch()
        return
    target = paths(args.mode)
    try:
        if args.command == 'enhance':
            from .enhancements import enhance
            enhance(args.mode)
        elif args.command == 'inspect':
            print(json.dumps(audit(load_source(args.mode, args.phase1)), indent=2))
        elif args.command == 'queries':
            tables = run_queries(target / 'analysis.sqlite', ROOT / 'results' / f'sql_{args.mode}')
            print({name: len(table) for name, table in tables.items()})
        else:
            output, performance = measure(execute, args.mode, args.phase1)
            (output / 'whole_pipeline_benchmark.json').write_text(json.dumps(performance, indent=2))
    except (FileNotFoundError, ValueError, OSError) as exc:
        parser.exit(1, f'Cannot complete {args.command}: {exc}\n')


if __name__ == '__main__':
    main()
