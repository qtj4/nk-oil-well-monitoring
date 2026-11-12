# Codex Phase 1 — dataset research, architecture, documentation, working skeleton

**Execution mode:** read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md` first. Operate independently: do not ask the user questions; inspect, decide, implement, test, fix and document. Record unavoidable blockers instead of stopping.

Read `01_SHARED_CONTRACT.md` and treat this phase as the only active implementation scope. Goal: a **runnable vertical slice** on a weak laptop, with evidence-based design; not a folder of empty placeholders.

## Tasks in order
### A. Reconnaissance and requirements
1. Inspect all present files, git status, Python/platform constraints, data files and any inherited code. Protect existing work.
2. Read the source dataset card and inspect source metadata: https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2. Where feasible fetch only schema/head, file list/size, splits, representative records and a small period-bounded sample; avoid auto-downloading the full set on a low-memory laptop. Use actual schema to identify well ID, timestamp, parameter, value, unit, well type, flag, partitioning, train/test metadata. Log uncertainties and missing access.
3. Establish approximate row count/size from trustworthy metadata or a streaming count with memory bound; do not invent it. Check May 2026 `dynamometer_area` and June 2026 NK-7 documented issue, noting what is metadata versus actually confirmed in sampled observations.
4. Translate **every** shared requirement to `docs/requirements_traceability.md`: ID, rubric weight, implementation owner/module, test/evidence, status (planned / implemented / tested), limitation. Include 8-query requirement, ER diagram, baseline+two methods, chronological split, and deliverables.

### B. Design and documentation BEFORE complex code
Produce:
- `docs/project_scope.md`: questions, definitions of regime change vs anomaly vs data-quality artifact, personas, expected findings and boundaries; don't promise oil-production causal diagnosis.
- `docs/dataset_profile.md`: links, schema from observation, field descriptions/units, cardinalities, size/splits, timeline, quality flags, source provenance, access method; explicit unknowns.
- `docs/architecture.md`: justified simple modular Python + Streamlit + SQLite architecture, data flow/raw→validated long→wide/Parquet→SQLite→EDA/detectors→visuals, responsibilities, execution environments, Mermaid component/dataflow diagram. Explain why separate JS backend/frontend is unnecessary.
- `docs/database_design.md`: provisional normalized relational schema, PK/FK/indexes, high-level ER diagram (Mermaid acceptable), long-vs-wide storage strategy and first query plans.
- `docs/experiments_plan.md`: baseline and two methods with assumptions, candidate targets, whether labels are known, fair comparisons, leakage checks, train/test policy, performance plan, risks if no ground truth.
- `docs/decisions.md`: ADR-style decisions and alternatives, including SQLite vs PostgreSQL; Streamlit vs Dash; simple CPU detectors vs complex ML; CSV vs Parquet.
- `docs/handoff.md`: stage status, blockers and concrete next steps.

### C. Initialize with a *working* minimal vertical slice
Recommended layout (adapt after inspection):
```
app.py
src/nk_oil/{__init__.py,config.py,dataset.py,quality.py,transform.py,database.py,analytics.py,methods.py,charts.py}
scripts/{inspect_dataset.py,prepare_data.py,init_db.py}
sql/queries/
tests/{conftest.py,test_ingest.py,test_transform.py,test_database.py}
docs/
data/{raw,processed,sample}/
results/
requirements.txt
README.md
.gitignore
```
Write executable entrypoints and real interfaces, not empty stubs. Add venv setup; `.gitignore` excludes raw/full data, DBs, large artifacts, tokens but retains small explicit fixtures. Pin versions of installed dependencies or document reproducible constraints.

Implement the minimum complete flow:
- config from environment / CLI (`sample` default); bounded input; dataset discovery or helpful no-data error;
- read a genuine small source slice if available; otherwise create an explicitly **synthetic tests-only** fixture with transparent provenance;
- parse timestamps, apply basic schema validation, audit nulls/duplicates, implement a safe long→wide pivot;
- write and read a processed Parquet (or CSV if Parquet dependency is temporarily blocked), create SQLite schema, insert sample rows idempotently, execute at least one tested SQL query into Pandas;
- launch Streamlit: data availability/status, well selector, time series chart and small quality table (real data only when available; synthetic labeled demo mode);
- useful `--help`, friendly exceptions and clear logs.

### D. Tests and acceptance
- Unit tests for pivot uniqueness, multi-well independence, timestamp ordering, schema validation and SQLite roundtrip.
- Execute install, test, inspect-data, init-db and app smoke checks where possible; list actual commands and failures.
- Show a clean start via README from fresh Python venv, or explicitly describe environment blockers.
- Verify there is a functional end-to-end vertical slice; no false claim of full rubric compliance yet.
- Update traceability statuses accurately, output file tree and handoff. Do not execute expensive full-data or model training in phase 1.

## Definition of done
A person can clone/install/run the skeleton and view a real chart from a small verified dataset slice, OR a conspicuously labeled synthetic demo if source unavailable. Architecture, dataset contract, SQL design, experiment design and requirement matrix exist. Sample tests pass; limitations plainly stated.
