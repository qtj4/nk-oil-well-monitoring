# Codex Phase 2 — complete application under weak-laptop constraints

**Execution mode:** read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md` first. Operate independently: do not ask the user questions; inspect, decide, implement, test, fix and document. Record unavoidable blockers instead of stopping.

Read `01_SHARED_CONTRACT.md`, prior handoff and existing repo. Implement **the complete required product**. Keep full-data processing optional; sample mode must run without GPU, without cloud, and without exhausting RAM. Do not defer UI, SQL, EDA, method implementations or tests to phase 3.

## 1. Real ingestion and memory-safe preprocessing
- Implement dataset load from cached local source or official URL, with explicit download instructions, chunking for CSV, selective columns/partitions for Parquet, path portability and controlled retries/errors.
- Validate canonical schema; sort and parse timestamps with explicit timezone assumptions; detect duplicates by actual grain and document deterministic collision handling; normalize well types based on observed labels, not invented types.
- Long→wide transformation by timestamp/well/parameter; demonstrate roundtrip or value reconciliation; no cross-well or time-bucket mixing; keep raw values available for audit.
- Stream results to Parquet using partitioning or chunks where appropriate; optimize dtypes without changing meaning; record dataset shape, memory baseline, output sizes and elapsed timings. Use CPU-light sample selection that remains chronological, representative and explicitly lists included/excluded wells/periods.
- Handle known `dynamometer_area` May-2026 scale shift and NK-7 June-2026 regime change carefully: measure before/after from data, flag possible measurement artifacts separately from genuine operating change, avoid hardcoded unverified correction factors; provide optional sensitivity experiments.

## 2. Quality and EDA
Build a reusable quality report (JSON/CSV/Parquet or tables) showing nulls, duplicates, `flag` distribution/meaning when documented, invalid records, period coverage, temporal gaps, outliers, per-well/per-parameter impacts. Clearly separate timestamp gaps detected by `LAG` from records with NULL values and nonuniform sampling frequency. Never treat planned operating changes as data errors without justification.

Analyze fountain vs sucker_rod_pump wells: per-group/per-well descriptive stats, timelines and daily periodicity, coverage-aware correlations, changes before/after important date boundaries. Use observed columns. Generate **at least five** high-quality charts (e.g. interactive time series with annotated change points, well-type distribution comparison, daily pattern, correlation heatmap, missingness/quality matrix, rolling statistics). Label units, axes, dates, data source and change markers; avoid misleading charts with no support.

## 3. Actual database and SQL requirement
Implement a normalized SQLite schema (e.g. wells, parameters, observations, quality flags/events or other observed entities), documented keys, sensible indexes/constraints and an ER diagram. Make ingestion rerunnable without duplicate inflation. Store SQL in **>=8 individually named `.sql` files** with specific analytical purposes, and execute each against the actual schema. Queries **collectively** include:
- `JOIN` across entities;
- `GROUP BY` and `HAVING`;
- subquery / CTE;
- window `LAG` for missing timestamp intervals per well+parameter;
- more window logic (rolling aggregates or row numbers) where sensible;
- well/time-period aggregates;
- well-type comparisons and quality coverage;
- analysis that feeds a dashboard or Pandas result.
Automated tests must execute all 8 queries on deterministic fixtures and verify invariants/results. Provide a CLI report/query runner that loads each query's output into Pandas and exports selected results. If source lacks metadata for a normalized dimension, document derivation instead of manufacturing entities.

## 4. Change point methods + baseline (not only library demos)
Define the evaluation task precisely: segment shifts in selected sensor variables / well regimes, not automatically supervised classification. Implement baseline + **two meaningfully different methods**, likely:
1. Baseline: no-change/persistence or simple rolling threshold, depending on measurable task.
2. Method A: rolling z-score or robust rolling median/MAD / CUSUM with causal window.
3. Method B: change-point segmentation (e.g. `ruptures` PELT, binary segmentation) or a different defensible statistical detector.
Use consistent tested interfaces, configs, thresholds and deterministic outputs. If alternatives require full-data power, provide a CPU-feasible run with downsampling and documented fidelity tradeoffs. Keep hyperparameter tuning strictly within chronological training/validation; freeze before test. Provided dataset chronological split takes precedence. Prohibit future-derived features in online detectors and train/test cross-contamination.

Determine whether labeled ground truth exists. If yes, use defensible event matching tolerance and precision/recall/F1 (with matching protocol explained), and/or MAE for a genuine numeric prediction target. If no, DO NOT manufacture labels or report fake precision/recall: compare detection counts, persistence/stability, expert-known transition alignment (not a definitive label), processing time/memory, and discuss inability to validate accuracy. All three methods must produce comparable outputs on the same evaluated scope. Save comparison table and machine-readable output plus figures. Include limitations / potential false detections due to May scaling.

## 5. Finished Streamlit dashboard
Implement **working**, usable tabs/pages rather than placeholders:
- Overview: dataset coverage, wells, periods, quality KPIs and source provenance;
- Well explorer: well, parameter, date range, quality filters, interactive Plotly timeseries, raw/rolling traces;
- Data quality: missingness, flags, duplicates, period gaps, known anomaly explanations;
- EDA: group comparison, correlation, daily patterns, explainable takeaways;
- Regime changes: baseline and 2 detectors, parameter/threshold selection (safe bounds), change markers and method comparison table;
- SQL Explorer / Reports: pre-defined 8 queries, table display, Pandas-derived visual/export, no uncontrolled raw SQL from end users by default.
Performance: cache immutable transformed data with invalidation by input version; load only selected well/time range; avoid full training and full reload on each widget event; use status/progress indicators and CSV exports where practical. Handle empty queries and unavailable computed artifacts without crashing. Support local CPU mode and optional precomputed full-mode outputs.

## 6. Verification, reproducibility, compliance
- Unit, DB integration and application smoke tests; specific cases for bad timestamps, empty input, unexpected flag, duplicated observations, temporal leakage, May/June issues, missing dates, SQL query correctness.
- Test dataset with at least two wells of different types and known injected synthetic regime change **for testing only**; do not include synthetic test data in research results.
- Capture actual benchmarks: timings, memory measurement approach, CSV/Parquet or Pandas/SQL comparison as appropriate, baseline vs two methods. Do not invent missing benchmarks.
- Complete `README.md`: install, data acquisition, normal/sample/full processing, DB initialization, running UI, executing SQL and tests, methods, resource limits, known limitations.
- Requirements matrix: every requirement 1–11 and cluster-specific task has implementation evidence (path/test/command), plus honest status of full-data validation as pending phase 3.

## Completion criteria
**All requested features exist and work on bounded real data** (or explicitly blocked by genuine absence of data). The dashboard is polished enough to show a teacher; all 8 SQL queries run; EDA is interpretable; baseline+two methods execute; the full dataset pipeline is designed to be scalable, and GPU/full-run is not necessary to demonstrate app features. Show actual test logs and open blockers in `docs/handoff.md`. Do not claim final full-data results yet.
