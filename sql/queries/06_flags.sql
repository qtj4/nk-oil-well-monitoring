SELECT flag,COUNT(*) records,COUNT(DISTINCT well_id) wells
FROM observations GROUP BY flag ORDER BY records DESC;
