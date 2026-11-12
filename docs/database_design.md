# Database
Dimensions wells(well_id PK, well_type) and parameters(parameter PK, unit); observations PK(well_id, parameter, timestamp), foreign keys to dimensions. Timestamp index supports range queries. Null values are retained. Dimension mappings must be unique. Idempotent observation upserts prevent duplicate inflation. Source split is retained per observation. Flags are source categorical values, not manufactured labels.

```mermaid
erDiagram
  wells ||--o{ observations : has
  parameters ||--o{ observations : measures
  wells { text well_id PK }
  parameters { text parameter PK }
  observations { text well_id FK
    text parameter FK
    text timestamp PK
    real value
    text flag
    text split }
```

Phase 2 query plans: coverage JOIN; monthly aggregates; HAVING flag groups; LAG missing intervals per well/parameter; causal rolling window; flag distribution; type-level summaries; latest observation via ROW_NUMBER. Results return to Pandas.

Phase 2 implementation: eight individual `sql/queries/*.sql` files execute via `pipeline.run_queries`. `flag_types` and `observation_flags` normalize semicolon-separated flags; original `observations.flag` is retained as audit provenance. CLI snapshot replacement clears derived observations/links inside a transaction, leaves dimensions and future analyst-review tables intact. Ordinary `build` calls use idempotent upsert. Rolling SQL explicitly uses 24 preceding **records**, which need not equal 24 clock hours.

```mermaid
erDiagram
  observations ||--o{ observation_flags : tagged
  flag_types ||--o{ observation_flags : defines
  observations { text well_id PK
    text parameter PK
    text timestamp PK }
  observation_flags { text well_id FK
    text parameter FK
    text timestamp FK
    text flag FK }
  flag_types { text flag PK }
```

Separate persistent review database:
```mermaid
erDiagram
  analysis_runs ||--o{ event_runs : contains
  events ||--o{ event_runs : associated
  events ||--o| alert_reviews : reviewed
  analysis_runs { text run_id PK
    text data_hash }
  events { text event_id PK
    text well_id
    text parameter
    text timestamp
    text config }
  event_runs { text event_id FK
    text run_id FK }
  alert_reviews { text event_id PK
    text status
    text note
    text updated_utc }
```
