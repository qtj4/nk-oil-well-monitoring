# Phase 3 full CPU validation
Environment: Python 3.12, Windows, ~6.29 GB installed RAM, AMD Radeon graphics inspected; GPU not used. CPU methods did not require moving environments. Pinned source revision `4004bb78ca8811a87c2892a89e457c59d22ace2b`; file sizes and SHA256/Git blob hashes verified against official tree metadata by `tests/test_full.py`.

Validated run: `20261112T171150743233Z_full` (reproduction of earlier full run). 258,387 actual rows; 206,706 train / 51,681 test. Timestamp range Jan 1 00:00–Sep 30 23:00, 2026. 10 wells, 43 observed well/parameter pairs. Zero duplicate primary keys and zero NULL sensor values; absent hours remain missing records. 21,014 absent hour slots summed within each pair's observed endpoints (not extrapolated beyond those endpoints). 7,041 records have a source quality flag. Wide result: 63,470 well-hour rows; every one of 258,387 numeric values reconciled exactly. SQLite count matches long data.

Full CSV input bytes: 19,845,754; long Parquet: 2,180,136 bytes; optimized long Pandas memory: 9.800458 MB. This source fails the recommended 500,000-row / 200-MB size threshold. Additional legitimate data or instructor exception is external; no padding.

Whole pipeline measured 9.0366 s, sampled absolute process RSS peak 277.590 MB, increment 179.917 MB from 97.673 MB baseline. RSS polling every 10 ms can miss short peaks. Chunked CSV ingest+validation: 0.4662 s; Parquet reread: 0.0572 s; eight SQL→Pandas outputs: 2.8777 s. Different work and warm caches prevent claiming a pure format speedup. No bottleneck justified redesign.

## Methods / interpretation
Same 1,747 eligible test well-parameter-days, at least 12 unflagged readings/day, area excluded, Aug 8 straddling bin excluded. Test candidate counts: no-change 0, rolling shift 29, CUSUM 139. Costs: ~0.0004 / 0.1604 / 0.1118 s respectively. Threshold 80%/120% gives rolling 39/21 and CUSUM 148/125 candidates. These are sensitivity and processing diagnostics, not accuracy or distinct physical regime counts. Repeated CUSUM alerts may reflect persistent deviation from training reference despite a 7-day cooldown. No outcome labels exist. Main configurations were frozen before full test; sensitivity does not select a winner.

## Source narrative versus measured evidence
April→May dynamometer medians rise by factors 9.95–20.37 across seven pump wells in these exact monthly windows. This supports a scale discontinuity, not its cause. Source card uses different example windows/approximations; do not force those numbers to match.

NK-7 SPM monthly median: April 5.3439; May 1.4740; June 1.7443. Zero SPM fractions: May 49.46%, June 16.32%. Thus reduced SPM is already visible in May; an exact June onset is not established by measurements. Area negative fraction: May 30.68%, June 50.92%. Late-year low SPM and negative area persist. Data do not resolve calibration, shut-in, operational or equipment causes. Evidence: `known_issues.csv` and `nk7_monthly_evidence.csv`.

## Product and reproducibility
681 real candidate events across train+test indexed without deleting sample-run event history/reviews. Characterization measured 3.0014 s, sampled RSS increment 4.989 MB. Full diagnostic generated offline. All seven UI tabs, mode/well/quality/sensitivity filters and report generation are covered by AppTest. Full tests verify exact source hashes, split separation and database integrity. Tests use temporary review databases, never add synthetic notes to actual analyst history.
