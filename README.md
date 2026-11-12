# NK Well Monitoring & Regime Review
Historical educational research using NK Oil Well Sensor Monitoring v2. Data provider: Galaz and Company LLP; dataset author: Arailym Tleubayeva. Source and limitations: `docs/dataset_profile.md`.

Windows PowerShell, from project root:
```powershell
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m nk_oil.cli fetch
./.venv/Scripts/python.exe -m nk_oil.cli prepare --mode sample
./.venv/Scripts/python.exe -m pytest
./.venv/Scripts/python.exe -m streamlit run app.py
```
Use the venv's Python on platforms where `python` is an alias. Defaults are CPU/sample mode. No GPU is required or claimed. Tests use clearly synthetic fixtures; research results use actual source records. No production control or validated fault prediction.

Read `docs/requirements_traceability.md`, `docs/handoff.md` and `docs/assumptions_and_blockers.md` for coverage and external dependencies.

Sample mode selects the first 10 days of each month (85,423 rows in the verified source), all available wells/parameters; gaps caused by selection are explicitly labeled. `data/sample/monthly_source.parquet` supports offline preparation after acquisition. `--phase1` reproduces the original small January-only slice.

```powershell
# SQL and full processing (verified on the complete source)
./.venv/Scripts/python.exe -m nk_oil.cli queries --mode sample
./.venv/Scripts/python.exe -m nk_oil.cli prepare --mode full
./.venv/Scripts/python.exe -m ruff check .
```
The UI selects sample/full in the sidebar. Preparation creates `data/processed/<mode>/` plus a versioned `results/<run_id>/` directory. Runs preserve measured summaries, method outputs, sensitivity, benchmarks, SQL and five offline HTML charts. UI caches by immutable data fingerprint. CLI `init-db` and `analyze` run the same reproducible pipeline; no hidden training at startup.

Methods: no-change baseline, causal rolling shift using preceding three daily values, two-sided CUSUM with training-only median/MAD. At least 12 unflagged hourly readings per daily median; exclude dynamometer area by default and exclude August 8 across both splits. Threshold sensitivity 80/100/120% is precomputed and descriptive. Training-era markers use training-wide fitted references; only test-era evaluation has frozen-reference temporal interpretation. No labels → no precision/recall or fault claims.

Benchmark method: 10-ms process RSS polling (includes Python/library baseline and may miss brief peaks); wall-clock timing. Read comparisons have different CSV validation and Parquet parsing work and warm filesystem caches, so are descriptive workload costs, not isolated format speedups. Resource budget: 25,000-row CSV chunks, source files capped at 30 MB each, deterministic monthly sample, no GPU.

Common errors: run commands from project root; use `py -3.12` if `python` opens Windows Store; run `fetch` when raw data are absent; use sample mode if full artifacts are not prepared. Restore the pinned metadata and cached sample from Git for offline use. Never mix synthetic test fixtures into actual results.

Product workflow: run `python -m nk_oil.cli enhance --mode sample` after preparation (use venv executable as above). Review workbench persists candidate statuses/notes to `data/reviews.sqlite`; it survives regenerated analysis. SQL & reports generates a self-contained downloadable diagnostic. Demo presets investigate NK-7 June, May area scaling and fountain pressures. Event characterization is a retrospective descriptive extension, not fault ML. See `docs/product_workflow.md`, `docs/ml_extension.md`, `docs/phase_2_5_demo_script.md`.

Final delivery: `deliverables/final_report.pdf` (9 pages), `final_presentation.pptx` (12 editable slides), presentation PDF/preview, complete Markdown report and `docs/defense_guide.md`. Evidence run: `results/20261112T171150743233Z_full/`. Full dataset: 258,387 actual source rows, zero duplicate keys/NULL sensor values, 21,014 absent pair-hour slots within pair endpoints. Main test candidate counts 0 / 29 / 139; this is not accuracy. NK-7 SPM already drops in May by measured monthly evidence despite the approximate June narrative in the source card. See `docs/full_data_validation.md` and `docs/final_audit.md`.

Validation: 21 tests passed in original and clean environments; pip check and Ruff passed. A fresh sample-only checkout skips the 2 full-artifact checks; run `fetch`, `prepare --mode full`, `enhance --mode full` to enable them. `./check.ps1` performs the current sample pipeline, enhancement, SQL and suite. Actual `DATA_MODE=full` is supported as the CLI/UI initial default; explicit `--mode` or sidebar selection overrides it. Tests expect the default sample mode.

Offline: after installing dependencies, `prepare --mode sample` can use bundled `data/sample/monthly_source.parquet` without network. The dashboard/report need no internet once prepared. Synthetic tests are separate from results. Windows paths are resolved from package location; a Git-free source archive is supported. Optional PDF regeneration: use a Python environment with ReportLab and Windows Arial fonts, run `python scripts/build_report.py`. PowerPoint authoring source requires the Codex bundled Artifact Tool; it is not required to run the application.

GitHub destination: **qtj4/nk-oil-well-monitoring only** (private). This project's phase history was created locally and is preserved. Never push to another owner or force-push. Exam/Moodle date, topic approval, dataset-size exception and real teammate contributions remain external inputs; no submission is claimed.
