select
    r.car_number,
    r.driver_name,
    rc.name as racing_class,
    g.name as grade,
    
    ifnull((
        select count(xrr.race_number)
        from race_results xrr
        where xrr.car_number = r.car_number
        and xrr.time is not null
    ), 0) as total_races,
    
    ifnull((
        select sum(xrr.time)
        from race_results xrr
        where xrr.car_number = r.car_number
        --and xx.
    ), 0.0) as total_time,
 
    rr.race_number,
    rr.round_number,
    rr.heat_number,
    rr.lane_number,
    rr.time,
    rr.place

from
    racers r left join
    grades g on r.grade_id = g.grade_id left join
    racing_classes rc on r.racing_class_id = rc.racing_class_id left join
    race_results rr on r.car_number = rr.car_number
where
    place is not null
order by
    r.car_number,
    rr.round_number
