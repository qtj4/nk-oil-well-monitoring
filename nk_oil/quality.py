from .dataset import KEY


def audit(df):
    return {
        'rows': len(df), 'wells': int(df.well_id.nunique()),
        'duplicates': int(df.duplicated(KEY).sum()),
        'null_values': int(df.value.isna().sum()),
        'start': str(df.timestamp.min()), 'end': str(df.timestamp.max()),
        'flags': {str(k): int(v) for k, v in df.flag.value_counts().items()},
    }
