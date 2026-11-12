import argparse
import json

from .config import ROOT, paths
from .dataset import fetch
from .pipeline import execute, load_source, run_queries
from .quality import audit


def main():
    parser = argparse.ArgumentParser(description='NK historical oil-well analytics')
    parser.add_argument('command', choices=['fetch', 'prepare', 'inspect', 'init-db', 'queries', 'analyze'])
    parser.add_argument('--mode', choices=['sample', 'full'], default='sample')
    parser.add_argument('--phase1', action='store_true', help='Use bounded first source slice')
    args = parser.parse_args()
    if args.command == 'fetch':
        fetch()
        return
    target = paths(args.mode)
    try:
        if args.command == 'inspect':
            print(json.dumps(audit(load_source(args.mode, args.phase1)), indent=2))
        elif args.command == 'queries':
            tables = run_queries(target / 'analysis.sqlite', ROOT / 'results' / f'sql_{args.mode}')
            print({name: len(table) for name, table in tables.items()})
        else:
            execute(args.mode, args.phase1)
    except (FileNotFoundError, ValueError, OSError) as exc:
        parser.exit(1, f'Cannot complete {args.command}: {exc}\n')


if __name__ == '__main__':
    main()
