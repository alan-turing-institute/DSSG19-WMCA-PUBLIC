-- Baseline: # of different transport stations per postcode
DROP TABLE if exists baseline.baseline_pcd_results;

CREATE TABLE baseline.pcd_results AS (
    WITH points AS (
        SELECT pcd,
            ST_SetSRID(ST_MakePoint(long, lat), 4326)::geography AS centroid
        FROM cleaned.pcd_centroids_wm
    ),
      bus_stops AS (
        SELECT DISTINCT ON (commonname, street, town) commonname, street, town, naptancode,
            ST_SetSRID(ST_MakePoint (longitude, latitude), 4326)::geography AS location
        FROM cleaned.naptan_stops
        WHERE stoptype IN ('BCT', 'BCS')
    ),
      metro_stops AS(
        SELECT DISTINCT ON (commonname, street, town) commonname, street, town, naptancode,
            ST_SetSRID(ST_MakePoint (longitude, latitude), 4326)::geography AS location
        FROM cleaned.naptan_stops
        WHERE stoptype = 'TMU'
    ),
      rail_stops AS (
        SELECT DISTINCT ON (commonname, street, town) commonname, street, town, naptancode,
            ST_SetSRID(ST_MakePoint (longitude, latitude), 4326)::geography AS location
        FROM cleaned.naptan_stops
        WHERE stoptype = 'RSE'
    )
    
    SELECT p.pcd, p.centroid,
        count(bs.location) AS count_bus_stops_400m,
        count(ms.location) AS count_metro_stops_600m,
        count(rs.location) AS count_rail_stops_800m,
        CASE WHEN count(bs.location) > 0 THEN 1 ELSE 0 END AS has_bus_access,
        CASE WHEN count(ms.location) > 0 THEN 1 ELSE 0 END AS has_metro_access,
        CASE WHEN count(rs.location) > 0 THEN 1 ELSE 0 END AS has_rail_access
    FROM points p
    LEFT OUTER JOIN bus_stops bs ON ST_DWithin (p.centroid, bs.location, 400)
    LEFT OUTER JOIN metro_stops ms ON ST_DWithin (p.centroid, ms.location, 600)
    LEFT OUTER JOIN rail_stops rs ON ST_DWithin (p.centroid, rs.location, 800)
    GROUP BY p.pcd, p.centroid
);


-- Baseline: # of different transport stations per oa
DROP TABLE if exists baseline.oa_results;

CREATE TABLE baseline.oa_results AS (
    SELECT count(*) as pcd_count,
        avg(r.has_bus_access) AS pct_bus_access,
        avg(r.has_metro_access) AS pct_metro_access,
        avg(r.has_rail_access) AS pct_rail_access,
        CASE WHEN avg(r.has_bus_access) = 1 THEN 1 ELSE 0 END AS pass_bus_access,
        CASE WHEN avg(r.has_metro_access) = 1 THEN 1 ELSE 0 END AS pass_metro_access,
        CASE WHEN avg(r.has_rail_access) = 1 THEN 1 ELSE 0 END AS pass_rail_access
    FROM baseline.pcd_results r
    INNER JOIN cleaned.pcd_oa_lookup_wm l ON r.pcd = l.pcd7
    GROUP BY l.oa11
);
