WITH intervals AS (
 SELECT well_id,parameter,timestamp,
 LAG(timestamp) OVER(PARTITION BY well_id,parameter ORDER BY timestamp) previous_time
 FROM observations
), gaps AS (
 SELECT *,CAST(ROUND((julianday(timestamp)-julianday(previous_time))*24) AS INTEGER) elapsed_hours
 FROM intervals WHERE previous_time IS NOT NULL
)
SELECT *,elapsed_hours-1 missing_hours FROM gaps WHERE elapsed_hours>1;
