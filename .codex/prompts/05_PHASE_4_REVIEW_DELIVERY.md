# Codex Phase 4 — senior review, cleanup, report, presentation and defense readiness

**Execution mode:** read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md` first. Operate independently: do not ask the user questions; inspect, decide, implement, test, fix and document. Record unavoidable blockers instead of stopping.

Read shared contract and the complete repository including phase 2.5 product/ML enhancements and phase 3 results. Act simultaneously as an independent rubric grader, QA tester, data-science reviewer, data engineer and technical editor. Your job is to **find real gaps and fix them**, not to congratulate the author. Do not delete valuable results or rewrite working modules without justification.

## 1. Independent compliance audit
Reconstruct grading against the official rubric weights: implementation 20, preprocessing 15, DB/SQL 10, EDA/visualization 15, comparison 15, code/reproducibility 10, report 5, presentation 10. For each requirement 1–11 and cluster-specific requirement, list exact code paths, tests, generated evidence and proof it works; distinguish implemented/not tested/verified. Specifically inspect:
- Python-only application and at least 5 useful functions, structures, branching, loops, real file IO, exception handling, modular imports;
- Streamlit interactivity, well/parameter/period selection and >=4–5 informative charts including interactive one;
- normalized SQLite schema, ER diagram, eight executable diverse SQL queries with JOIN/HAVING/CTE/window `LAG`, and Pandas roundtrip;
- chunked ingest, dtype optimizations, Parquet and measured memory/time; actual row count/size;
- long→wide correctness, gaps/quality flags, documented May-2026 dynamometer scaling and NK-7 June-2026 regime transition;
- type-wise EDA, daily pattern and correlations;
- train/test chronological integrity, baseline + two methods and valid comparison metrics; no leakage or fictional labels;
- source data provenance, dependencies/version pins, CLI/readme freshness, clean repo.

Make a table in `docs/final_audit.md` with criterion, expected maximum, supported score range (heuristic only, not an instructor score), evidence, impact and fix. Prioritize blockers and correct them. Do not report grade 100 without demonstrated rubric evidence.

## 2. Product extension review (Phase 2.5)
Check real persistence of analyst alert reviews, consistent event/run provenance, safe SQLite queries, the offline downloadable diagnostic report, clear historical-data labeling and validity/limitations of any additional ML experiment. These are bonus extensions, not substitutes for mandatory requirements and not guaranteed extra rubric points. Include the end-to-end review-to-report workflow in the defense script only if actually implemented and tested.

## 3. Reliability + clean code review
Check clean-environment install and demo from README; app and tests on CPU; identify dead files, duplicate logic, slow Pandas patterns, unsafe resource use, paths that only work on author's machine, inconsistent date handling and SQLite index issues. Fix bugs, improve types/docstrings/names, simplify overly complex abstractions. Add targeted tests for regression and boundary conditions. Avoid destructive formatting/reorganizing late in project unless necessary. Prevent accidental Git commits of huge data, `.env`, API tokens or databases.

## 3. Scientific validity review
Inspect actual generated tables and figures, cross-check numbers against source/manifests, reconcile counts between long/wide and SQL, expose missing records and seasonal/operational confounders. Critically assess May scale shift, June operational change, lack of labels and ambiguity of detector alerts. Revisit model comparisons for fair evaluation and test leakage; rerun targeted experiments only if necessary. Maintain provenance and uncertainty. Do not invent causal interpretations or field-grounded recommendations beyond evidence.

## 4. Produce final documents IN THE REPOSITORY
A. `README.md` usable by an independent lecturer: purpose; dataset credit and link/license; architecture; prerequisites; install with pinned `requirements.txt`; get data; sample-mode smoke run; full run; DB+8 SQL; dashboard; methods; test commands; reproducibility; limitations; typical errors.
B. `docs/final_report.md` with full academic report: abstract, problem definition, dataset and legitimacy, research questions, methods, database/ER and SQL, preprocessing, data quality and known issues, baseline + 2 methods, split and metrics, results tables/plots, performance, interpretation, limitations and conclusions; citations. Only use **actual measured** numbers.
C. `docs/presentation_outline.md` (~8–12 coherent slides depending on professor time): problem and relevance; data source/types; system architecture; data quality + known anomalies; SQLite/SQL; EDA; regime-change approach; baseline vs two methods/results; live dashboard demonstration; limitations/conclusion. Each slide: title, key message, appropriate actual graphic, short speaker notes. Avoid empty word-cloud slides.
D. Generate actual `deliverables/final_report.pdf` and `deliverables/final_presentation.pptx` **if available tooling permits**; otherwise leave complete Markdown/slide content, provide exact generation commands and state missing outputs honestly. Presentation may also be PDF per syllabus. Do not claim generated artifacts without file checks.
E. `docs/defense_guide.md`: 5–8 minute coherent demonstration script (adjust if known), plain-language concepts (pivot, SQL LAG, baseline, rolling z-score, change point, chronological split, data leakage), 12–20 likely professor questions and precise answers, a fallback demo when internet/GPU is unavailable.
F. Team contribution sections for 2–3 students **only if actual team members and real contributions are known**; leave explicit placeholders otherwise, not fabricated names or workload shares.
G. `docs/submission_checklist.md`: GitHub public/private sharing decision, source push status, Git history, exact dataset access, Moodle submission of report/presentation at least 2–3 days before exam (ask for actual deadline; do not invent it), teacher approval/status, file checklist.

## 5. Final validation and response
Execute test suite, SQL runner, CLI sample pipeline and dashboard smoke checks as feasible. Verify at least the smallest end-to-end demonstration works **offline** with predownloaded real sample or explicitly labeled demo data. Confirm report figures/tables match `results/<run_id>` and every chart has a data source. Save checklist and audit evidence. Give a clear pass/fail scorecard, missing/blocked items and commands. If anything remains incomplete, distinguish true blockers from optional polish; do not silently claim compliance.

## Definition of done
A fresh reviewer can install, run, explain and demonstrate the project using the documents, and can trace every major result to data/code. The final hand-in files exist or remaining generation constraints are explicitly documented.
