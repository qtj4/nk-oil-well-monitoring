# Decisions
1. SQLite over PostgreSQL: portable offline local usage; no administration.
2. Streamlit over Dash: all-Python educational workflow with simple widgets and caching.
3. CPU causal detectors over deep learning: no reliable failure labels, limited RAM (~6.29 GB installed).
4. Preserve raw float64 values; categorical identifiers and Parquet reduce memory without precision loss.
5. Reject duplicate observation keys rather than silently average conflicting records.
6. Sample: first 72 hours of each month, all wells; monthly gaps are selection artifacts and must be identified.
7. Keep timezone naive: source does not document one. Source year itself remains uncertain.
