DROP TABLE IF EXISTS results.populations;
CREATE TABLE IF NOT EXISTS results.populations AS (
    WITH wide AS (
        SELECT oa11 as oa_id,
               {pop_col_defs}
        FROM semantic.oa
    ),

    arr AS (
    SELECT oa_id,
           ARRAY{pop_col_names} AS pop_list,
           ARRAY[{pop_cols}] AS cnt_list
    FROM wide
	ORDER BY oa_id
    )

    SELECT oa_id,
        UNNEST(pop_list) AS population,
        UNNEST(cnt_list) AS count
    FROM arr
);

