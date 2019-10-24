drop table if exists results.model_1_distribution;
create table results.model_1_distribution (
	bin_count int, 
	bin_minimums float[],
	subgroup_pop int[],
	description varchar 
);