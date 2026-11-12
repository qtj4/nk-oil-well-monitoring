SELECT well_id,parameter,substr(timestamp,1,7) month,COUNT(*) records,
AVG(value) mean_value,MIN(value) minimum,MAX(value) maximum
FROM observations GROUP BY well_id,parameter,month;
