WITH joined AS (
    SELECT m.oa,
        m.population,
        m.value,
        b.wkb_geography
    FROM cleaned.oa_boundaries_wm b
        INNER JOIN results.model_results m ON b.oa11cd = m.oa
    WHERE m.model_id = 1
)
SELECT jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_agg(features.feature))
FROM (
    SELECT json_build_object(
        'type', 'Feature', 
        'id', oa, 
        'geometry', st_asgeojson (wkb_geography)::json, 
        'properties', json_build_object(
            'population', population, 
            'value', value)) AS feature
    FROM (
        SELECT *
        FROM joined) inputs) AS features;

