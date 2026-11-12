from streamlit.testing.v1 import AppTest
from nk_oil.config import ROOT


def test_app_startup():
    at = AppTest.from_file(ROOT / 'app.py', default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value.startswith('NK Well Monitoring')
