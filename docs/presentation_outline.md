# Storyboard / 12 slides, 5-8 minutes
Design: Arial, warm paper background, teal quantitative evidence, rust for caveats. Native editable charts/tables/diagrams; no generated field photographs. Two prototype directions compared: warm editorial (large figure, quiet annotation) versus dark technical (denser plotting). Chosen warm editorial for projection/readability and stable Office rendering. Prototype: `work/design_directions.html` in task workspace. No user template supplied; template picker unavailable.

|Slide|Purpose / key message|Actual visual / source|Notes / time|
|---|---|---|---|
|1|Historical well regime analysis|Minimal editable title|Scope and no fault labels, 15s|
|2|258,387 records, exact split|Native train/test bar chart; dataset_summary|10 wells, source year/timezone caveat, 25s|
|3|Local reproducible architecture|Native pipeline diagram; Python modules|CLI prepares, UI reads cached results, 25s|
|4|Normalized SQLite and 8 real queries|Editable schema and LAG snippet|Absent hour != NULL, 35s|
|5|Quality flags and coverage|Native table; flags/quality_report|7,041 flagged rows; 21,014 pair-hour absences, 30s|
|6|Area medians shift across pump wells|Native April/May ratio chart; known_issues|9.95-20.37x, no causal calibration claim, 35s|
|7|NK-7 lower SPM already in May|Native monthly line chart; nk7_monthly_evidence|Card approximate June narrative disagrees on onset, 40s|
|8|Causal test evaluation|Editable method definitions; manifest|Daily availability, official split, train-only fit, 35s|
|9|Candidate counts differ, accuracy unknown|Native 0/29/139 bar chart; methods_comparison|1,747 units, sensitivity, repeated CUSUM alerts, 40s|
|10|Analyst review and offline report|Editable workflow; tested UI path|Review != ground truth, stable IDs, 45s|
|11|Measured CPU resources|Native operation time chart; benchmarks|RSS methodology; no pure format speedup, 25s|
|12|Limits and defensible conclusion|Editable synthesis|Size exception, source metadata, external submission, 25s|

Every slide cites exact local producing artifacts and source URL in notes. Full run ID is embedded. Team members not provided; do not invent presenters/contributions. Detailed claim ledger: `docs/claim_ledger.md`.
