DROP TABLE if exists model.trips{suffix}_new;
CREATE TABLE model.trips{suffix}_new AS (
WITH appended AS (
    SELECT trip_id, oa_id, poi_id, date, time, computed
    FROM model.trips{suffix}
    UNION ALL
    SELECT
    	NULL AS trip_id, oa_id, poi_id, date, time, 0 AS computed
    FROM model.k_poi{suffix}
    CROSS JOIN model.timestamps{suffix}
),
  cleaned AS (
    SELECT DISTINCT
        first_value(trip_id) over w as trip_id_raw,
        oa_id,
        poi_id,
        date,
        time,
        MAX(computed) over w AS computed
    FROM appended
    window w as (partition by oa_id, poi_id, date, time)
)
SELECT
    CASE
        WHEN trip_id_raw IS NOT NULL THEN trip_id_raw
        ELSE ROW_NUMBER() OVER(PARTITION BY trip_id_raw) + MAX(trip_id_raw) OVER()
    END AS trip_id,
    oa_id,
    poi_id,
    date,
    time,
    computed
FROM cleaned
);

DROP TABLE if exists model.trips{suffix};
ALTER TABLE model.trips{suffix}_new RENAME TO trips{suffix};
ALTER TABLE model.trips{suffix} ADD PRIMARY KEY (trip_id);

CREATE INDEX IF NOT EXISTS trip_id_idx{suffix} on model.trips{suffix}(trip_id);
CREATE INDEX IF NOT EXISTS oa_id_idx{suffix} on model.trips{suffix}(oa_id);
CREATE INDEX IF NOT EXISTS poi_id_idx{suffix} on model.trips{suffix}(poi_id);
