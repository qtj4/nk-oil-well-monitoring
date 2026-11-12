WITH ranked AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY well_id,parameter ORDER BY timestamp DESC) r
 FROM observations
)
SELECT well_id,parameter,timestamp,value,flag FROM ranked WHERE r=1;
