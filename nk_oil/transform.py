from .dataset import KEY


def to_wide(df):
    if df.duplicated(KEY).any():
        raise ValueError('Duplicate well/timestamp/parameter; refusing ambiguous pivot')
    return df.pivot(index=['well_id', 'timestamp'], columns='parameter', values='value').reset_index()
