# 2–3 minute demo
0:00 — Open prepared sample dashboard offline; point out historical source revision, 85,423 rows and lack of verified failure labels.

0:25 — Choose NK-7 June scenario, SPM. Explain measured May/June difference in Data quality, inspect actual daily/rolling trend. Candidate markers do not prove equipment failure.

0:55 — Regime changes: contrast no-change, rolling shift and CUSUM; counts and threshold sensitivity are diagnostics, not accuracy. Source test begins Aug 8 23:00; June is training-era retrospective context.

1:20 — Review workbench: choose a candidate, inspect score and 7-day median/variance/coverage context; mark needs_investigation with a note and save. Reload to show persistence.

1:55 — SQL & reports: show LAG gaps versus nulls, then generate/download self-contained HTML diagnostic. Open offline report to show provenance, chart and analyst note.

2:30 — Mention May area scenario, possible calibration confounding, source-size exception and unverified SCADA year/timezone.

Fallback: prepared Parquet/SQLite plus `results/<run_id>/NK7_diagnostic.html`, five offline HTML figures and saved SQL exports. No internet/GPU required. If artifacts absent, `python -m nk_oil.cli prepare --mode sample` uses bundled verified sample; then `enhance --mode sample`.
