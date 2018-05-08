select
    rc.name as racing_class,
    r.car_number,
    r.driver_name,
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

    -- round 1
    rr1.lane_number as round1_lane,
    -- round 2
    rr2.lane_number as round2_lane,

    -- round 3
    rr3.lane_number as round3_lane,

    -- round 4
    rr4.lane_number as round4_lane,

    -- round 5
    rr5.lane_number as round5_lane,

    -- round 6
    rr6.lane_number as round6_lane,

    -- round 7
    rr7.lane_number as round7_lane,

    -- round 8
    rr8.heat_number as round8_heat,
    rr8.lane_number as round8_lane,
    rr8.time as round8_time,
    rr8.place as round8_place,

    -- round 9
    rr9.heat_number as round9_heat,
    rr9.lane_number as round9_lane,
    rr9.time as round9_time,
    rr9.place as round9_place,

    -- round 10
    rr10.heat_number as round10_heat,
    rr10.lane_number as round10_lane,
    rr10.time as round10_time,
    rr10.place as round10_place
from
    racers r join
    grades g on r.grade_id = g.grade_id join
    racing_classes rc on r.racing_class_id = rc.racing_class_id left join
    race_results rr1 on r.car_number = rr1.car_number and rr1.round_number = 1 left join
    race_results rr2 on r.car_number = rr2.car_number and rr2.round_number = 2 left join
    race_results rr3 on r.car_number = rr3.car_number and rr3.round_number = 3 left join
    race_results rr4 on r.car_number = rr4.car_number and rr4.round_number = 4 left join
    race_results rr5 on r.car_number = rr5.car_number and rr5.round_number = 5 left join
    race_results rr6 on r.car_number = rr6.car_number and rr6.round_number = 6 left join
    race_results rr7 on r.car_number = rr7.car_number and rr7.round_number = 7 left join
    race_results rr8 on r.car_number = rr8.car_number and rr8.round_number = 8 left join
    race_results rr9 on r.car_number = rr9.car_number and rr9.round_number = 9 left join
    race_results rr10 on r.car_number = rr10.car_number and rr10.round_number = 10
order by
    2