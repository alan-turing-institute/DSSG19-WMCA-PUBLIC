SELECT
    e.oa_id, e.poi_id, e.date, e.time, e.trip_id,
    o.snapped_latitude as oa_lat, o.snapped_longitude as oa_lon,
    p.snapped_latitude as poi_lat, p.snapped_longitude as poi_lon
FROM ((model.trips{suffix} e INNER JOIN semantic.oa o ON e.oa_id = o.oa11)
    INNER JOIN semantic.poi p on e.poi_id = p.id)
WHERE e.computed = 0
ORDER BY e.trip_id
LIMIT {limit} OFFSET {offset};
