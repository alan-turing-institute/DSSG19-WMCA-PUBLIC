
DROP TABLE if exists semantic.oa CASCADE;
CREATE TABLE semantic.oa AS (
    WITH oa_geo AS(
        SELECT
            oa11cd as oa11,
            geometry,
            centroid,
            snapped_centroid as snapped_centroid, -- Taking only the snapped one
            latitude as snapped_latitude,
            longitude as snapped_longitude
        FROM cleaned.oa_boundaries_wm_snapped
    ),
    oa_demo AS(
        SELECT *
        FROM cleaned.ons_age_structure_wm
        FULL JOIN cleaned.ons_car_availability_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_disability_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_employment_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_approx_social_grade_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_birth_country_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_deprivation_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_english_proficiency_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_ethnicity_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_lone_parent_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_students_wm USING (year, oa11, geography)
        FULL JOIN cleaned.ons_usual_residents_wm USING (year, oa11, geography)
    ),
    oa_lsoa_lookup AS(
        SELECT DISTINCT ON (oa11)
            oa11,
            lsoa11            
        FROM cleaned.pcd_centroids_wm
    )
    SELECT * FROM oa_geo
    FULL JOIN oa_demo USING (oa11)
    FULL JOIN oa_lsoa_lookup USING (oa11)
);
ALTER TABLE semantic.oa
    ADD PRIMARY KEY (oa11);


-- Postcode table
DROP TABLE if exists semantic.pcd CASCADE;
CREATE TABLE semantic.pcd AS(
    SELECT * FROM cleaned.pcd_centroids_wm
);
ALTER TABLE semantic.pcd
    ADD PRIMARY KEY (pcd),
    ADD FOREIGN KEY (oa11) REFERENCES semantic.oa(oa11);


-- POI
DROP TABLE if exists semantic.poi;
CREATE TABLE semantic.poi (
    type varchar,
    name varchar,
    snapped_latitude float,
    snapped_longitude float,
    snapped_location geometry(Point, 4326)
);

-- insert hospitals
INSERT INTO semantic.poi
    SELECT
        organisationtype as type,
        organisationname as name,
        latitude as snapped_latitude, 
        longitude as snapped_longitude, 
        location as snapped_location
    FROM cleaned.nhs_hospitals_wm
;

-- insert job centres
INSERT INTO semantic.poi
    SELECT
        type,
        name,
        latitude as snapped_latitude,
        longitude as snapped_latitude,
        snapped_location
    FROM cleaned.ukgov_job_centres_wm_snapped
;

-- insert strategic centres
INSERT INTO semantic.poi
    SELECT
        type,
        name,
        latitude as snapped_latitude,
        longitude as snapped_longitude,
        snapped_location
    FROM cleaned.ukgov_strategic_centres_wm_snapped
;

-- insert schools
INSERT INTO semantic.poi 
    SELECT
        type,
        name,
        latitude as snapped_latitude,
        longitude as snapped_longitude,
        snapped_location
    FROM cleaned.ukgov_schools_wm_snapped
;

-- insert childcare
INSERT INTO semantic.poi 
    SELECT
        type,
        name,
        latitude as snapped_latitude,
        longitude as snapped_longitude,
        snapped_location
    FROM cleaned.ofsted_childcare_wm_snapped
;

-- insert rail stations
INSERT INTO semantic.poi
    SELECT
        type,
        name,
        latitude as snapped_latitude,
        longitude as snapped_longitude,
        snapped_location
    FROM cleaned.wmca_rail_stations_wm_snapped
;

ALTER TABLE semantic.poi
    ADD COLUMN ID serial, -- unique ID
    ADD PRIMARY KEY (ID);

