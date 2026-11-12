import json

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from nk_oil.config import ROOT, paths
from nk_oil.database import query
from nk_oil.events import characterize, ingest, queue, review
from nk_oil.reporting import diagnostic


@pytest.fixture
def product():
    manifest = {'run_id': 'fixture_run', 'data_hash': 'fixture_hash', 'source_revision': 'fixture_only'}
    candidates = pd.DataFrame([{'event_id': 'fixture_event', 'well_id': 'A', 'parameter': 'p',
                                'timestamp': pd.Timestamp('2026-05-08'), 'method': 'cusum', 'score': 6.,
                                'threshold': 5., 'value': 20., 'data_hash': 'fixture_hash', 'config': '{}'}])
    ts = pd.date_range('2026-05-01', periods=14 * 24, freq='h')
    data = pd.DataFrame({'well_id': 'A', 'parameter': 'p', 'unit': 'u', 'timestamp': ts,
                         'value': [10.] * 168 + [20.] * 168, 'flag': '', 'split': 'train'})
    return manifest, candidates, data


def test_review_persistence_history_and_validation(product, tmp_path):
    manifest, candidates, _ = product
    db = tmp_path / 'reviews.sqlite'
    ingest(db, candidates, manifest)
    ingest(db, candidates, manifest)
    review(db, 'fixture_event', 'A', 'needs_investigation', "O'Brien <script>alert(1)</script>")
    assert queue(db, 'fixture_run', 'A').status.tolist() == ['needs_investigation']
    assert queue(db, 'fixture_run', 'B').empty
    ingest(db, candidates, {**manifest, 'run_id': 'fixture_second_run'})
    assert queue(db, 'fixture_second_run', 'A').note.iloc[0].startswith("O'Brien")
    assert query(db, 'SELECT COUNT(*) n FROM alert_reviews').iloc[0, 0] == 1
    for event_id, well, status, note in [('fixture_event', 'B', 'confirmed', ''),
                                          ('missing', 'A', 'confirmed', ''),
                                          ('fixture_event', 'A', 'fake', ''),
                                          ('fixture_event', 'A', 'confirmed', 'x' * 4001)]:
        with pytest.raises(ValueError):
            review(db, event_id, well, status, note)
    assert query(db, 'PRAGMA foreign_key_check').empty


def test_characterization_is_retrospective_and_correct(product):
    _, candidates, data = product
    result = characterize(candidates, data)
    assert result.level_delta.iloc[0] == 10.
    assert result.before_n.iloc[0] == 168
    assert result.after_absent_or_null_fraction.iloc[0] == 0
    assert result.available_at.iloc[0] == '2026-05-09 00:00:00'
    assert result.right_censored.iloc[0]


def test_offline_report_escapes_notes(product, tmp_path):
    manifest, candidates, data = product
    db = tmp_path / 'reviews.sqlite'
    ingest(db, candidates, manifest)
    review(db, 'fixture_event', 'A', 'confirmed', '<script>unsafe()</script>')
    report = diagnostic(data, queue(db, manifest['run_id']), pd.DataFrame({'method': ['no_change']}),
                        manifest, 'A', 'p', '2026-05-01', '2026-05-15')
    for section in ['Provenance', 'Coverage', 'Sensor summaries', 'Time series', 'Data quality',
                    'analyst reviews', 'Method comparison', 'Limitations', 'fixture_hash']:
        assert section in report
    assert '<script>unsafe()</script>' not in report
    assert '&lt;script&gt;unsafe()&lt;/script&gt;' in report
    assert '<script src=' not in report
    with pytest.raises(ValueError):
        diagnostic(data.iloc[:0], candidates, pd.DataFrame(), manifest, 'A', 'p', '2026-05-01', '2026-05-15')


def test_ui_review_to_report(tmp_path, monkeypatch):
    db = tmp_path / 'ui_reviews.sqlite'
    monkeypatch.setenv('NK_REVIEW_DB', str(db))
    at = AppTest.from_file(ROOT / 'app.py', default_timeout=30).run()
    assert not at.exception
    decision = next(w for w in at.selectbox if w.label == 'Decision')
    decision.select('needs_investigation')
    next(w for w in at.text_area if w.label == 'Analyst note').set_value('Automated UI acceptance check')
    next(w for w in at.button if w.label == 'Save review').click().run()
    assert not at.exception
    run_id = (paths('sample') / 'latest_run.txt').read_text().strip()
    assert 'Automated UI acceptance check' in queue(db, run_id, 'NK-7').note.tolist()
    at.run()
    assert not at.exception
    next(w for w in at.button if w.label == 'Generate well diagnostic report').click().run()
    assert not at.exception
    assert 'Automated UI acceptance check' in at.session_state['diagnostic'][1]
    next(w for w in at.selectbox if w.label == 'Demo scenario').select('May area scale investigation').run()
    assert not at.exception
    assert next(w for w in at.selectbox if w.label == 'Well').value == 'NK-82'
    assert next(w for w in at.selectbox if w.label == 'Parameter').value == 'dynamometer_area'
    # Real evidence manifests must never contain synthetic fixtures.
    assert json.loads((ROOT / 'results' / run_id / 'run_manifest.json').read_text())['data_hash'] != 'fixture_hash'
