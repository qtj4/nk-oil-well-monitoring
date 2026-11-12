import sqlite3

import pandas as pd


def connect(path):
    con = sqlite3.connect(path)
    con.execute('PRAGMA foreign_keys=ON')
    return con


def build(df, path, replace_snapshot=False):
    with connect(path) as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS wells(well_id TEXT PRIMARY KEY, well_type TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS parameters(parameter TEXT PRIMARY KEY, unit TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS observations(
          well_id TEXT REFERENCES wells, parameter TEXT REFERENCES parameters,
          timestamp TEXT, value REAL, n_obs INTEGER, flag TEXT, split TEXT,
          PRIMARY KEY(well_id,parameter,timestamp));
        CREATE INDEX IF NOT EXISTS obs_time ON observations(timestamp);
        CREATE TABLE IF NOT EXISTS flag_types(flag TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS observation_flags(
          well_id TEXT,parameter TEXT,timestamp TEXT,flag TEXT REFERENCES flag_types,
          PRIMARY KEY(well_id,parameter,timestamp,flag),
          FOREIGN KEY(well_id,parameter,timestamp) REFERENCES observations(well_id,parameter,timestamp));
        ''')
        if replace_snapshot:
            con.execute('DELETE FROM observation_flags')
            con.execute('DELETE FROM observations')
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
        con.executemany('''INSERT INTO observations VALUES (?,?,?,?,?,?,?)
ON CONFLICT(well_id,parameter,timestamp) DO UPDATE SET value=excluded.value,
n_obs=excluded.n_obs,flag=excluded.flag,split=excluded.split''',
                        rows.astype(object).where(rows.notna(), None).itertuples(index=False, name=None))
        for row in rows[rows.flag != ''].itertuples(index=False):
            con.execute('DELETE FROM observation_flags WHERE well_id=? AND parameter=? AND timestamp=?',
                        (row.well_id, row.parameter, row.timestamp))
            for flag in str(row.flag).split(';'):
                con.execute('INSERT OR IGNORE INTO flag_types VALUES (?)', (flag,))
                con.execute('INSERT OR IGNORE INTO observation_flags VALUES (?,?,?,?)',
                            (row.well_id, row.parameter, row.timestamp, flag))


def query(path, sql, params=()):
    with connect(path) as con:
        return pd.read_sql_query(sql, con, params=params)
