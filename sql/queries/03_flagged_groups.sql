SELECT well_id,parameter,COUNT(*) records,SUM(flag!='') flagged,
1.0*SUM(flag!='')/COUNT(*) flagged_fraction
FROM observations GROUP BY well_id,parameter HAVING SUM(flag!='')>0;
