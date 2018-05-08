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

    -- round 1
    rr1.heat_number as "r1 heat",
    rr1.lane_number as "r1 lane",
    rr1.time as "r1 time",
    rr1.place as "r1 place",

    -- round 2
    rr2.heat_number as "r2 heat",
    rr2.lane_number as "r2 lane",
    rr2.time as "r2 time",
    rr2.place as "r2 place",

    -- round 3
    rr3.heat_number as "r3 heat",
    rr3.lane_number as "r3 lane",
    rr3.time as "r3 time",
    rr3.place as "r3 place",

    -- round 4
    rr4.heat_number as "r4 heat",
    rr4.lane_number as "r4 lane",
    rr4.time as "r4 time",
    rr4.place as "r4 place",

    -- round 5
    rr5.heat_number as "r5 heat",
    rr5.lane_number as "r5 lane",
    rr5.time as "r5 time",
    rr5.place as "r5 place",

    -- round 6
    rr6.heat_number as "r6 heat",
    rr6.lane_number as "r6 lane",
    rr6.time as "r6 time",
    rr6.place as "r6 place",

    -- round 7
    rr7.heat_number as "r7 heat",
    rr7.lane_number as "r7 lane",
    rr7.time as "r7 time",
    rr7.place as "r7 place",

    -- round 8
    rr8.heat_number as "r8 heat",
    rr8.lane_number as "r8 lane",
    rr8.time as "r8 time",
    rr8.place as "r8 place",

    -- round 9
    rr9.heat_number as "r9 heat",
    rr9.lane_number as "r9 lane",
    rr9.time as "r9 time",
    rr9.place as "r9 place",

    -- round 10
    rr10.heat_number as "r10 heat",
    rr10.lane_number as "r10 lane",
    rr10.time as "r10 time",
    rr10.place as "r10 place"
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
    6
