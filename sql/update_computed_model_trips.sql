UPDATE model.trips{suffix} SET computed=1
WHERE trip_id IN (
        SELECT trip_id FROM model.trips{suffix}
        ORDER BY trip_id
        LIMIT {limit} OFFSET {offset} 
    );
