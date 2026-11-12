# Requirements traceability
Statuses are phase-specific; future features remain planned until tested.

|ID|Weight|Owner / evidence|Phase 1 status / limitation|
|---|---:|---|---|
|R1 Python functions, control flow, files, exceptions, modules|20|nk_oil/*.py, tests/test_core.py|Implemented; tests pending|
|R2 interactive UI, selectors, 5 visuals|20/15|app.py|One interactive chart; full UI planned|
|R3 normalized DB + 8 SQL incl LAG|10|database.py, database_design.md|Roundtrip implemented; eight queries planned|
|R4 chunking, dtype, Parquet, timings, size|15/10|dataset.py, cli.py|Chunking/Parquet implemented; benchmarks planned; source too small|
|R5 safe long-to-wide|15|transform.py, test_core.py|Implemented; collision rejection|
|R6 quality, flags, gaps, May/June|15|quality.py, dataset_profile.md|Basic audit implemented; issue measurements planned|
|R7 grouped EDA, patterns, coverage correlations|15|analytics.py (planned)|Planned|
|R8 official split, no leakage|15|dataset_profile.md, experiments_plan.md|Source split inspected; full validation planned|
|R9 baseline + distinct methods, fair evidence|15|methods.py (planned)|Planned; no ground truth metrics|
|R10 report, slides, reproducibility|5/10|README, docs, requirements.txt|Design docs present; final artifacts planned|
|R11 end-to-end startup and tests|10|test_core.py, Streamlit AppTest|Verification pending|

Weights overlap requirements and must not be summed. Rubric totals: software 20, data 15, DB 10, EDA 15, methods 15, reproducibility 10, report 5, defense 10 = 100.

## Phase 2 tested coverage
R1–R9 and R11 implemented/tested on real monthly sample (85,423 rows): `pipeline.py`, `analytics.py`, `quality.py`, `methods.py`, `charts.py`, `app.py`, eight `sql/queries/*.sql`; `test_analysis.py` and `test_app.py` provide invariants and UI smoke evidence. Run exports reconcile every nonnull pivot value and SQL count. Five HTML charts, quality, issue measurements and method comparisons are generated. 13 tests pass. R4 size recommendation remains unsatisfied by source; full validation pending phase 3. R10 final academic report/slides remain phase 4 work. No scientific detection accuracy claimed.

Phase 1 gate: R1/R5/R11 tested on bounded real source and synthetic unit fixtures; R3 single-query SQLite roundtrip tested. 7 tests pass. Remaining requirements stay planned as described above.
