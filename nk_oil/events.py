import json
from datetime import datetime, timezone

import pandas as pd

from .database import connect, query

STATUSES = ['unreviewed', 'confirmed', 'dismissed', 'needs_investigation']


def migrate(path):
    with connect(path) as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS schema_versions(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_versions VALUES (1);
        CREATE TABLE IF NOT EXISTS analysis_runs(run_id TEXT PRIMARY KEY,data_hash TEXT NOT NULL,manifest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
          event_id TEXT PRIMARY KEY,well_id TEXT NOT NULL,parameter TEXT NOT NULL,timestamp TEXT NOT NULL,
          method TEXT NOT NULL,score REAL,threshold REAL,value REAL,data_hash TEXT NOT NULL,config TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS event_lookup ON events(well_id,timestamp,method);
        CREATE TABLE IF NOT EXISTS event_runs(
          event_id TEXT REFERENCES events,run_id TEXT REFERENCES analysis_runs,PRIMARY KEY(event_id,run_id));
        CREATE TABLE IF NOT EXISTS alert_reviews(
          event_id TEXT PRIMARY KEY REFERENCES events,status TEXT NOT NULL
          CHECK(status IN ('unreviewed','confirmed','dismissed','needs_investigation')),
          note TEXT NOT NULL,updated_utc TEXT NOT NULL);
        ''')


def ingest(path, events, manifest):
    migrate(path)
    with connect(path) as con:
        con.execute('INSERT OR IGNORE INTO analysis_runs VALUES (?,?,?)',
                    (manifest['run_id'], manifest['data_hash'], json.dumps(manifest, sort_keys=True)))
        for row in events.itertuples(index=False):
            con.execute('INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?,?,?,?)',
                        (row.event_id, row.well_id, row.parameter, str(row.timestamp), row.method,
                         row.score, row.threshold, row.value, row.data_hash, row.config))
            con.execute('INSERT OR IGNORE INTO event_runs VALUES (?,?)', (row.event_id, manifest['run_id']))


def review(path, event_id, well_id, status, note):
    if status not in STATUSES:
        raise ValueError('Invalid review status')
    if not isinstance(note, str) or len(note) > 4000 or '\x00' in note:
        raise ValueError('Note must contain at most 4000 characters and no NUL')
    with connect(path) as con:
        row = con.execute('SELECT well_id FROM events WHERE event_id=?', (event_id,)).fetchone()
        if row is None or row[0] != well_id:
            raise ValueError('Event does not belong to the selected well')
        con.execute('''INSERT INTO alert_reviews VALUES (?,?,?,?) ON CONFLICT(event_id)
DO UPDATE SET status=excluded.status,note=excluded.note,updated_utc=excluded.updated_utc''',
                    (event_id, status, note.strip(), datetime.now(timezone.utc).isoformat()))


def queue(path, run_id, well_id=None):
    sql = '''SELECT e.*,COALESCE(r.status,'unreviewed') status,COALESCE(r.note,'') note,r.updated_utc
FROM events e JOIN event_runs er USING(event_id) LEFT JOIN alert_reviews r USING(event_id)
WHERE er.run_id=?'''
    params = [run_id]
    if well_id:
        sql += ' AND e.well_id=?'
        params.append(well_id)
    return query(path, sql + ' ORDER BY e.timestamp,e.parameter,e.method', params)


def characterize(events, data):
    """Retrospective context only; never fed into candidate detection or fitted models."""
    rows = []
    for event in events.itertuples():
        group = data[(data.well_id == event.well_id) & (data.parameter == event.parameter)]
        at = pd.Timestamp(event.timestamp)
        before = group[(group.timestamp >= at - pd.Timedelta(days=7)) & (group.timestamp < at)]
        after = group[(group.timestamp >= at) & (group.timestamp < at + pd.Timedelta(days=7))]
        a, b = before.value.dropna(), after.value.dropna()
        delta = b.median() - a.median()
        later = events[(events.well_id == event.well_id) & (events.parameter == event.parameter)
                       & (events.method == event.method) & (pd.to_datetime(events.timestamp) > at)]
        next_time = pd.to_datetime(later.timestamp).min() if len(later) else group.timestamp.max()
        rows.append({'event_id': event.event_id, 'well_id': event.well_id, 'parameter': event.parameter,
                     'timestamp': str(at), 'method': event.method, 'before_n': len(a), 'after_n': len(b),
                     'before_median': a.median(), 'after_median': b.median(), 'level_delta': delta,
                     'before_std': a.std(), 'after_std': b.std(),
                     'standardized_delta': delta / a.std() if len(a) > 1 and a.std() > 0 else None,
                     'before_flag_density': float((before.flag != '').mean()) if len(before) else None,
                     'after_flag_density': float((after.flag != '').mean()) if len(after) else None,
                     'before_absent_or_null_fraction': 1 - len(a) / 168,
                     'after_absent_or_null_fraction': 1 - len(b) / 168,
                     'days_to_next_candidate_or_scope_end': max((next_time - at).total_seconds() / 86400, 0),
                     'right_censored': later.empty,
                     'possible_scale_artifact': event.parameter == 'dynamometer_area' and at.month == 5,
                     'available_at': str(at + pd.Timedelta(days=1)),
                     'context': '7-day retrospective; selection/scope truncation counts as absent; not a label'})
    return pd.DataFrame(rows)
