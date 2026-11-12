# Source observations
Source: https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2

Pinned revision: `4004bb78ca8811a87c2892a89e457c59d22ace2b`. Card and API metadata are preserved in `data/raw/`.
Observed CSV columns: well_id, well_type, timestamp, parameter, value, unit, n_obs, flag. Grain: parameter/well/hour; collision policy: reject ambiguous pivots. Timestamps are naive; do not assign a geographic timezone. Card warns the source year was assigned from file sequence.

Card reports 258,387 rows, 10 wells, Jan–Sep 2026, train 206,706 and test 51,681. Official split boundary: 2026-08-08 23:00, preserved without shuffling. Source CSV files total about 19.85 MB excluding redundant combined CSV. This is below both recommended 500,000-row and 200-MB thresholds: instructor exception or additional legitimate source required. Never duplicate rows.

Units: pressures atm, SPM strokes/min, fillage %, rod weight kg, area unitless. Units were assigned by source authors. NK-76 has no casing pressure. Well-type comparison must not equate unlike parameters.

Quality flags describe raw-record conditions propagated into hourly means: weight_overflow, area_negative, area_extreme, spm_outlier. Empty flag does not certify quality. Missing hours are absent records, distinct from null values. No imputation is applied.

Known May area scale shift and NK-7 June transition are source-card assertions until measured by the pipeline. Exclude area from default detectors; keep it for investigation. NK-7 is retained. No operating/failure ground truth or maintenance history. Apache-2.0 with provider attribution (Galaz and Company LLP) and source ownership restrictions. Full cardinalities and issue measurements will be saved as executable artifacts in subsequent phases.

Phase 1 measured slice: 2,064 actual source rows, all 10 wells and 8 parameter names, 2026-01-01 00:00 through 2026-01-03 00:00 (last hour incomplete). Zero null numeric values in this slice only. Reproduction: first 2,065 lines of pinned train CSV; retained at data/sample/phase1_source.csv.

Phase 3 measured full source matches card row/split totals: 258,387 / 206,706 / 51,681. 43 observed well/parameter pairs, 8 parameters, 10 wells, zero NULL values/duplicate keys. See `full_data_validation.md` and exact CSVs. Missing raw-record fillage cited by the card is not equivalent to NULL hourly values: absent hourly parameter rows capture missingness here. NK-7 lower SPM begins in May by monthly evidence, so the card's June narrative must not be treated as an exact onset label. Source quality-flag counts match the documented values; 7,041 hourly rows flagged in total. No production/failure labels were discovered in files or card.
