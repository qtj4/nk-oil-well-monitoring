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
# SQL and full processing (full validation belongs to phase 3)
./.venv/Scripts/python.exe -m nk_oil.cli queries --mode sample
./.venv/Scripts/python.exe -m nk_oil.cli prepare --mode full
./.venv/Scripts/python.exe -m ruff check .
```
The UI selects sample/full in the sidebar. Preparation creates `data/processed/<mode>/` plus a versioned `results/<run_id>/` directory. Runs preserve measured summaries, method outputs, sensitivity, benchmarks, SQL and five offline HTML charts. UI caches by immutable data fingerprint. CLI `init-db` and `analyze` run the same reproducible pipeline; no hidden training at startup.

Methods: no-change baseline, causal rolling shift using preceding three daily values, two-sided CUSUM with training-only median/MAD. At least 12 unflagged hourly readings per daily median; exclude dynamometer area by default and exclude August 8 across both splits. Threshold sensitivity 80/100/120% is precomputed and descriptive. Training-era markers use training-wide fitted references; only test-era evaluation has frozen-reference temporal interpretation. No labels → no precision/recall or fault claims.

Benchmark method: 10-ms process RSS polling (includes Python/library baseline and may miss brief peaks); wall-clock timing. Read comparisons have different CSV validation and Parquet parsing work and warm filesystem caches, so are descriptive workload costs, not isolated format speedups. Resource budget: 25,000-row CSV chunks, source files capped at 30 MB each, deterministic monthly sample, no GPU.

Common errors: run commands from project root; use `py -3.12` if `python` opens Windows Store; run `fetch` when raw data are absent; use sample mode if full artifacts are not prepared. Restore the pinned metadata and cached sample from Git for offline use. Never mix synthetic test fixtures into actual results.

Product workflow: run `python -m nk_oil.cli enhance --mode sample` after preparation (use venv executable as above). Review workbench persists candidate statuses/notes to `data/reviews.sqlite`; it survives regenerated analysis. SQL & reports generates a self-contained downloadable diagnostic. Demo presets investigate NK-7 June, May area scaling and fountain pressures. Event characterization is a retrospective descriptive extension, not fault ML. See `docs/product_workflow.md`, `docs/ml_extension.md`, `docs/phase_2_5_demo_script.md`.
