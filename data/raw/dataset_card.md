---
license: apache-2.0
task_categories:
- time-series-forecasting
tags:
- oil-and-gas
- well-monitoring
- sensor-data
- time-series
- industrial
- predictive-maintenance
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files:
  - split: train
    path: train.csv
  - split: test
    path: test.csv
---

# Oil Well Sensor Monitoring Dataset - NK Field (v2, extended)

Hourly sensor readings from 10 oil wells at the NK field, **January 1 - September 30, 2026**.
This version extends the earlier release (period to July 20, 2026) and adds per-row quality flags.

Data provider: **Galaz and Company LLP** (ТОО «Галаз и Компания»), within the research project
"Development and Implementation of Control Algorithms for Low-Production-Rate Wells in Mechanized Oil Production Systems, Including Plunger Lift and Sucker-Rod Pump Systems, Using Artificial Intelligence Methods."

## Summary

| Item | Value |
|---|---|
| Wells | 10 (3 fountain, 7 sucker-rod pump) |
| Period | 2026-01-01 00:00 - 2026-09-30 23:00 |
| Sampling | hourly (aggregated from raw records, see below) |
| Rows | 258,387 (long format) |
| Train | 206,706 rows, 2026-01-01 00:00 - 2026-08-08 22:00 |
| Test | 51,681 rows, 2026-08-08 23:00 - 2026-09-30 23:00 |
| Split | chronological, no shuffling (about 80% / 20% of rows) |

## Wells

| Well ID | Type | Parameters |
|---|---|---|
| NK-75, NK-83 | fountain | tubing, casing, line pressure |
| NK-76 | fountain | tubing, line pressure (no casing pressure) |
| NK-7, NK-68, NK-77, NK-82, NK-86, NK-91, NK-93 | sucker-rod pump | SPM, pump fillage, min/max rod weight, dynamometer area |

## Structure

One row = one parameter of one well in one hour.

| Field | Type | Description |
|---|---|---|
| `well_id` | string | Well identifier |
| `well_type` | string | `fountain` or `sucker_rod_pump` |
| `timestamp` | datetime | Start of the hour |
| `parameter` | string | Parameter name |
| `value` | float | Hourly mean of raw records |
| `unit` | string | Unit of measurement |
| `n_obs` | int | Number of raw records aggregated into the hour |
| `flag` | string | Quality flag(s), `;`-separated; empty if none |

| Parameter | Unit | Well type |
|---|---|---|
| `tubing_pressure`, `casing_pressure`, `line_pressure` | atm | fountain |
| `SPM` | strokes/min | sucker-rod pump |
| `pump_fillage` | % | sucker-rod pump |
| `min_rod_weight`, `max_rod_weight` | kg | sucker-rod pump |
| `dynamometer_area` | unitless | sucker-rod pump |

Units are carried over from the previous release; they are not stored in the source Excel files.

## Processing

- Source: one Excel sheet per well; raw sampling is about 10 min (sucker-rod pump wells) and about 5 min (fountain wells).
- Columns renamed to English, `well_type` and `unit` assigned, long format.
- Rows with duplicate raw timestamps removed (first occurrence kept); records sorted chronologically.
- Raw records aggregated to hourly **mean** (`value`); `n_obs` is the record count.
- **No imputation:** missing hours are absent rows.
- **No outlier removal or correction.** Suspicious raw records are only flagged.

## Quality flags

Flags are computed on raw records; an hour is flagged if any of its raw records is flagged.
Because `value` is a mean, a flagged hour may be distorted by the artifact (e.g. one 65530 record).

| Flag | Rule | Rows |
|---|---|---|
| `weight_overflow` | min/max rod weight >= 30,000 (values such as 65530 suggest a 16-bit overflow) | 4,098 |
| `area_negative` | dynamometer area < 0 | 2,844 |
| `area_extreme;area_negative` | both | 77 |
| `area_extreme` | abs(dynamometer area) > 1e6 | 20 |
| `spm_outlier` | SPM > 9 | 2 |

## Known data-quality issues

1. **Scale shift of `dynamometer_area` in May 2026.** In all sucker-rod pump wells the median area grows by a factor of roughly 13-30 (e.g. NK-68: ~15,300 before May, ~225,700 after; NK-77: ~17,700 to ~300,100; NK-91: ~9,600 to ~190,900; NK-93: ~4,500 to ~61,900; NK-82 changes on 2026-05-08). This looks like a change of units or calibration rather than a physical effect; the cause has not been confirmed. Not flagged. Normalize per period or exclude the parameter before modelling.
2. **NK-7 behaviour changes from June 2026:** SPM falls from about 4-5 to about 1, dynamometer area is mostly negative, and 12% of its records have SPM = 0. Treat as a different operating or sensor regime.
3. **Multi-day gaps:** NK-91 2026-01-29 to 2026-02-04 and about 2026-05-21 to 2026-05-30; NK-86 2026-04-29 to 2026-05-12; NK-93 about 53 h in January; NK-82 about 41 h in January.
4. **Common collection outages across wells:** about 2026-02-27 (12 h), 2026-03-08 (12 h), 2026-04-15 (21 h), 2026-08-03 (7 h), 2026-09-13 (7 h).
5. High share of missing pump fillage and area values in NK-7, NK-82, NK-93 (about 18-23% of raw records).
6. Original timestamps had no explicit year in the earlier release; the year 2026 was assigned from the monthly file sequence and should be verified against the SCADA system.
7. Fountain wells report pressures asynchronously; individual parameters are frequently missing within an hour.
8. Zero values (e.g. SPM = 0) mostly correspond to shut-ins and are kept.

## Intended use and limitations

For scientific, educational and experimental research (forecasting, anomaly detection, shut-in detection, predictive maintenance). Not for real-time production or safety-critical decisions; verify results against the operator's monitoring systems.
The data do not include production rate, water cut, bottom-hole or reservoir pressure, maintenance history, or verified failure labels. Plunger lift wells are not included.

## Attribution and license

Apache License 2.0. Users must also comply with the data-ownership, confidentiality and contractual requirements of the original data. Acknowledge Galaz and Company LLP (ТОО «Галаз и Компания») in publications.

## Citation

```bibtex
@dataset{tleubayeva_2026_nk_well_monitoring_v2,
  author       = {Arailym Tleubayeva},
  title        = {Oil Well Sensor Monitoring Dataset: NK Field (v2)},
  year         = {2026},
  publisher    = {Hugging Face},
  note         = {Data provided by Galaz and Company LLP within a research project on AI-based control of low-production-rate wells},
  url          = {https://huggingface.co/datasets/Arailym-tleubayeva/NK-Oil-Well-Sensor-Monitoring-v2}
}
```
