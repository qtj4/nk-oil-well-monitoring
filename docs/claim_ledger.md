# Claims and rubric map
All quantitative results are original computations from actual pinned source. No simulated findings or invented uncertainty bars.

|ID / slides|Claim|Exact evidence|Unit / uncertainty / boundary|
|---|---|---|---|
|C1 / 1-2|258,387 rows, 10 wells; official split|dataset_summary.json, pinned source card|Hourly parameter rows; assigned source year|
|C2 / 3|All numeric pivot cells reconcile|pipeline.execute merge invariant; summary.reconciled_nonnull_values|Includes zeros; no cross-well merge|
|C3 / 4|8 actual SQLite queries return Pandas|sql/queries, phase3_sql.txt; test_analysis|Tested SQLite version in manifest|
|C4 / 5|7,041 flagged rows, no NULL, 21,014 absent pair-hours|summary.flags; quality_report.absent_slots|Internal pair endpoints, not shared downtime|
|C5 / 6|April→May area ratios 9.95-20.37|known_issues.csv|Monthly median ratios; source windows differ; cause unverified|
|C6 / 7|NK-7 lower SPM visible in May|nk7_monthly_evidence.csv|Monthly median; exact onset cannot be dated|
|C7 / 8|Frozen train normalization, causal test histories|methods.py, test_analysis leakage tests|Training events retrospective; daily value available next day|
|C8 / 9|0/29/139 test candidates, 1,747 units|methods_comparison.csv|Counts, no accuracy; repeated CUSUM alerts possible|
|C9 / 10|Persistent review and offline report|events.py/reporting.py; test_product|Human opinion, not official truth; local user only|
|C10 / 11|9.0366 s pipeline, 277.59 MB sampled RSS|whole_pipeline_benchmark.json|10-ms polling may miss peaks; baseline included|
|C11 / 11|21 tests in original and fresh env|phase4_tests.txt, phase4_clean_env_tests.txt|Executed tests; not proof of field validity|
|C12 / 12|Size and missing labels limit inference|source metadata and card; assumptions_and_blockers|Instructor exception and independent expert labels external|

Source artifact folder: results/20261112T171150743233Z_full/. Source URL/revision in report and every slide notes. Slide numerical chart data round to 6 decimals solely for portable Excel workbook precision; exact CSVs are retained.

Rubric coverage: software slides 3/10; preprocessing 2/3/5; database 4; EDA 5/6/7; methods 8/9; reproducibility 11; report final_report.pdf; defense whole deck/guide. Supported status and heuristic score boundaries: final_audit.md.
