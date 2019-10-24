DROP TABLE IF EXISTS feature.oa_walkable_stops;

CREATE TABLE feature.oa_walkable_stops_ AS (
    SELECT DISTINCT (o.oa11),
        o.centroid,
        s.stop_id,
        s.location AS stop_location
    FROM semantic.oa o
    LEFT JOIN cleaned.gtfs_stops s ON ST_DWithin (o.centroid,
        s.location,
        400)
);

create index oa_walkable_oa_idx on feature.oa_walkable_stops(oa11);
create index oa_walkable_stop_id_idx on feature.oa_walkable_stops(stop_id);

DROP TABLE IF EXISTS feature.poi_walkable_stops;

CREATE TABLE feature.poi_walkable_stops AS (
    SELECT DISTINCT (p.id),
        p.location AS poi_location,
        s.stop_id,
        s.location AS stop_location
    FROM semantic.poi p
    LEFT JOIN cleaned.gtfs_stops s ON ST_DWithin (p.location,
        s.location,
        400)
);

create index poi_walkable_oa_idx on feature.poi_walkable_stops(id);
create index poi_walkable_stop_id_idx on feature.poi_walkable_stops(stop_id);

