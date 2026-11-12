import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODE = os.getenv('DATA_MODE', 'sample')
CUTOFF = '2026-08-08 23:00:00'
SOURCE = 'https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2'


def paths(mode=MODE):
    if mode not in {'sample', 'full'}:
        raise ValueError('DATA_MODE must be sample or full')
    target = ROOT / 'data' / 'processed' / mode
    target.mkdir(parents=True, exist_ok=True)
    return target
