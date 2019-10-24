
DROP TABLE IF EXISTS wm_la;
CREATE TEMPORARY TABLE wm_la AS ( 
	SELECT lad16cd, lad16nm, cty16nm FROM raw.ons_la_county_lookup
        WHERE cty16nm='West Midlands');

-- raw.ONS_pcd_centroids --> cleaned.pcd_centroids_wm

DROP TABLE IF EXISTS cleaned.pcd_centroids_wm;

CREATE TABLE cleaned.pcd_centroids_wm AS (
    SELECT  trim(regexp_replace(c.pcd, '\s+', ' ', 'g')) AS pcd,
            c.oa11,
            c.lsoa11, 
            c.msoa11, 
            ST_SetSRID(ST_MakePoint(c.long::float, c.lat::float), 4326) AS centroid, -- this sets the ROW SRID as 4326
            c.long as lon,
            c.lat as lat,
            w.cty16nm 
        FROM raw.ONS_pcd_centroids c
        INNER JOIN wm_la w 
		ON c.laua = w.lad16cd -- filter to WM
);

ALTER TABLE cleaned.pcd_centroids_wm
    ADD PRIMARY KEY (pcd),
    ALTER COLUMN centroid TYPE geometry(Point, 4326); -- this sets the GEOM COLUMN SRID as 4326

CREATE INDEX LSOA_co ON cleaned.pcd_centroids_wm (pcd);


-- Take the raw OA boundaries for all UK and filter to West Midlands

DROP TABLE IF EXISTS cleaned.oa_boundaries_wm CASCADE;

CREATE TABLE cleaned.oa_boundaries_wm (
    ogc_fid integer,
    objectid numeric,
    oa11cd varchar,
    lad11cd varchar,
    st_areasha numeric,
    st_lengths numeric,
    geometry geometry(MultiPolygon, 4326), -- this sets the GEOM COLUMN SRID as 4326
    centroid geometry(Point, 4326) -- this sets the GEOM COLUMN SRID as 4326
);

INSERT INTO cleaned.oa_boundaries_wm
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
    )
    SELECT
        ogc_fid,
        objectid,
        oa11cd,
        lad11cd,
        st_areasha,
        st_lengths,
        ST_Transform(wkb_geometry, 4326) AS geometry, -- this sets the ROW SRID (?) as 4326
        ST_Transform(ST_Centroid(wkb_geometry), 4326) AS centroid
    FROM gis.oa_boundaries_all oa
    INNER JOIN distinct_wm_oa p ON p.oa11 = oa.oa11cd
;
CREATE INDEX oa_spatial_idx ON cleaned.oa_boundaries_wm USING gist(geometry);

-- raw.ONS_KS102UK_age_structure --> cleaned.ONS_age_structure_wm
DROP TABLE IF EXISTS cleaned.ONS_age_structure_wm;

CREATE TABLE cleaned.ONS_age_structure_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT r.*
    FROM raw.ONS_KS102UK_age_structure r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_age_structure_wm
    ADD PRIMARY KEY (oa11),
	ALTER COLUMN date_ TYPE INT using date_::integer,
	ALTER COLUMN age_all_residents TYPE INT using age_all_residents::integer,
	ALTER COLUMN age_0_to_5 TYPE INT using age_0_to_5::integer,
	ALTER COLUMN age_5_to_7 TYPE INT using age_5_to_7::integer,
	ALTER COLUMN age_8_to_9 TYPE INT using age_8_to_9::integer,
	ALTER COLUMN age_10_to_14 TYPE INT using age_10_to_14::integer,
	ALTER COLUMN age_15 TYPE INT using age_15::integer,
	ALTER COLUMN age_16_to_17 TYPE INT using age_16_to_17::integer,
	ALTER COLUMN age_18_to_19 TYPE INT using age_18_to_19::integer,
	ALTER COLUMN age_20_to_24 TYPE INT using age_20_to_24::integer,
	ALTER COLUMN age_25_to_29 TYPE INT using age_25_to_29::integer,
	ALTER COLUMN age_30_to_44 TYPE INT using age_30_to_44::integer,
	ALTER COLUMN age_45_to_59 TYPE INT using age_45_to_59::integer,
	ALTER COLUMN age_60_to_64 TYPE INT using age_60_to_64::integer,
	ALTER COLUMN age_65_to_74 TYPE INT using age_65_to_74::integer,
	ALTER COLUMN age_75_to_84 TYPE INT using age_75_to_84::integer,
	ALTER COLUMN age_85_to_89 TYPE INT using age_85_to_89::integer,
	ALTER COLUMN age_90_plus TYPE INT using age_90_plus::integer,
	ALTER COLUMN age_mean TYPE float using age_mean::double precision,
	ALTER COLUMN age_median TYPE float using age_median::double precision;

ALTER TABLE cleaned.ONS_age_structure_wm
    RENAME COLUMN date_ TO year;

-- raw.ONS_KS404UK_car_availability --> cleaned.ONS_car_availability_wm

DROP TABLE IF EXISTS cleaned.ONS_car_availability_wm;

CREATE TABLE cleaned.ONS_car_availability_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT r.*
    FROM raw.ONS_KS404UK_car_availability r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_car_availability_wm
	ADD PRIMARY KEY (oa11),
	ALTER COLUMN date_ TYPE INT using date_::integer,
	ALTER COLUMN cars_all_households TYPE INT using cars_all_households::integer,
	ALTER COLUMN cars_no_car TYPE INT using cars_no_car::integer,
	ALTER COLUMN cars_1_car TYPE INT using cars_1_car::integer,
	ALTER COLUMN cars_3_cars TYPE INT using cars_3_cars::integer,
	ALTER COLUMN cars_4_plus_cars TYPE INT using cars_4_plus_cars::integer,
	ALTER COLUMN cars_sum_of_cars TYPE INT using cars_sum_of_cars::integer;

ALTER TABLE cleaned.ONS_car_availability_wm
    RENAME COLUMN date_ TO year;

-- raw.ONS_QS303EW_disability --> cleaned.ONS_disability_wm

DROP TABLE IF EXISTS cleaned.ONS_disability_wm;

CREATE TABLE cleaned.ONS_disability_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT r.*
    FROM raw.ons_qs303ew_disability r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_disability_wm
	ADD PRIMARY KEY (oa11),
	ALTER COLUMN date_ TYPE INT using date_::integer,
	ALTER COLUMN disability_all TYPE INT using disability_all::integer,
	ALTER COLUMN disability_severe TYPE INT using disability_severe::integer,
	ALTER COLUMN disability_moderate TYPE INT using disability_moderate::integer,
	ALTER COLUMN disability_none TYPE INT using disability_none::integer;

ALTER TABLE cleaned.ONS_disability_wm
    RENAME COLUMN date_ TO year;

-- raw.ONS_KS601UK_employment --> cleaned.ONS_employment_wm

DROP TABLE IF EXISTS cleaned.ONS_employment_wm;

CREATE TABLE cleaned.ONS_employment_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT r.*
    FROM raw.ons_ks601uk_employment r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_employment_wm
	ADD PRIMARY KEY (oa11),
	ALTER COLUMN date_ TYPE INT using date_::integer,
	ALTER COLUMN emp_all_residents_16_to_74 TYPE INT using emp_all_residents_16_to_74::integer,
	ALTER COLUMN emp_active TYPE INT using emp_active::integer,
	ALTER COLUMN emp_active_in_employment TYPE INT using emp_active_in_employment::integer,
	ALTER COLUMN emp_active_part_time TYPE INT using emp_active_part_time::integer,
	ALTER COLUMN emp_active_full_time TYPE INT using emp_active_full_time::integer,
	ALTER COLUMN emp_active_self_employed TYPE INT using emp_active_self_employed::integer,
	ALTER COLUMN emp_active_unemployed TYPE INT using emp_active_unemployed::integer,
	ALTER COLUMN emp_active_full_time_student TYPE INT using emp_active_full_time_student::integer,
	ALTER COLUMN emp_inactive TYPE INT using emp_inactive::integer,
	ALTER COLUMN emp_inactive_retired TYPE INT using emp_inactive_retired::integer,
	ALTER COLUMN emp_inactive_student TYPE INT using emp_inactive_student::integer,
	ALTER COLUMN emp_inactive_homemaking TYPE INT using emp_inactive_homemaking::integer,
	ALTER COLUMN emp_inactive_disabled TYPE INT using emp_inactive_disabled::integer,
	ALTER COLUMN emp_inactive_other TYPE INT using emp_inactive_other::integer,
	ALTER COLUMN emp_unemployed_16_to_24 TYPE INT using emp_unemployed_16_to_24::integer,
	ALTER COLUMN emp_unemployed_50_to_74 TYPE INT using emp_unemployed_50_to_74::integer,
	ALTER COLUMN emp_unemployed_never_worked TYPE INT using emp_unemployed_never_worked::integer,
	ALTER COLUMN emp_unemployed_long_term_unemployed TYPE INT using emp_unemployed_long_term_unemployed::integer;

ALTER TABLE cleaned.ONS_employment_wm
    RENAME COLUMN date_ TO year;

-- raw.ONS_KS201UK_ethnicity --> cleaned.ONS_ethnicity_wm

DROP TABLE IF EXISTS cleaned.ONS_ethnicity_wm;

CREATE TABLE cleaned.ONS_ethnicity_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.all_::int as eth_all,
        r.white::int as eth_white,
        r.gypsy::int as eth_gypsy,
        r.mixed::int as eth_mixed,
        r.asian_indian::int as eth_asian_indian,
        r.asian_pakistani::int as eth_asian_pakistani,
        r.asian_bangladeshi::int as eth_asian_bangladeshi,
        r.asian_chinese::int as eth_asian_chinese,
        r.asian_other::int as eth_asian_other,
        r.black::int as eth_black,
        r.other::int as eth_other
    FROM raw.ons_ks201uk_ethnicity r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_ethnicity_wm
    ADD PRIMARY KEY (oa11);


-- raw.ONS_KS101UK_usual_residents --> cleaned.ONS_usual_residents_wm

DROP TABLE IF EXISTS cleaned.ONS_usual_residents_wm;

CREATE TABLE cleaned.ONS_usual_residents_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.all_usual_residents::int as usual_residents_all,
        r.males::int as usual_residents_males,
        r.females::int as usual_residents_females,
        r.lives_in_household::int as usual_residents_lives_in_household,
        r.lives_in_communal_establishment::int as usual_residents_lives_in_communal_establishment,
        r.student::int as usual_residents_student,
        r.area_hectares::float as usual_residents_area_hectares,
        r.density_persons_per_hectare::float as usual_residents_density_persons_per_hectare
    FROM raw.ons_ks101uk_usual_residents r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_usual_residents_wm
    ADD PRIMARY KEY (oa11);


-- raw.ONS_KS107UK_lone_parent --> cleaned.ONS_lone_parent_wm

DROP TABLE IF EXISTS cleaned.ONS_lone_parent_wm;

CREATE TABLE cleaned.ONS_lone_parent_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.lone_parent_total_hh::int as lone_parent_total,
        r.lone_parent_part_time_emp::int as lone_parent_part_time_emp,
        r.lone_parent_full_time_emp::int as lone_parent_full_time_emp,
        r.lone_parent_no_emp::int as lone_parent_no_emp,
        r.male_lone_parent_total::int as lone_parent_total_male,
        r.male_lone_parent_part_time_emp::int as lone_parent_part_time_emp_male,
        r.male_lone_parent_full_time_emp::int as lone_parent_full_time_emp_male,
        r.male_lone_parent_no_emp::int as lone_parent_no_emp_male,
        r.female_lone_parent_total::int as lone_parent_total_female,
        r.female_lone_parent_part_time_emp::int as lone_parent_part_time_emp_female,
        r.female_lone_parent_full_time_emp::int as lone_parent_full_time_emp_female,
        r.female_lone_parent_no_emp::int as lone_parent_no_emp_female
    FROM raw.ons_ks107uk_lone_parent r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_lone_parent_wm
    ADD PRIMARY KEY (oa11);

-- raw.ONS_KS501UK_students --> cleaned.ONS_students_wm

DROP TABLE IF EXISTS cleaned.ONS_students_wm;

CREATE TABLE cleaned.ONS_students_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.highest_qual_all::int as students_highest_qual_all,
        r.no_qual::int as students_no_qual,
        r.highest_qual_level_1::int as students_highest_qual_level_1,
        r.highest_qual_level_2::int as students_highest_qual_level_2,
        r.highest_qual_apprenticeship::int as students_highest_qual_apprenticeship,
        r.highest_qual_level_3::int as students_highest_qual_level_3,
        r.highest_qual_level_4_above::int as students_highest_qual_level_4_above,
        r.highest_qual_other::int as students_highest_qual_other,
        r.schoolchildren_students_16_to_17::int as students_16_to_17,
        r.schoolchildren_students_18_plus::int as students_18_plus,
        r.students_employed::int as students_employed,
        r.students_unemployed::int as students_unemployed,
        r.students_econ_inactive::int as students_econ_inactive
    FROM raw.ons_ks501uk_students r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_students_wm
    ADD PRIMARY KEY (oa11);

-- raw.ONS_QS203UK_birth_country --> cleaned.ONS_birth_country_wm

DROP TABLE IF EXISTS cleaned.ONS_birth_country_wm;

CREATE TABLE cleaned.ONS_birth_country_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.all_categories::int as birth_country_all,
        europe_total::int as birth_country_europe_total,
        europe_uk_total::int as birth_country_europe_uk_total,
        europe_uk_england::int as birth_country_europe_uk_england,
        europe_uk_n_ireland::int as birth_country_europe_uk_n_ireland,
        europe_uk_scotland::int as birth_country_europe_uk_scotland,
        europe_uk_wales::int as birth_country_europe_uk_wales,
        europe_uk_other::int as birth_country_europe_uk_other,
        europe_channel_islands::int as birth_country_europe_channel_islands,
        europe_ireland::int as birth_country_europe_ireland,
        europe_other_total::int as birth_country_europe_other_total,
        europe_other_eu_total::int as birth_country_europe_other_eu_total,
        europe_other_eu_germany::int as birth_country_europe_other_eu_germany,
        europe_other_eu_lithuania::int as birth_country_europe_other_eu_lithuania,
        europe_other_eu_poland::int as birth_country_europe_other_eu_poland,
        europe_other_eu_romania::int as birth_country_europe_other_eu_romania,
        europe_other_eu_other::int as birth_country_europe_other_eu_other,
        europe_other_rest_total::int as birth_country_europe_other_rest_total,
        europe_other_rest_turkey::int as birth_country_europe_other_rest_turkey,
        europe_other_rest_other::int as birth_country_europe_other_rest_other,
        africa_total::int as birth_country_africa_total,
        africa_n::int as birth_country_africa_n,
        africa_cw_total::int as birth_country_africa_cw_total,
        africa_cw_nigeria::int as birth_country_africa_cw_nigeria,
        africa_cw_other::int as birth_country_africa_cw_other,
        africa_se_total::int as birth_country_africa_se_total,
        africa_se_kenya::int as birth_country_africa_se_kenya,
        africa_se_south_africa::int as birth_country_africa_se_south_africa,
        africa_se_zimbabwe::int as birth_country_africa_se_zimbabwe,
        africa_se_other::int as birth_country_africa_se_other,
        mideast_asia_total::int as birth_country_mideast_asia_total,
        mideast_asia_mideast_total::int as birth_country_mideast_asia_mideast_total,
        mideast_asia_mideast_iran::int as birth_country_mideast_asia_mideast_iran,
        mideast_asia_mideast_other::int as birth_country_mideast_asia_mideast_other,
        mideast_asia_east_asia_total::int as birth_country_mideast_asia_east_asia_total,
        mideast_asia_east_asia_china::int as birth_country_mideast_asia_east_asia_china,
        mideast_asia_east_asia_hong_kong::int as birth_country_mideast_asia_east_asia_hong_kong,
        mideast_asia_east_asia_other::int as birth_country_mideast_asia_east_asia_other,
        mideast_asia_south_asia_total::int as birth_country_mideast_asia_south_asia_total,
        mideast_asia_south_asia_bangladesh::int as birth_country_mideast_asia_south_asia_bangladesh,
        mideast_asia_south_asia_india::int as birth_country_mideast_asia_south_asia_india,
        mideast_asia_south_asia_pakistan::int as birth_country_mideast_asia_south_asia_pakistan,
        mideast_asia_south_asia_other::int as birth_country_mideast_asia_south_asia_other,
        mideast_asia_se_asia_total::int as birth_country_mideast_asia_se_asia_total,
        mideast_asia_central_asia_total::int as birth_country_mideast_asia_central_asia_total,
        americas_total::int as birth_country_americas_total,
        americas_north_america_total::int as birth_country_americas_north_america_total,
        americas_north_america_caribbean::int as birth_country_americas_north_america_caribbean,
        americas_north_america_usa::int as birth_country_americas_north_america_usa,
        americas_north_america_other::int as birth_country_americas_north_america_other,
        americas_central_america::int as birth_country_americas_central_america,
        americas_south_america::int as birth_country_americas_south_america,
        antarctica_oceania_total::int as birth_country_antarctica_oceania_total,
        antarctica_oceania_australia::int as birth_country_antarctica_oceania_australia,
        antarctica_oceania_other::int as birth_country_antarctica_oceania_other,
        other::int as birth_country_other
    FROM raw.ons_qs203uk_birth_country r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_birth_country_wm
    ADD PRIMARY KEY (oa11);

-- raw.ONS_QS205EW_english_proficiency --> cleaned.ONS_english_proficiency_wm

DROP TABLE IF EXISTS cleaned.ONS_english_proficiency_wm;

CREATE TABLE cleaned.ONS_english_proficiency_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.rural_urban::varchar as eng_prof_rural_urban,
        r.all_::int as eng_prof_all,
        r.main_english::int as eng_prof_main_english,
        r.main_not_english_very_well::int as eng_prof_main_not_english_very_well,
        r.main_not_english_not_well::int as eng_prof_main_not_english_not_well,
        r.main_not_english_cannot::int as eng_prof_main_not_english_cannot
    FROM raw.ons_qs205ew_english_proficiency r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_english_proficiency_wm
    ADD PRIMARY KEY (oa11);

-- raw.ONS_QS119ew_deprivation --> cleaned.ONS_deprivation_wm

DROP TABLE IF EXISTS cleaned.ONS_deprivation_wm;

CREATE TABLE cleaned.ONS_deprivation_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.rural_urban::varchar as deprived_rural_urban,
        r.all_::int as deprived_all,
        r.deprived_0_dim::int as deprived_0_dim,
        r.deprived_1_dim::int as deprived_1_dim,
        r.deprived_2_dim::int as deprived_2_dim,
        r.deprived_3_dim::int as deprived_3_dim,
        r.deprived_4_dim::int as deprived_4_dim
    FROM raw.ons_qs119ew_deprivation r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_deprivation_wm
    ADD PRIMARY KEY (oa11);

-- raw.ONS_QS613ew_approx_social_grade --> cleaned.ONS_approx_social_grade_wm

DROP TABLE IF EXISTS cleaned.ONS_approx_social_grade_wm;

CREATE TABLE cleaned.ONS_approx_social_grade_wm AS (
    WITH distinct_wm_oa AS (
        SELECT DISTINCT oa11
        FROM cleaned.pcd_centroids_wm -- this has 8461 rows
)
    SELECT 
        r.date_::int as year,
        r.oa11::varchar as oa11,
        r.geography::varchar as geography,
        r.all_::int as grade_all,
        r.grade_ab::int as grade_ab,
        r.grade_c1::int as grade_c1,
        r.grade_c2::int as grade_c2,
        r.grade_de::int as grade_de
    FROM raw.ons_qs613ew_approx_social_grade r
        INNER JOIN distinct_wm_oa l ON r.oa11 = l.oa11 -- filter to WM
);

ALTER TABLE cleaned.ONS_approx_social_grade_wm
    ADD PRIMARY KEY (oa11);


-- raw.NHS_hospitals --> cleaned.NHS_hospitals

DROP TABLE IF EXISTS cleaned.nhs_hospitals_wm;

CREATE TABLE cleaned.nhs_hospitals_wm AS(

    WITH

    hospitals AS (
        SELECT r.organisationid,
                r.organisationcode,
                initcap(r.organisationtype) as organisationtype,
                r.subtype,
                r.sector,
                r.organisationstatus,
                r.ispimsmanaged,
                r.organisationname,
                r.address1,
                r.address2,
                r.address3,
                r.city,
                r.county,
                r.postcode,
                r.latitude::float,
                r.longitude::float,
                r.parentodscode,
                r.parentname,
                r.phone,
                r.email,
                r.website,
                r.fax,
                ST_SetSRID(ST_MakePoint(r.longitude::float, r.latitude::float), 4326) AS location -- this sets the ROW SRID as 4326
        FROM raw.NHS_hospitals r
        INNER JOIN cleaned.pcd_centroids_wm l
        ON r.postcode = l.pcd -- filter to WM
	)

	SELECT
	    DISTINCT ON (longitude, latitude) -- drop duplicates. This also drops job centres outside WM.
	    *
	FROM hospitals
);

ALTER TABLE cleaned.nhs_hospitals_wm
    ADD PRIMARY KEY (OrganisationID),  
    ALTER COLUMN IsPimsManaged TYPE boolean using IsPimsManaged::boolean,
    ALTER COLUMN location TYPE geometry(Point, 4326); -- this sets the GEOM COLUMN SRID as 4326

-- raw.ukgov_job_centres_wm --> cleaned.ukgov_job_centres_wm

DROP TABLE IF EXISTS cleaned.ukgov_job_centres_wm;

CREATE TABLE cleaned.ukgov_job_centres_wm AS (

    WITH

    job_centres AS (

        SELECT l.name,
               l.pcd,
               initcap(type) as type,
               lon,
               lat,
               ST_SetSRID(ST_MakePoint(r.lon::float, r.lat::float), 4326) AS pcd_centroid -- postcode centroid
        FROM raw.ukgov_job_centres_wm l
        LEFT JOIN cleaned.pcd_centroids_wm r
        ON l.pcd = r.pcd -- no filtering! Includes job centres outside of west midlands
	)

	SELECT
	    DISTINCT ON (lon, lat) -- drop duplicates. This also drops job centres outside WM.
	    *
	FROM job_centres
	WHERE lon IS NOT NULL
);

ALTER TABLE cleaned.ukgov_job_centres_wm
    ADD PRIMARY KEY (name),
    ALTER COLUMN pcd_centroid TYPE geometry(Point, 4326), -- this sets the GEOM COLUMN SRID as 4326
    DROP COLUMN lon, -- dropping so that semantic contains only the snapped lon and lat
    DROP COLUMN lat;
CREATE INDEX ukgov_job_centres_wm_cent_idx ON cleaned.ukgov_job_centres_wm USING gist(pcd_centroid);

-- raw.ukgov_strategic_centres_wm --> cleaned.ukgov_strategic_centres_wm

DROP TABLE IF EXISTS cleaned.ukgov_strategic_centres_wm;

CREATE TABLE cleaned.ukgov_strategic_centres_wm AS(
    SELECT name,
           lon::float,
           lat::float,
           ST_SetSRID(ST_MakePoint(lon::float, lat::float), 4326) AS location -- this sets the ROW SRID as 4326
    FROM raw.ukgov_strategic_centres_wm
);

ALTER TABLE cleaned.ukgov_strategic_centres_wm
    ADD PRIMARY KEY (name),
    ADD COLUMN type varchar DEFAULT 'Strategic Centre',
    ALTER COLUMN location TYPE geometry(Point, 4326), -- this sets the GEOM COLUMN SRID as 4326
    DROP COLUMN lon, -- dropping so that semantic contains only the snapped lon and lat
    DROP COLUMN lat;
CREATE INDEX ukgov_strategic_centres_wm_cent_idx ON cleaned.ukgov_strategic_centres_wm USING gist(location);

-- raw.ukgov_schools_uk --> cleaned.ukgov_schools_wm

DROP TABLE IF EXISTS cleaned.ukgov_schools_wm;

CREATE TABLE cleaned.ukgov_schools_wm AS(

    WITH

    schools AS (

        SELECT l.SCHNAME AS name,
               l.POSTCODE AS pcd,
               l.URN AS id,
               r.lon AS lon,
               r.lat AS lat,
               l.ISPRIMARY::boolean AS is_primary,
               l.ISSECONDARY::boolean AS is_secondary,
               l.ISPOST16::boolean AS is_post_16,
               ST_SetSRID(ST_MakePoint(r.lon::float, r.lat::float), 4326) AS location -- this sets the ROW SRID as 4326
        FROM raw.ukgov_schools_uk l
        LEFT JOIN cleaned.pcd_centroids_wm r
        ON l.POSTCODE = r.pcd -- no filtering! Includes schools across the entire UK
	)

	SELECT
	    DISTINCT ON (lon, lat) -- drop duplicates. This also drops job centres outside WM.
	    *
	FROM schools
	WHERE lon IS NOT NULL
);

ALTER TABLE cleaned.ukgov_schools_wm
    ADD PRIMARY KEY (id),
    ADD COLUMN type varchar DEFAULT 'School',
    ALTER COLUMN location TYPE geometry(Point, 4326); -- this sets the GEOM COLUMN SRID as 4326

-- raw.ofsted_childcare_wm --> cleaned.ofsted_childcare_wm

DROP TABLE IF EXISTS cleaned.ofsted_childcare_wm;

CREATE TABLE cleaned.ofsted_childcare_wm AS(

    WITH

    childcare AS (

        SELECT l.name,
               l.pcd,
               r.lon AS lon,
               r.lat AS lat,
               ST_SetSRID(ST_MakePoint(r.lon::float, r.lat::float), 4326) AS location -- this sets the ROW SRID as 4326
        FROM raw.ofsted_childcare_wm l
        LEFT JOIN cleaned.pcd_centroids_wm r
        ON l.pcd = r.pcd -- no filtering! Includes some childcare centres outside the borders of the WM
	)

	SELECT
	    DISTINCT ON (lon, lat) -- drop duplicates. This also drops childcare centres outside WM.
	    *
	FROM childcare
	WHERE lon IS NOT NULL
);

ALTER TABLE cleaned.ofsted_childcare_wm
    ADD COLUMN id SERIAL PRIMARY KEY,
    ADD COLUMN type varchar DEFAULT 'Childcare',
    ALTER COLUMN location TYPE geometry(Point, 4326); -- this sets the GEOM COLUMN SRID as 4326


-- raw.wmca_rail_stations_uk --> cleaned.wmca_rail_stations_wm

DROP TABLE IF EXISTS cleaned.wmca_rail_stations_wm;

CREATE TABLE cleaned.wmca_rail_stations_wm AS(

    WITH

    british_national_grid AS (
        SELECT name,
               ST_SetSRID(ST_MakePoint(x::float, y::float), 27700) AS location -- this sets original projection
        FROM raw.wmca_rail_stations_uk
	),

	standard_projection AS (
	        SELECT name,
               ST_Transform(location, 4326) AS location -- this transforms to standard projection 4326
        FROM british_national_grid
	),

	latlons AS (
        SELECT name,
               ST_X(location) as latitude,  -- this extracts the lat and lon
               ST_Y(location) AS longitude,
               location
        FROM standard_projection
        )

        select l.name,
               l.latitude,
               l.longitude,
               location
            from latlons l
            INNER JOIN  -- this filters to the West Midlands
            cleaned.oa_boundaries_wm as o
            ON ST_WITHIN(l.location, o.geometry)
);

ALTER TABLE cleaned.wmca_rail_stations_wm
    ADD COLUMN id SERIAL PRIMARY KEY,
    ADD COLUMN type varchar DEFAULT 'Rail Station',
    ALTER COLUMN location TYPE geometry(Point, 4326); -- this sets the GEOM COLUMN SRID as 4326



-- Add OSM tables

DROP TABLE if exists cleaned.planet_osm_line;
CREATE TABLE cleaned.planet_osm_line AS (
  SELECT osm_id,
         amenity,
         area,
         tags,
         ST_Transform(way, 4326) as way
    FROM raw.planet_osm_line
);
SELECT UpdateGeometrySRID('cleaned', 'planet_osm_line', 'way', 4326); -- change row and geom col SRID to 4326
CREATE INDEX planet_osm_line_way_idx ON cleaned.planet_osm_line USING gist(way);

/*
DROP TABLE if exists cleaned.planet_osm_nodes;
CREATE TABLE cleaned.planet_osm_nodes AS (
  SELECT *
    FROM raw.planet_osm_nodes
);

DROP TABLE if exists cleaned.planet_osm_point;
CREATE TABLE cleaned.planet_osm_point AS (
  SELECT osm_id,
         amenity,
         area,
         tags,
         ST_Transform(way, 4326) as way
    FROM raw.planet_osm_point
);
SELECT UpdateGeometrySRID('cleaned', 'planet_osm_point', 'way', 4326); -- change row and geom col SRID to 4326
CREATE INDEX planet_osm_point_way_idx ON cleaned.planet_osm_point USING gist(way);


DROP TABLE if exists cleaned.planet_osm_polygon;
CREATE TABLE cleaned.planet_osm_polygon AS (
  SELECT osm_id,
         amenity,
         way_area,
         tags,
         ST_Transform(way, 4326) as way
    FROM raw.planet_osm_polygon
);
SELECT UpdateGeometrySRID('cleaned', 'planet_osm_polygon', 'way', 4326); -- change row and geom col SRID to 4326
CREATE INDEX planet_osm_polygon_way_idx ON cleaned.planet_osm_polygon USING gist(way);

DROP TABLE if exists cleaned.planet_osm_rels;
CREATE TABLE cleaned.planet_osm_rels AS (
  SELECT *
    FROM raw.planet_osm_rels
);

DROP TABLE if exists cleaned.planet_osm_roads;
CREATE TABLE cleaned.planet_osm_roads AS (
  SELECT osm_id,
         amenity,
         way_area,
         tags,
         ST_Transform(way, 4326) as way
    FROM raw.planet_osm_roads
);
SELECT UpdateGeometrySRID('cleaned', 'planet_osm_roads', 'way', 4326); -- change row and geom col SRID to 4326
CREATE INDEX planet_osm_polygon_roads_idx ON cleaned.planet_osm_roads USING gist(way);

DROP TABLE if exists cleaned.planet_osm_ways;
CREATE TABLE cleaned.planet_osm_ways AS (
  SELECT *
    FROM raw.planet_osm_ways
);
*/


-- Snap OA centroids to road geometry

DROP TABLE IF EXISTS snapped_centroids_wm;
CREATE TEMP TABLE snapped_centroids_wm AS
SELECT p.oa11cd AS oa_id,
       p.centroid AS centroid,
       ST_ClosestPoint (l.way, p.centroid) AS snapped_centroid
FROM (
    SELECT p.oa11cd AS oa,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.oa_boundaries_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.centroid
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.oa_boundaries_wm AS p ON table1.oa = p.oa11cd
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3;

-- Bring snapped centroids together with other OA data

DROP TABLE IF EXISTS cleaned.oa_boundaries_wm_snapped;
CREATE TABLE cleaned.oa_boundaries_wm_snapped AS(
    SELECT oa.*,
           sc.snapped_centroid AS snapped_centroid,
           ST_y(sc.snapped_centroid) AS latitude,
	       ST_x(sc.snapped_centroid) AS longitude
    FROM snapped_centroids_wm sc
    INNER JOIN cleaned.oa_boundaries_wm oa ON sc.oa_id = oa.oa11cd
);

-- Snap job centre locations to road geometry

DROP TABLE IF EXISTS snapped_job_centres_wm;
CREATE TEMP TABLE snapped_job_centres_wm AS
SELECT p.name AS name,
       p.pcd_centroid AS pcd_centroid,
       ST_ClosestPoint (l.way, p.pcd_centroid) AS snapped_location
FROM (
    SELECT p.name AS name,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.ukgov_job_centres_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.pcd_centroid
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.ukgov_job_centres_wm AS p ON table1.name = p.name
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3;

-- Bring snapped job centres together with other data

DROP TABLE IF EXISTS cleaned.ukgov_job_centres_wm_snapped;
CREATE TABLE cleaned.ukgov_job_centres_wm_snapped AS(
    SELECT jc.name,
           jc.type,
           sn.pcd_centroid,
           sn.snapped_location AS snapped_location,
           ST_y(sn.snapped_location) AS latitude,
	       ST_x(sn.snapped_location) AS longitude
    FROM snapped_job_centres_wm sn
    INNER JOIN cleaned.ukgov_job_centres_wm jc ON sn.name = jc.name
);

-- Snap strategic centre locations to road geometry

DROP TABLE IF EXISTS snapped_strategic_centres_wm;
CREATE TEMP TABLE snapped_strategic_centres_wm AS
SELECT p.name AS name,
       p.location AS location,
       ST_ClosestPoint (l.way, p.location) AS snapped_location
FROM (
    SELECT p.name AS name,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.ukgov_strategic_centres_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.location
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.ukgov_strategic_centres_wm AS p ON table1.name = p.name
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3;

-- Bring snapped strategic centres together with other data

DROP TABLE IF EXISTS cleaned.ukgov_strategic_centres_wm_snapped;
CREATE TABLE cleaned.ukgov_strategic_centres_wm_snapped AS(
    SELECT sc.name,
           sc.type,
           sn.location,
           sn.snapped_location AS snapped_location,
           ST_y(sn.snapped_location) AS latitude,
	       ST_x(sn.snapped_location) AS longitude
    FROM snapped_strategic_centres_wm sn
    INNER JOIN cleaned.ukgov_strategic_centres_wm sc ON sn.name = sc.name
);

-- Snap school locations to road geometry

DROP TABLE IF EXISTS snapped_schools_wm;
CREATE TEMP TABLE snapped_schools_wm AS
SELECT p.name AS name,
       p.id AS id,
       p.location AS location,
       ST_ClosestPoint (l.way, p.location) AS snapped_location
FROM (
    SELECT p.name AS name,
           p.id AS id,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.ukgov_schools_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.location
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.ukgov_schools_wm AS p ON table1.id = p.id
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3, 4;

-- Bring snapped schools together with other data

DROP TABLE IF EXISTS cleaned.ukgov_schools_wm_snapped;
CREATE TABLE cleaned.ukgov_schools_wm_snapped AS(
    SELECT sc.name,
           sc.type,
           sn.location,
           sn.snapped_location AS snapped_location,
           ST_y(sn.snapped_location) AS latitude,
	       ST_x(sn.snapped_location) AS longitude
    FROM snapped_schools_wm sn
    INNER JOIN cleaned.ukgov_schools_wm sc ON sn.id = sc.id
);

-- Snap childcare locations to road geometry

DROP TABLE IF EXISTS snapped_childcare_wm;
CREATE TEMP TABLE snapped_childcare_wm AS
SELECT p.name AS name,
       p.id AS id,
       p.location AS location,
       ST_ClosestPoint (l.way, p.location) AS snapped_location
FROM (
    SELECT p.name AS name,
           p.id AS id,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.ofsted_childcare_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.location
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.ofsted_childcare_wm AS p ON table1.id = p.id
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3, 4;

-- Bring snapped childcare together with other data

DROP TABLE IF EXISTS cleaned.ofsted_childcare_wm_snapped;
CREATE TABLE cleaned.ofsted_childcare_wm_snapped AS(
    SELECT sc.name,
           sc.type,
           sn.location,
           sn.snapped_location AS snapped_location,
           ST_y(sn.snapped_location) AS latitude,
	       ST_x(sn.snapped_location) AS longitude
    FROM snapped_childcare_wm sn
    INNER JOIN cleaned.ofsted_childcare_wm sc ON sn.id = sc.id
);

-- Snap rail station locations to road geometry

DROP TABLE IF EXISTS snapped_rail_stations_wm;
CREATE TEMP TABLE snapped_rail_stations_wm AS
SELECT p.name AS name,
       p.id AS id,
       p.location AS location,
       ST_ClosestPoint (l.way, p.location) AS snapped_location
FROM (
    SELECT p.name AS name,
           p.id AS id,
           cjl.osm_id AS nearest_road,
           cjl.geom AS geom
    FROM cleaned.wmca_rail_stations_wm AS p
    CROSS JOIN LATERAL (
        SELECT r.osm_id,
               ST_AsText(r.way) as geom
        FROM cleaned.planet_osm_line r
        ORDER BY r.way <-> p.location
        LIMIT 1) AS cjl) AS table1
    INNER JOIN cleaned.wmca_rail_stations_wm AS p ON table1.id = p.id
    INNER JOIN cleaned.planet_osm_line AS l ON table1.geom = ST_AsText(l.way)
group by 1, 2, 3, 4;

-- Bring snapped rail stations together with other data

DROP TABLE IF EXISTS cleaned.wmca_rail_stations_wm_snapped;
CREATE TABLE cleaned.wmca_rail_stations_wm_snapped AS(
    SELECT sc.name,
           sc.type,
           sn.location,
           sn.snapped_location AS snapped_location,
           ST_y(sn.snapped_location) AS latitude,
	       ST_x(sn.snapped_location) AS longitude
    FROM snapped_rail_stations_wm sn
    INNER JOIN cleaned.wmca_rail_stations_wm sc ON sn.id = sc.id
);

-- Hardcoding latitude and longitude when snapped centroid falls on an unconnected road
UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.5227987993297,
    longitude = -2.08436776221958
WHERE
   oa11cd = 'E00049365';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4025592139435,
    longitude = -1.5976175620818
WHERE
   oa11cd = 'E00172155';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.5615549428508,
    longitude = -2.05246167590059
WHERE
   oa11cd = 'E00052132';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4980063577372,
    longitude = -2.02792381326826
WHERE
   oa11cd = 'E00050261';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4056431933213,
    longitude = -1.51549349002789
WHERE
   oa11cd = 'E00172205';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.3515919014821,
    longitude = -1.78205469685795
WHERE
   oa11cd = 'E00051504';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4677079398976,
    longitude = -1.93666635944615
WHERE
   oa11cd = 'E00045613';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4980063577372,
    longitude = -2.02792381326826
WHERE
   oa11cd = 'E00045620';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4597820471708,
    longitude = -1.93722451158809
WHERE
   oa11cd = 'E00045629';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.6120224173596,
    longitude = -2.13460688852088
WHERE
   oa11cd = 'E00053017';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4211353939385,
    longitude = -1.69575071970747
WHERE
   oa11cd = 'E00051117';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.3983327055288,
    longitude = -1.7369140033066
WHERE
   oa11cd = 'E00051118';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4664445569164,
    longitude = -1.76514590893414
WHERE
   oa11cd = 'E00051133';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.427751224413,
    longitude = -1.93603297996386
WHERE
   oa11cd = 'E00045482';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.5653847975693,
    longitude = -2.05956526189146
WHERE
   oa11cd = 'E00052132';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.4751868335343,
    longitude = -1.95963739723586
WHERE
   oa11cd = 'E00046396';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.431501518074,
    longitude = -1.76817770559418
WHERE
   oa11cd = 'E00051718';

UPDATE cleaned.oa_boundaries_wm_snapped
SET latitude = 52.3853167741399,
    longitude = -1.54887284466298
WHERE
   oa11cd = 'E00048944';


-- Adjust location of schools that aren't on a connected road
UPDATE cleaned.ukgov_schools_wm_snapped
SET latitude = 52.5678003490819,
    longitude = -2.14938646888889
WHERE
   name = 'Woodfield Infant School';

UPDATE cleaned.ukgov_schools_wm_snapped
SET latitude = 52.4583315538734,
    longitude = -1.88263891543757
WHERE
   name = 'Redstone Educational Academy';

UPDATE cleaned.ukgov_schools_wm_snapped
SET latitude = 52.5030679892469,
    longitude = -1.87855218319503
WHERE
   name = 'The Wisdom Academy';

UPDATE cleaned.ukgov_schools_wm_snapped
SET latitude = 52.4045085835708,
    longitude = -1.92853841781766
WHERE
   name = 'Cadbury Sixth Form College';


-- Adjust location of childcare providers that aren't on a connected road
UPDATE cleaned.ofsted_childcare_wm_snapped
SET latitude = 52.5283813945791,
    longitude = -2.08103790085646
WHERE
   name = 'Foxyards Primary School';

UPDATE cleaned.ofsted_childcare_wm_snapped
SET latitude = 52.4787133447242,
    longitude = -2.00701421900862
WHERE
   name = 'Kiddies World';

UPDATE cleaned.ofsted_childcare_wm_snapped
SET latitude = 52.3983327055288,
    longitude = -1.7369140033066
WHERE
   name = 'The Courtyard Nursery School';


-- Adjust location of strategic centre that isn't on a connected road
UPDATE cleaned.ukgov_strategic_centres_wm_snapped
SET latitude = 52.452780,
    longitude = -1.732388
WHERE
   name = 'UKCentral';


-- Adjust location of job centres that aren't on a connected road
UPDATE cleaned.ukgov_job_centres_wm_snapped
SET latitude = 52.404596,
    longitude = -1.510207
WHERE
   name = 'Cofa Court';

UPDATE cleaned.ukgov_job_centres_wm_snapped
SET latitude = 52.455744,
    longitude = -1.870832
WHERE
   name = 'Heynesfield House';


-- Adjust location of train stations that aren't on a connected road
UPDATE cleaned.wmca_rail_stations_wm_snapped
SET latitude = 52.5855866262231,
    longitude = -2.11637546163522
WHERE
   name = 'Wolverhampton';



