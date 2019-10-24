DROP TABLE IF EXISTS wmca.temp;
CREATE TABLE wmca.temp AS (
    SELECT unnest(raw_list) as raw_list
    FROM results.hist where model_id=0
);

ALTER TABLE results.model_results ADD threshold_sigma_2 VARCHAR(50);
UPDATE results.model_results
SET threshold_sigma_2 = CASE
           WHEN results.model_results.value > (SELECT avg(raw_list)+(2*stddev_pop(raw_list)) FROM wmca.temp) AND results.model_results.population > (SELECT avg(population)+(2*stddev_pop(population)) as threshold_pop FROM results.model_results WHERE model_id=0) THEN 1
                ELSE 0
              end