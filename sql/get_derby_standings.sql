select
  r.car_number,
  r.driver_name,
  rc.name as racing_class_name,
  g.name as grade_name,
  r.den,
  ifnull(sum(rr.time), 0.0) as total_time,
  count(rr.time) as race_count
from
  racers r join
  racing_classes rc on r.racing_class_id = rc.racing_class_id left join
  grades g on r.grade_id = g.grade_id left join
  race_results rr on
    r.car_number = rr.car_number and
    -- ensure everyone has a time recorded
    rr.round_number < ifnull((
        select min(x.round_number)
        from race_results x
        where x.time is null
    ), 999)
where
  r.bye_number is null
group by
  r.car_number,
  r.driver_name,
  g.name,
  rc.name,
  r.den
order by
  rc.racing_class_id,
  6 desc,
  g.grade_id,
  r.car_number
