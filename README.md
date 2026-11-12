# NK Well Monitoring & Regime Review
Historical educational research using NK Oil Well Sensor Monitoring v2. Data provider: Galaz and Company LLP; dataset author: Arailym Tleubayeva. Source and limitations: `docs/dataset_profile.md`.

Windows PowerShell, from project root:
```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m nk_oil.cli prepare --phase1
./.venv/Scripts/python.exe -m pytest
./.venv/Scripts/python.exe -m streamlit run app.py
```
Use the venv's Python on platforms where `python` is an alias. Defaults are CPU/sample mode. No GPU is required or claimed. Tests use clearly synthetic fixtures; research results use actual source records. No production control or validated fault prediction.

Read `docs/requirements_traceability.md`, `docs/handoff.md` and `docs/assumptions_and_blockers.md` for coverage and external dependencies.
