from streamlit.testing.v1 import AppTest
from nk_oil.config import ROOT


def test_app_startup():
    at = AppTest.from_file(ROOT / 'app.py', default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.startswith('NK Well Monitoring')
    assert len(at.tabs) >= 6
    next(w for w in at.selectbox if w.label == 'Well').select('NK-75').run()
    assert not at.exception
    next(w for w in at.selectbox if w.label == 'Parameter').select('line_pressure').run()
    assert not at.exception
    for name in ['04_gaps', '08_latest']:
        next(w for w in at.selectbox if w.label == 'Analytical SQL').select(name).run()
        assert not at.exception
