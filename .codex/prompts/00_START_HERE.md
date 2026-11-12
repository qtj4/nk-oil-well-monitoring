# NK Oil Wells — Codex implementation playbook

## Project
**Operating Regime Analysis of Oil Wells** — comparison of `fountain` and `sucker_rod_pump` wells and detection of operating regime changes using **NK Oil Well Sensor Monitoring v2**.

Dataset: https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2

Course: Programming for Data Analysis and Database, Applied Artificial Intelligence master's final project. Implementation must be Python 3.x; executable in terminal/VS Code/PyCharm or Colab. Streamlit is the preferred UI (all application code in Python).

## Autonomous mode
The user expects Codex to work independently, **without asking questions or requesting routine approvals**. Before every stage read `00_AUTONOMOUS_EXECUTION.md` and `01_SHARED_CONTRACT.md`. Decide ambiguous details based on the rubric, inspected data and code; implement and run checks, and record assumptions or genuine blockers rather than interrupting the user.

## Execution order
1. Read `01_SHARED_CONTRACT.md` and `02_PHASE_1_FOUNDATION.md`; run phase 1. Review output and commit.
2. Re-read shared contract, run `03_PHASE_2_FULL_IMPLEMENTATION.md`; insist on functional completeness under CPU/lightweight constraints.
3. Run `03A_PHASE_2_5_PRODUCT_ML_ENHANCEMENTS.md` as a targeted product/ML enhancement stage, **still on the CPU laptop**; complete practical alert review, report export and one defensible ML/analytics addition.
4. Run `04_PHASE_3_FULL_DATA_GPU.md` in a GPU/full-compute environment. GPU is optional if selected methods are CPU-only; never claim GPU acceleration without actual use.
5. Run `05_PHASE_4_REVIEW_DELIVERY.md` for objective acceptance and submission artifacts.

Give Codex **the autonomy policy, shared contract, and the requested phase file**. Put the files in the **project root or `.codex/prompts/`** and refer to them in Codex with explicit paths. If the repo already exists, instruct Codex to inspect it before touching files.

## Priority / boundaries
- **P0:** all required coursework functionality, reliable startup, no temporal data leakage, dataset-specific known issues, SQLite + 8 real queries, readable dashboard.
- **P1:** measured performance, reproducible baseline + two methods, testing, results interpretability.
- **P2:** phase 2.5 targeted operational workflow and scientifically justified lightweight ML; advanced deployment only if time remains.
- Do not introduce a separate JavaScript frontend, REST microservices, Docker/Kafka/Postgres by default. Streamlit + Python modules + SQLite is sufficient and more defensible for the rubric.
- Do not generate fake dataset stats, metrics, analysis conclusions, screenshots, or training results.

## Stage handoff artifacts
Each phase must end with:
- summary of files created/modified;
- commands actually executed and their outcome;
- requirements coverage updated in `docs/requirements_traceability.md`;
- known issues and next-stage risks in `docs/handoff.md`;
- specific run instructions;
- **actual** tests and performance metrics, explicitly distinguishing measured values from planned values.

## Minimum final deliverables
Python source, dataset files or credible data source link, pinned `requirements.txt`, README with reproducible instructions, SQLite database creation script/pipeline, ER diagram, at least eight real SQL queries, report, presentation, GitHub repo with commit history, Moodle submission of report and presentation 2–3 days before final exam. Instructor-approved topic and teammate contributions where applicable.

## Grading weights
Software implementation 20, data/preprocessing 15, databases/SQL 10, EDA/visualization 15, methods/comparison 15, reproducibility/code quality 10, report 5, presentation/defense 10 = 100.

## Ready-to-paste stage command

```text
Read 00_AUTONOMOUS_EXECUTION.md, 01_SHARED_CONTRACT.md, and the relevant PHASE markdown. Execute the selected phase autonomously to completion. Do not ask me for choices or clarification. Inspect the repository and real dataset, make justified decisions, implement code, run tests, fix failures and update documentation. For genuine external blockers, continue all feasible work and report precise limitations in a final handoff without questions.
```
