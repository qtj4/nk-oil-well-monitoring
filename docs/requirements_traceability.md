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

## Phase 2.5
P0 A/B/C and P1 option 2 verified: `events.py`, `reporting.py`, `enhancements.py`, integrated `app.py`; `test_product.py` tests persistence/idempotence/history/status validation/well ownership, report sections/escaping/offline chart assets and UI review→reload→report/preset selection. 17 total tests pass. Real characterization CSV and measured costs exported. Strengthens software (20), methods interpretation (15), reproducibility (10), defense (10), without exceeding rubric maxima or replacing mandatory features. Full-data testing remains phase 3.

## Phase 3
R1–R9/R11 verified on full source with `test_full.py`, all prior tests and `results/phase3_*` logs. Reproduced run `20261112T171150743233Z_full`: 258,387 rows; pivot/SQLite counts reconcile; source file hashes verify; all seven UI tabs/filter/report paths run. 19 total tests. `docs/full_data_validation.md` records exact measured costs and source-card discrepancy for NK-7 May onset. R4 only size recommendation remains externally unresolved. R10 final report/slides and objective delivery audit remain phase 4. No GPU use, official ground truth or public submission claimed.

## Phase 4 final gate
R1–R11 final status: core implementation/full-data/sample/product paths tested; R10 now has actual 9-page PDF, 12-slide editable PPTX, presentation PDF, Markdown and defense guide. 21 tests pass in original and fresh venv; pip check and Ruff pass. Offline bundled source and no-Git archives covered. Actual Streamlit server started on localhost:8501. Artifacts rendered/visually reviewed with Poppler and PowerPoint; native text edit/save/reopen test passed, final text-fit warnings empty. `docs/final_audit.md` lists honest rubric ranges and remaining external conditions; `docs/artifact_qa.md` records authoring/QA limits. R4 source-size recommendation is unresolved externally; teacher approval/team/deadline/Moodle are not fabricated. GitHub restricted to verified qtj4; private repository created, push tracked in submission checklist.

Phase 1 gate: R1/R5/R11 tested on bounded real source and synthetic unit fixtures; R3 single-query SQLite roundtrip tested. 7 tests pass. Remaining requirements stay planned as described above.
