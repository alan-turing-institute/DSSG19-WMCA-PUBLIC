DROP TABLE IF EXISTS vis.map_attributes;

CREATE TABLE vis.map_attributes AS(

    WITH array_table AS(
	SELECT trip_id,
	        ARRAY{metric_arr} AS metric_arr,
            ARRAY{value_arr} AS value_arr
	FROM results.trips
	ORDER BY trip_id
    ),

    long_res AS(
        SELECT trip_id,
            UNNEST(metric_arr) AS metric,
            UNNEST(value_arr) AS value
        FROM array_table
    ),

    full_res AS(
        SELECT r.*, m.oa_id, o.centroid AS oa_centroid, m.poi_id, p.type AS poi_type, t.stratum
        FROM long_res r
        INNER JOIN model.trips m USING (trip_ID)
        INNER JOIN model.timestamps t USING (date, time)
        INNER JOIN semantic.poi p ON m.poi_id=p.id
        INNER JOIN semantic.oa o ON m.oa_id=o.oa11
    ),

    median AS(
        SELECT oa_id, oa_centroid, poi_id, poi_type, stratum, metric,
            PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY value) AS value
        FROM full_res
        GROUP BY oa_id, oa_centroid, poi_id, poi_type, stratum, metric
    ),

    median_all_time AS(
        SELECT oa_id, oa_centroid, poi_id, poi_type, 'All times' AS stratum, metric,
        		PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY value) AS value
        FROM full_res
        GROUP BY oa_id, oa_centroid, poi_id, poi_type, metric
    ),

    m AS(
        SELECT * FROM median
            UNION ALL
            SELECT * FROM median_all_time
    )
    
    SELECT oa_id, oa_centroid, poi_type, stratum, metric, MIN(value) as value
    FROM m
    GROUP BY oa_id, oa_centroid, poi_type, stratum, metric
);
