/*
The following code generates geopoints for hospitals and OA centroids, 
then computes, for each OA centroid, the distance to all hospitals 
within 5000 meters. 

The last passage gets the mean distance to hospital for each OA centroid.

The distance of 5000 meters can be a variable parameter in future models. 
*/

DROP TABLE IF EXISTS results.model_results;

CREATE TABLE results.model_results AS (
    WITH elderly_pop AS (
        SELECT oa11,
            (age_75_to_84 + age_85_to_89 + age_90_plus) AS pop
        FROM cleaned.ONS_age_structure_wm),

        hospital AS (
            SELECT organisationid,
                ST_SetSRID (ST_MakePoint (longitude::float, latitude::float), 4326)::geography AS loc
            FROM cleaned.nhs_hospitals_wm),

            oa_centroid AS (
                SELECT oa11, centroid
                FROM semantic.oa),

                geo AS (
                    SELECT o.oa11,
                        ST_Distance (h.loc, o.centroid) AS distance
                    FROM hospital h,
                        oa_centroid o
                    WHERE ST_Distance (h.loc, o.centroid) < 5000) -- 5000 meters is an arbitrary distance

                    SELECT 1 as model_id, 
                        geo.oa11 as oa, 
                    	avg(geo.distance) AS value, 
                    	e.pop AS population
                    FROM geo
                        INNER JOIN elderly_pop e ON geo.oa11 = e.oa11
                    GROUP BY geo.oa11, e.pop
);


