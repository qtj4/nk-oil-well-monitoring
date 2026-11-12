SELECT o.well_id,w.well_type,o.parameter,p.unit,COUNT(*) records,
COUNT(o.value) valid_values,MIN(timestamp) first_time,MAX(timestamp) last_time
FROM observations o JOIN wells w USING(well_id) JOIN parameters p USING(parameter)
GROUP BY o.well_id,o.parameter;
