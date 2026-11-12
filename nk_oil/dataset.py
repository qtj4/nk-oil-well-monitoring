import hashlib
import json
import time
import urllib.request

import numpy as np
import pandas as pd

from .config import ROOT, SOURCE

KEY = ['well_id', 'timestamp', 'parameter']
COLUMNS = ['well_id', 'well_type', 'timestamp', 'parameter', 'value', 'unit', 'n_obs', 'flag']


def validate(frame):
    missing = set(COLUMNS) - set(frame)
    if missing:
        raise ValueError(f'Missing source columns: {sorted(missing)}')
    df = frame[COLUMNS + (['split'] if 'split' in frame else [])].copy()
    df['timestamp'] = pd.to_datetime(df.timestamp, format='ISO8601', errors='raise')
    if df[KEY + ['well_type', 'unit']].isna().any().any():
        raise ValueError('Null observation identity or metadata')
    if df.timestamp.dt.tz is not None:
        raise ValueError('Expected source naive timestamps; timezone is undocumented')
    if not set(df.well_type).issubset({'fountain', 'sucker_rod_pump'}):
        raise ValueError('Unknown well type')
    df['value'] = pd.to_numeric(df.value, errors='raise')
    if np.isinf(df.value).any():
        raise ValueError('Infinite sensor value')
    df['flag'] = df.flag.fillna('')
    df['n_obs'] = pd.to_numeric(df.n_obs, errors='raise').astype('int32')
    if (df.n_obs < 1).any():
        raise ValueError('n_obs must be positive')
    for col in ['well_id', 'well_type', 'parameter', 'unit', 'flag']:
        df[col] = df[col].astype('category')
    return df.sort_values(KEY).reset_index(drop=True)


def read_csv(path, sample=False):
    if not path.exists():
        raise FileNotFoundError(f'{path} unavailable. Run: python -m nk_oil.cli fetch')
    parts = []
    for chunk in pd.read_csv(path, chunksize=25000):
        if sample:
            ts = pd.to_datetime(chunk.timestamp, errors='raise')
            # 10 contiguous days/month include May 8 and support detector warmup.
            chunk = chunk[ts.dt.day <= 10]
        if not chunk.empty:
            parts.append(chunk)
    return validate(pd.concat(parts, ignore_index=True)) if parts else validate(pd.DataFrame(columns=COLUMNS))


def fingerprint(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fetch():
    raw = ROOT / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((raw / 'source_metadata.json').read_text())
    revision = metadata['sha']
    for name in ['train.csv', 'test.csv']:
        target = raw / name
        if target.exists():
            continue
        for attempt in range(3):
            try:
                with urllib.request.urlopen(f'{SOURCE}/resolve/{revision}/{name}', timeout=60) as r:
                    with open(target.with_suffix('.part'), 'wb') as out:
                        count = 0
                        while block := r.read(1024 * 1024):
                            count += len(block)
                            if count > 30_000_000:
                                raise ValueError('Download exceeds documented resource budget')
                            out.write(block)
                target.with_suffix('.part').replace(target)
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(attempt + 1)
