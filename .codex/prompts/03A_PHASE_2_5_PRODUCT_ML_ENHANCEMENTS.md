# Codex Phase 2.5 — high-impact product features and practical ML (AFTER Phase 2, BEFORE Phase 3)

**Execution mode:** read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md` first. Operate independently: do not ask the user questions; inspect, decide, implement, test, fix and document. Record unavoidable blockers instead of stopping.

You are a senior product-minded Python engineer, data scientist, UX designer and reviewer. Read `01_SHARED_CONTRACT.md`, `03_PHASE_2_FULL_IMPLEMENTATION.md`, existing repository, tests, docs and `docs/handoff.md` before work. **Implement valuable extensions on top of the already working Stage 2 system.** Do not rebuild the app. Do not compromise mandatory coursework features, chronological split, data validity, low-resource demo or simplicity. This stage should make the project feel like a system an engineer could genuinely use, not a collection of notebooks.

## Product goal

A production-inspired **Well Monitoring & Regime Review Workbench**: an operator selects a well and time window, sees sensor trends and detected changes, can review/explain alerts, compare baseline and methods, and export a report. If possible, the app offers a *carefully justified and explainable* ML-assisted signal. All claims must be framed as **analytical decision support**, not safety-critical equipment control or reliable failure prediction.

## First: audit feasibility and choose tight scope

1. Inventory already-existing features and identify missing improvements. Do not duplicate phase 2 work. Inspect actual dataset schema, labels (if any), well type, flag semantics, units, periods, timestamps, chronological split and current method outputs. Assess whether ML has a **legitimate task with reliable labels or target** and enough training observations.
2. Write `docs/phase_2_5_scope.md` with a prioritized P0/P1/P2 table containing: feature, user's problem it solves, expected demo value, estimated effort (S/M/L), data dependencies, scientific risks, acceptance check. Target **3–5 working, integrated enhancements** rather than a dozen decorative tabs. Defer any high-effort feature that adds weak grading value.
3. Update `docs/requirements_traceability.md`: explain that enhancements are bonus value, **not guaranteed extra points** beyond rubric maxima. State exactly which rubric criteria/defense arguments each feature strengthens.
4. Respect resource constraints: CPU laptop, offline local demo, SQLite, Streamlit and optional precomputed ML artifacts. No frontend rewrite, no required Docker, cloud, user auth, Kafka, Redis, React or FastAPI. A separate API is optional only if a real integration use case is demonstrated and all core features still work without it.

## P0: implement these product-quality features (high score-to-effort)

### A. Event/alert review workflow with persistent SQLite storage

- Use existing change-point events from all three methods. Build an **event review queue** by well, parameter, time, method and status with filters/sort and relevant signal plot. Show clear explanation: observed value, before/after window statistics, event timestamp, score/threshold when available, `flag`/coverage context and possible May-2026 sensor scale artifact.
- Users can mark an alert `unreviewed`, `confirmed`, `dismissed` or `needs_investigation`; add optional analyst note and timestamp. Persist reviews in normalized SQLite (e.g. `alert_reviews` referencing stable event identifiers) without modifying raw observations or presenting human reviews as official truth labels.
- Event IDs must be reproducible across runs for identical method/config/data versions; define behavior when analysis is regenerated. Validate notes and status, use safe parameterized SQL, protect against duplicate reviews. If no events exist, show a helpful empty state.
- Add a comparison detail for **NK-7 June-2026** if actual data covers it; do not assert confirmation from the dataset unless verified.
- Support export of filtered reviewed events as CSV/JSON. Tests for persistence, duplicate handling, invalid statuses and events belonging to other wells.

### B. One-click well diagnostic report

- A Streamlit action generates a **downloadable self-contained HTML report** (and optionally PDF only if easy/reliable) for the selected well/date: data coverage, sensor summaries with units, time-series chart, data-quality issues, detected regime events, method comparison and reviewed-event summary.
- Report must include run ID, dataset version/path/hash or fingerprint, date range, method configurations, generation timestamp and honest limitations. Escape user-authored notes; don't assume internet for charts/assets. All values derived from actual database/artifacts, no hand-written numbers.
- UI download via `st.download_button`. Add snapshot/golden-data tests asserting essential report sections and escaping. Generate within a reasonable resource budget, no repeated full-data processing.

### C. Operational UX / reproducible scenarios

- Add curated **demo scenarios** based on *verified* dataset coverage, e.g. compare fountain vs sucker-rod-pump, investigate `dynamometer_area` around May-2026, inspect NK-7 around June-2026. Each scenario is a saved UI filter preset with question, expected views and caveats. If a real scenario is unavailable in sample mode, disable with explanation, not an invented plot.
- Add explicit dataset provenance badge/text, selected mode (sample/full), loading/empty/error states, time-window controls, chart download and clear metric definitions. Avoid inaccurate "live" data language: dataset is historical.
- Provide a 2–3 minute realistic defense story: choose a well -> inspect trend -> detect change -> check flag/coverage -> review alert -> export diagnostic report.

## P1: implement ONE low-risk ML/analytics enhancement chosen from actual data evidence

Pick one after documenting feasibility; **do not turn this into a GPU-heavy ML project**. ML earns credibility through valid experimental design rather than flashy terminology.

**Option 1 — Forecasting next sensor value (preferred IF stable numeric target and sufficient time history):**
- Define explicit target (parameter and horizon), per-well or justified group strategy, time-aware lag/rolling features computed only from preceding observations; avoid future aggregation, target leakage and cross-well mixing.
- Compare a persistence/last-value baseline with two economical candidates, e.g. Ridge regression and HistGradientBoostingRegressor or RandomForestRegressor with constrained size. If three methods already satisfy the phase 2 requirement, these are *additional* ML evidence, not a replacement for regime detection.
- Chronological train/validation/test, hyperparameter selection only before frozen test; report MAE (and optionally RMSE) plus latency, RAM and data coverage by well type. Prediction forecast is NOT proof of fault prediction. Offer a cached chart of observed vs predicted and residual anomalies, with an honest model limitations panel.

**Option 2 — Explainable regime characterization (when no defensible supervised target):**
- Add quantitative *unsupervised* features before/after change events: level shift, rolling variability, slope, flag density, missingness, duration; optional clustering of event signatures (KMeans only if sensible). Label clusters as descriptive patterns, **never** as verified equipment failure or operating state. Include sample sizes, feature distributions, sensitivity and execution costs. Do not invent precision/recall.
- Highlight change-point reasons in UI: which sensors changed, magnitude and possible data quality confounders. This may be more valuable than forced ML if ground truth is missing.

**Option 3 — Lightweight anomaly score (if forecasting and clustering are unjustified):**
- Robust MAD-based anomaly scores or IsolationForest with carefully bounded contamination, fit strictly on training data. Compare with an uncomplicated threshold baseline, discuss false positive risk and separate measurement artifacts vs operational changes. No precision/recall absent validated labels.

The option selected must be defensible in 60 seconds: what does it predict/describe, what is input/output, why this method, how evaluated, what limitations. Save real results and configs; integrate **one** useful chart + explanations into existing app. If data access is missing, implement with explicit fixture-only tests and mark experimental results as pending, NOT complete.

## P2: only if effort remains and P0/P1 are verified

- Add comparison mode for two selected wells with aligned time units, normalized view toggle and sampling/coverage warnings. Avoid implying causal comparisons where confounded.
- Add saved filter presets/bookmarks in local SQLite, simple export/import of project settings as JSON.
- Optional thin FastAPI **read-only** endpoint for well summary/events if genuinely useful for integration demonstration; document it as optional, keep Streamlit standalone and Python-only, test it. Do not add this merely to use the word “full-stack”.
- Optional lightweight deploy instructions (Streamlit Community Cloud if data size/licensing permit or local Docker only if trivial). Local offline demo is first-class.

## Architecture and safety

- Separate presentation/controllers from pure analytics and persistence. Migrate existing SQLite schema non-destructively; never overwrite a research run or raw data with review notes. Use parameterized SQL, transaction boundaries, explicit schema versioning and indexes for event/well/time lookups.
- Make event artifact ingestion idempotent. Cache expensive computations per run/config, not unversioned global mutable state. The dashboard must never train expensive models on every rerun. Keep preview mode responsive on constrained RAM.
- Unit tests + integration tests for alert workflow, report generation, chosen ML features and time-split invariants; Streamlit smoke test if tool support permits. Verify that initial phase 2 behavior is unchanged.
- Clearly distinguish model-generated **candidate events** and human-reviewed statuses. No automatic maintenance actions, no "confirmed fault" without valid external ground truth. Keep security simple and honest: local single-user analyst app, not a multi-tenant production system; if multiple users or remote access is desired, note the missing auth/audit/concurrency hardening.

## Required deliverables

1. Integrated implementation and tests for P0 (A/B/C); P1 chosen option implemented or explicitly blocked by actual data limitations (with rationale).
2. `docs/phase_2_5_scope.md`, `docs/product_workflow.md`, `docs/ml_extension.md` (chosen task, leakage controls, methods/metrics), updated architecture, README, requirements traceability and handoff.
3. `results/` outputs from actual executed experiments only, with seed/config/source fingerprint and resource measurements. Never substitute fixtures as research.
4. `docs/phase_2_5_demo_script.md`: a concise **2–3-minute** live walkthrough and fallbacks when offline / results absent.
5. Print commands actually run, tests passed/failed, feature-by-feature acceptance status and blockers for Phase 3.

## Definition of done (stop condition)

- From Streamlit, a reviewer can select a well, inspect a candidate regime change and data-quality context, **save a review to SQLite**, reload and see it persisted, then **download a real diagnostic report**.
- At least one tested added analytical/ML insight is visible with real (or explicitly pending) evidence and no invalid label/metric claims.
- CPU/sample mode works locally and all existing mandatory Phase 2 requirements remain intact. Do not spend effort on auth, frontend rewrites or large deep-learning models at the expense of these outcomes.

## Final Codex response

Summarize implemented functionality and exact repository paths, actual commands and test logs, any P1/P2 decisions, demo workflow and handoff instructions for `04_PHASE_3_FULL_DATA_GPU.md`. Implement code now; do not only propose a plan.
