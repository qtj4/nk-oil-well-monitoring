SELECT w.well_type,o.parameter,p.unit,COUNT(DISTINCT o.well_id) wells,
COUNT(*) records,AVG(o.value) mean_value,SUM(o.value IS NULL) null_values
FROM observations o JOIN wells w USING(well_id) JOIN parameters p USING(parameter)
GROUP BY w.well_type,o.parameter;
