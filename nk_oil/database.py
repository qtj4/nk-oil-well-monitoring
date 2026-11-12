import sqlite3

import pandas as pd


def connect(path):
    con = sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys=ON')
    return con


def build(df, path):
    with connect(path) as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS wells(well_id TEXT PRIMARY KEY, well_type TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS parameters(parameter TEXT PRIMARY KEY, unit TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS observations(
          well_id TEXT REFERENCES wells, parameter TEXT REFERENCES parameters,
          timestamp TEXT, value REAL, n_obs INTEGER, flag TEXT, split TEXT,
          PRIMARY KEY(well_id,parameter,timestamp));
        CREATE INDEX IF NOT EXISTS obs_time ON observations(timestamp);
        ''')
        for col, table, fields in [('well_id', 'wells', ['well_id', 'well_type']),
                                   ('parameter', 'parameters', ['parameter', 'unit'])]:
            dim = df[fields].drop_duplicates()
            if dim[col].duplicated().any():
                raise ValueError(f'Conflicting {table} metadata')
            con.executemany(f'INSERT OR IGNORE INTO {table} VALUES (?,?)', dim.itertuples(index=False, name=None))
        rows = df.copy()
        rows['timestamp'] = rows.timestamp.dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'split' not in rows:
            rows['split'] = 'train'
        rows = rows[['well_id', 'parameter', 'timestamp', 'value', 'n_obs', 'flag', 'split']]
        con.executemany('INSERT OR REPLACE INTO observations VALUES (?,?,?,?,?,?,?)',
                        rows.astype(object).where(rows.notna(), None).itertuples(index=False, name=None))


def query(path, sql, params=()):
    with connect(path) as con:
        return pd.read_sql_query(sql, con, params=params)
