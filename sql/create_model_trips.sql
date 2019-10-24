DROP TABLE if exists model.trips{suffix};

CREATE TABLE model.trips{suffix} AS (
    SELECT
        row_number() over () as trip_id,
        oa_id,
        poi_id,
        date,
        time,
        0 AS computed
    FROM model.k_poi{suffix}
    CROSS JOIN model.timestamps{suffix}
);

ALTER TABLE model.trips{suffix} ADD PRIMARY KEY (trip_id);

CREATE INDEX IF NOT EXISTS trip_id_idx{suffix} on model.trips{suffix}(trip_id);
CREATE INDEX IF NOT EXISTS oa_id_idx{suffix} on model.trips{suffix}(oa_id);
CREATE INDEX IF NOT EXISTS poi_id_idx{suffix} on model.trips{suffix}(poi_id);
