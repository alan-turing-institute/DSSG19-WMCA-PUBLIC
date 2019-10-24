DROP TABLE if exists raw.ONS_pcd_centroids;
CREATE TABLE if not exists raw.ONS_pcd_centroids(
	X float, 
	Y float, 
	objectid varchar,
	pcd varchar, 
	pcd2 varchar,
	pcds varchar,
	dointr varchar,
	doterm varchar,
	usertype varchar, 
	oseast1m varchar,
	osnrth1m varchar, 
	osgrdind varchar, 
	oa11 varchar, 
	cty varchar, 
	laua varchar, 
	ward varchar, 
	hlthau varchar, 
	ctry varchar, 
	pcon varchar, 
	eer varchar, 
	teclec varchar, 
	ttwa varchar, 
	pct varchar, 
	nuts varchar, 
	park varchar, 
	lsoa11 varchar, 
	msoa11 varchar, 
	wz11 varchar, 
	ccg varchar, 
	bua11 varchar, 
	buasd11 varchar, 
	ru11ind varchar, 
	oac11 varchar, 
	lat float, 
	long float, 
	lep1 varchar, 
	lep2 varchar,
	pfa varchar, 
	imd float, 
	ced varchar, 
	nhser varchar, 
	rgn varchar, 
	calncv varchar, 
	stp varchar 
);

-- ONS： local authority - county lookup table
DROP TABLE if exists raw.ONS_la_county_lookup;
CREATE TABLE if not exists raw.ONS_la_county_lookup(
	LAD16CD varchar,
	LAD16NM varchar,
	CTY16CD varchar,
	CTY16NM varchar,
	FID int
);

-- ONS: car availability
DROP TABLE if exists raw.ONS_KS404UK_car_availability;
CREATE TABLE if not exists raw.ONS_KS404UK_car_availability(
	date_ varchar, 
	oa11 varchar, 
	geography varchar, 
	cars_all_households varchar, 
	cars_no_car varchar, 
	cars_1_car varchar, 
	cars_2_cars varchar, 
	cars_3_cars varchar, 
	cars_4_plus_cars varchar, 
	cars_sum_of_cars varchar 
);

-- ONS: age
DROP TABLE if exists raw.ONS_KS102UK_age_structure;
CREATE TABLE if not exists raw.ONS_KS102UK_age_structure(
	date_ varchar, 
	oa11 varchar, 
	geography varchar, 
	age_all_residents varchar, 
	age_0_to_5 varchar, 
	age_5_to_7 varchar, 
	age_8_to_9 varchar, 
	age_10_to_14 varchar, 
	age_15 varchar, 
	age_16_to_17 varchar, 
	age_18_to_19 varchar,
	age_20_to_24 varchar,
	age_25_to_29 varchar, 
	age_30_to_44 varchar,
	age_45_to_59 varchar, 
	age_60_to_64 varchar,
	age_65_to_74 varchar,
	age_75_to_84 varchar, 
	age_85_to_89 varchar, 
	age_90_plus varchar, 
	age_mean varchar,
	age_median varchar
);

-- ONS: disability
DROP TABLE if exists raw.ONS_QS303EW_disability;
CREATE TABLE if not exists raw.ONS_QS303EW_disability(
	date_ varchar, 
	oa11 varchar, 
	geography varchar, 
	rural_urban varchar, 
	disability_all varchar, 
	disability_severe varchar, 
	disability_moderate varchar, 
	disability_none varchar
);

-- ONS: employment
DROP TABLE if exists raw.ONS_KS601UK_employment;
CREATE TABLE if not exists raw.ONS_KS601UK_employment(
	date_ varchar, 
	oa11 varchar, 
	geography varchar, 
	emp_all_residents_16_to_74 varchar, 
	emp_active varchar, 
	emp_active_in_employment varchar, 
	emp_active_part_time varchar, 
	emp_active_full_time varchar, 
	emp_active_self_employed varchar,
	emp_active_unemployed varchar,
	emp_active_full_time_student varchar,
	emp_inactive varchar,
	emp_inactive_retired varchar,
	emp_inactive_student varchar,
	emp_inactive_homemaking varchar,
	emp_inactive_disabled varchar,
	emp_inactive_other varchar,
	emp_unemployed_16_to_24 varchar,
	emp_unemployed_50_to_74 varchar,
	emp_unemployed_never_worked varchar,
	emp_unemployed_long_term_unemployed varchar
);

-- ONS: ethnicity
DROP TABLE if exists raw.ONS_KS201UK_ethnicity;
CREATE TABLE if not exists raw.ONS_KS201UK_ethnicity(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    all_ varchar,
    white varchar,
    gypsy varchar,
    mixed varchar,
    asian_indian varchar,
    asian_pakistani varchar,
    asian_bangladeshi varchar,
    asian_chinese varchar,
    asian_other varchar,
    black varchar,
    other varchar
);

-- ONS: usual residents
DROP TABLE if exists raw.ONS_KS101UK_usual_residents;
CREATE TABLE if not exists raw.ONS_KS101UK_usual_residents(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    all_usual_residents varchar,
    males varchar,
    females varchar,
    lives_in_household varchar,
    lives_in_communal_establishment varchar,
    student varchar,
    area_hectares varchar,
    density_persons_per_hectare varchar
);

-- ONS: lone parent
DROP TABLE if exists raw.ONS_KS107UK_lone_parent;
CREATE TABLE if not exists raw.ONS_KS107UK_lone_parent(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    lone_parent_total_hh varchar,
    lone_parent_part_time_emp varchar,
    lone_parent_full_time_emp varchar,
    lone_parent_no_emp varchar,
    male_lone_parent_total varchar,
    male_lone_parent_part_time_emp varchar,
    male_lone_parent_full_time_emp varchar,
    male_lone_parent_no_emp varchar,
    female_lone_parent_total varchar,
    female_lone_parent_part_time_emp varchar,
    female_lone_parent_full_time_emp varchar,
    female_lone_parent_no_emp varchar
);

-- ONS: students
DROP TABLE if exists raw.ONS_KS501UK_students;
CREATE TABLE if not exists raw.ONS_KS501UK_students(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    highest_qual_all varchar,
    no_qual varchar,
    highest_qual_level_1 varchar,
    highest_qual_level_2 varchar,
    highest_qual_apprenticeship varchar,
    highest_qual_level_3 varchar,
    highest_qual_level_4_above varchar,
    highest_qual_other varchar,
    schoolchildren_students_16_to_17 varchar,
    schoolchildren_students_18_plus varchar,
    students_employed varchar,
    students_unemployed varchar,
    students_econ_inactive varchar
);

-- ONS: birth country
DROP TABLE if exists raw.ONS_QS203UK_birth_country;
CREATE TABLE if not exists raw.ONS_QS203UK_birth_country(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    all_categories varchar,
    europe_total varchar,
    europe_uk_total varchar,
    europe_uk_england varchar,
    europe_uk_n_ireland varchar,
    europe_uk_scotland varchar,
    europe_uk_wales varchar,
    europe_uk_other varchar,
    europe_channel_islands varchar,
    europe_ireland varchar,
    europe_other_total varchar,
    europe_other_eu_total varchar,
    europe_other_eu_germany varchar,
    europe_other_eu_lithuania varchar,
    europe_other_eu_poland varchar,
    europe_other_eu_romania varchar,
    europe_other_eu_other varchar,
    europe_other_rest_total varchar,
    europe_other_rest_turkey varchar,
    europe_other_rest_other varchar,
    africa_total varchar,
    africa_n varchar,
    africa_cw_total varchar,
    africa_cw_nigeria varchar,
    africa_cw_other varchar,
    africa_se_total varchar,
    africa_se_kenya varchar,
    africa_se_south_africa varchar,
    africa_se_zimbabwe varchar,
    africa_se_other varchar,
    mideast_asia_total varchar,
    mideast_asia_mideast_total varchar,
    mideast_asia_mideast_iran varchar,
    mideast_asia_mideast_other varchar,
    mideast_asia_east_asia_total varchar,
    mideast_asia_east_asia_china varchar,
    mideast_asia_east_asia_hong_kong varchar,
    mideast_asia_east_asia_other varchar,
    mideast_asia_south_asia_total varchar,
    mideast_asia_south_asia_bangladesh varchar,
    mideast_asia_south_asia_india varchar,
    mideast_asia_south_asia_pakistan varchar,
    mideast_asia_south_asia_other varchar,
    mideast_asia_se_asia_total varchar,
    mideast_asia_central_asia_total varchar,
    americas_total varchar,
    americas_north_america_total varchar,
    americas_north_america_caribbean varchar,
    americas_north_america_usa varchar,
    americas_north_america_other varchar,
    americas_central_america varchar,
    americas_south_america varchar,
    antarctica_oceania_total varchar,
    antarctica_oceania_australia varchar,
    antarctica_oceania_other varchar,
    other varchar
);

-- ONS: English proficiency
DROP TABLE if exists raw.ONS_QS205EW_english_proficiency;
CREATE TABLE if not exists raw.ONS_QS205EW_english_proficiency(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    rural_urban varchar,
    all_ varchar,
    main_english varchar,
    main_not_english_very_well varchar,
    main_not_english_well varchar,
    main_not_english_not_well varchar,
    main_not_english_cannot varchar
);

-- ONS: Deprivation
DROP TABLE if exists raw.ONS_QS119EW_deprivation;
CREATE TABLE if not exists raw.ONS_QS119EW_deprivation(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    rural_urban varchar,
    all_ varchar,
    deprived_0_dim varchar,
    deprived_1_dim varchar,
    deprived_2_dim varchar,
    deprived_3_dim varchar,
    deprived_4_dim varchar
);

-- ONS: Approx Social Grade
DROP TABLE if exists raw.ONS_QS613EW_approx_social_grade;
CREATE TABLE if not exists raw.ONS_QS613EW_approx_social_grade(
    date_ varchar,
    oa11 varchar,
    geography varchar,
    all_ varchar,
    grade_ab varchar,
    grade_c1 varchar,
    grade_c2 varchar,
    grade_de varchar
);

-- Load data: NHS hospitals
DROP TABLE if exists raw.NHS_hospitals;
CREATE TABLE if not exists raw.NHS_hospitals(
    OrganisationID     VARCHAR,   
    OrganisationCode   VARCHAR, 
    OrganisationType   VARCHAR, 
    SubType            VARCHAR, 
    Sector             VARCHAR, 
    OrganisationStatus VARCHAR, 
    IsPimsManaged      VARCHAR, 
    OrganisationName   VARCHAR, 
    Address1           VARCHAR,
    Address2           VARCHAR,
    Address3           VARCHAR,
    City               VARCHAR,
    County             VARCHAR,
    Postcode           VARCHAR,
    Latitude           VARCHAR,
    Longitude          VARCHAR,
    ParentODSCode      VARCHAR,
    ParentName         VARCHAR,
    Phone              VARCHAR,
    Email              VARCHAR,
    Website            VARCHAR,
    Fax                VARCHAR
);

-- Strategic Centres
DROP TABLE if exists raw.ukgov_strategic_centres_wm;
CREATE TABLE if not exists raw.ukgov_strategic_centres_wm (
    name               VARCHAR,
    lat                VARCHAR,
    lon               VARCHAR,
    type               VARCHAR
);

-- Job Centres
DROP TABLE if exists raw.ukgov_job_centres_wm;
CREATE TABLE if not exists raw.ukgov_job_centres_wm (
    name               VARCHAR,
    pcd                VARCHAR,
    type               VARCHAR
);

-- Schools
DROP TABLE if exists raw.ukgov_schools_uk;
CREATE TABLE if not exists raw.ukgov_schools_uk (
    URN                VARCHAR,
    LA                 VARCHAR,
    ESTAB              VARCHAR,
    LAESTAB            VARCHAR,
    SCHNAME            VARCHAR,
    OTHERSCHNAME       VARCHAR,
    STREET	           VARCHAR,
    LOCALITY           VARCHAR,
    ADDRESS3	       VARCHAR,
    TOWN	           VARCHAR,
    POSTCODE	       VARCHAR,
    TELNUM	           VARCHAR,
    ICLOSE	           VARCHAR,
    OPENDATE	       VARCHAR,
    CLOSEDATE	       VARCHAR,
    ISNEW	           VARCHAR,
    MINORGROUP	       VARCHAR,
    NFTYPE	           VARCHAR,
    OTHERNFTYPE	       VARCHAR,
    ISPRIMARY	       VARCHAR,
    ISSECONDARY	       VARCHAR,
    ISPOST16	       VARCHAR,
    AGEL	           VARCHAR,
    AGEH	           VARCHAR,
    GENDER	           VARCHAR,
    SIXFGENDER	       VARCHAR,
    RELDENOM	       VARCHAR,
    ADMPOL	           VARCHAR,
    OTHERURN	       VARCHAR,
    NEWACFLAG	       VARCHAR,
    RE_BROKERED        VARCHAR
);

-- Childcare
DROP TABLE if exists raw.ofsted_childcare_wm;
CREATE TABLE if not exists raw.ofsted_childcare_wm (
    name               VARCHAR,
    pcd                VARCHAR,
    type               VARCHAR
);

-- Rail Stations
DROP TABLE if exists raw.wmca_rail_stations_uk;
CREATE TABLE if not exists raw.wmca_rail_stations_uk (
    X                  VARCHAR,
    Y                  VARCHAR,
    objectid           VARCHAR,
    featureco          VARCHAR,
    identifier         VARCHAR,
    name               VARCHAR
);


-- Enables compact store of OSM data.
-- commented bc throws psycopg2 error: extension "hstore" already exists
-- Uncomment below if you want to see OSM tags.

--create extension hstore;
