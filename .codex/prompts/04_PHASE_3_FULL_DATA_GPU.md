# Codex Phase 3 — full-dataset execution, GPU only where justified, final experimental results

**Execution mode:** read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md` first. Operate independently: do not ask the user questions; inspect, decide, implement, test, fix and document. Record unavoidable blockers instead of stopping.

Read shared contract, prior docs and stage 2 implementation and phase 2.5 enhancements. You now have a stronger GPU-capable computer or Colab. **Your job is not to rebuild the application.** Confirm data access, run the exact full-data pipeline, profile bottlenecks, improve only where measurements justify it, and create evidence-backed final experimental results.

## Execution safety
1. Inspect actual environment (Python packages, disk, CPU, memory, CUDA/accelerator) and dataset file list, source version/hash. Do not assume GPU exists just because Colab is used.
2. Protect source/training data, split integrity and stage 2/2.5 working CPU mode. Track GPU usage only if chosen algorithm actually runs on GPU. Rolling statistics, SQLite and typical `ruptures` often remain CPU tasks; a fast CPU run is acceptable and more truthful than decorative GPU code.
3. Establish run identifiers, deterministic seeds (where applicable), input fingerprints, environment/package versions, experiment configs and artifact folders. Confirm that dataset source timestamp and specific split metadata are recorded.

## Phase 2.5 integration
- Recompute/reindex regime events from full-data outputs without losing analyst review notes; stable event IDs should be tied to run/config/data version. If reviews from sample mode do not match full run, keep history and mark them as belonging to their originating run rather than silently merging.
- Run the optional Phase 2.5 ML/analytics extension only if feasible and justified by actual data; refresh its model card/limitations and dashboard artifacts. Verify diagnostic export works for full-data derived wells.

## Full execution
- Acquire the *real full dataset* or explicit accessible subset if blocked; report row count, MB, period coverage, well types, flags, missing values and compliance with recommended >=500k rows / >=200MB; never pad rows to meet it.
- Execute validated chunked reading, cleaning (with retained audit raw evidence), type optimization, long→wide pivot, Parquet export, normalized SQLite import/indexes, all 8 SQL queries, Pandas imports and EDA exports.
- Record actual time, peak resident RAM (or well-defined tracemalloc/process method), file sizes and processing parameters. Benchmark at least two processing approaches if appropriate (e.g. chunked CSV vs Parquet; SQL vs Pandas); run comparable inputs and document measurement method.
- Generate final dashboard-ready cached datasets, plots and quality exports. Test real app navigation/filters on realistic full-data partitions.

## Methods and model execution
- Verify and *use* the designated chronological train/test split. Where absent, apply documented chronological fallback. Ensure detectors, scalers, thresholds, rolling features and aggregate references cannot use future/test information during fitting or tuning.
- Run baseline + 2 methods on identical evaluation units; measure latency/memory, event counts/stability and appropriate **true** outcome metrics if annotated regime labels exist. If no reference labels, be explicit that quality/precision cannot be established and supply only measurable descriptive/robustness proxies.
- Compare fountain and sucker-rod-pump well behavior and study May 2026 dynamometer scale shift and NK-7 June 2026 transitions separately; sensitivity analysis should consider whether scale/flag issues spuriously drive detectors.
- Optional acceleration: optimize confirmed slow hotspots; evaluate sampling, vectorization, algorithm settings and parallelism; consider GPU-accelerated model only if required for a justified modelling extension. If GPU algorithm is added, preserve a CPU fallback and fair comparisons. Document speedup as a measured ratio on equivalent workloads, never an estimate.
- Freeze decisions before final test; avoid repeated tuning on the test set.

## Final artifacts
Save under `results/<run_id>/`:
- `run_manifest.json` (config, commit hash if available, source version, data hash/paths, environment, split, timestamps);
- `dataset_summary.json` and `quality_report.*`;
- `processing_benchmarks.csv` (observed values and measurement units);
- `methods_comparison.csv` (baseline + 2, exact metric definitions, timing, memory and score applicability);
- event tables by method, well, parameter, timestamp and optional confidence/status;
- main figures (`.html` interactive and/or `.png` static), important SQL exports;
- `findings.md` with evidence, uncertainty, limitations and references to generated outputs.
Avoid committing huge datasets or model artifacts to GitHub; document retrieval/checksums and small reproducibility sample.

## Tests / gating
Run all tests and a full-data smoke test of every UI tab. Validate schema counts and pivot reconciliation, SQL completeness, split separation, no future leakage, correctness under sparse periods and unknown flags. Reproduce a selected run from clean commands. Capture all actual command outputs/exit status, remaining failures and relevant performance decisions. Update `docs/requirements_traceability.md` and `docs/handoff.md`.

## Completion
Full datasets and experiment results are **real, reproducible and defensible**; or explicitly document blocked parts and never present partial analysis as a full run. Preserve a lightweight demo mode for defense on less powerful hardware.
