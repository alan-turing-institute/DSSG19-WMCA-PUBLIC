DROP TABLE if exists raw.planet_osm_line;
DROP TABLE if exists raw.planet_osm_nodes;
DROP TABLE if exists raw.planet_osm_point;
DROP TABLE if exists raw.planet_osm_polygon;
DROP TABLE if exists raw.planet_osm_rels;
DROP TABLE if exists raw.planet_osm_roads;
DROP TABLE if exists raw.planet_osm_ways;

ALTER TABLE public.planet_osm_line SET SCHEMA raw;
ALTER TABLE public.planet_osm_nodes SET SCHEMA raw;
ALTER TABLE public.planet_osm_point SET SCHEMA raw;
ALTER TABLE public.planet_osm_polygon SET SCHEMA raw;
ALTER TABLE public.planet_osm_rels SET SCHEMA raw;
ALTER TABLE public.planet_osm_roads SET SCHEMA raw;
ALTER TABLE public.planet_osm_ways SET SCHEMA raw;
