SELECT well_id,parameter,timestamp,value,
AVG(value) OVER(PARTITION BY well_id,parameter ORDER BY timestamp
 ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING) preceding_24_records_mean
FROM observations;
