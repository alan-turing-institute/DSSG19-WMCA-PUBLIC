DROP TABLE IF EXISTS model.k_poi{suffix};

CREATE TABLE IF NOT EXISTS model.k_poi{suffix} AS (

    WITH poi AS (
        SELECT
            id as poi_id,
            type as poi_type,
            snapped_latitude as poi_latitude,
            snapped_longitude as poi_longitude,
            snapped_location::geography AS poi_location
        FROM semantic.poi),

    oa_ptype AS (
        SELECT
            oa11 AS oa_id,
            centroid::geography AS oa_centroid,
            ptype.*
        FROM semantic.oa
        CROSS JOIN LATERAL (
            SELECT
                UNNEST(ARRAY{poi_types}) AS poi_type,
                UNNEST(ARRAY{poi_Ks}) AS poi_K
        ) AS ptype
    )

    SELECT
        oa_ptype.oa_id, oa_ptype.oa_centroid,
        p.*,
        ST_Distance(oa_ptype.oa_centroid, p.poi_location) AS distance
    FROM oa_ptype
    CROSS JOIN LATERAL (
        SELECT
            poi.*,
            RANK() OVER (ORDER BY poi.poi_location <-> oa_ptype.oa_centroid) AS rank
        FROM poi
        WHERE oa_ptype.poi_type=poi.poi_type
    ) AS p
    WHERE rank <= poi_K
);
