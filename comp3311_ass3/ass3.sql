-- Q6. In the Meetings table, the weeks column currently stores the 11 weeks a meeting runs in the format "1-5,7-10" or "2,4,6,8,10". While this makes sense to a human, it's not a friendly format to use when processing large datasets.
create or replace view Q6(weeks)
as
select weeks from meetings group by weeks 
;

-- Q7. What percentage of all rooms at UNSW are underused during a term at UNSW? Underused is defined as when across weeks 1-10 inclusive, the room is used on average for less than 20 hours a week
create or replace view Q7(id, code, term, meeting_day, start_time, end_time, weeks_binary)
as
select r.id, r.code, t.name, m.day, m.start_time, m.end_time, m.weeks_binary,
round(((m.end_time-m.start_time) / 100 + abs(m.end_time % 100 / 60.0-m.start_time % 100 / 60.0))
* length(replace(substring(m.weeks_binary, 1, 10), '0', '')), 1) as time
from rooms r
join meetings m on m.room_id = r.id
join classes cl on cl.id = m.class_id
join courses c on cl.course_id = c.id
join terms t on c.term_id = t.id
where r.code ilike 'K-%'
group by r.id, r.code, t.name, m.day, m.start_time, m.end_time, m.weeks_binary
order by r.code, m.day, m.start_time, m.end_time, m.weeks_binary
;

-- Q8. Produce a timetable for 19T3 for 1, 2 or 3 courses that aims to minimise the amount of hours being spent in a week on campus or commuting.
create or replace view Q8(id, code, tag, day, start_time, end_time, total_time)
as
select cl.id, s.code, t.name, m.day, m.start_time, m.end_time,
round((m.end_time-m.start_time) / 100 + abs(m.end_time % 100 / 60.0-m.start_time % 100 / 60.0), 1) as time
from classes cl
join meetings m on m.class_id = cl.id
join rooms r on m.room_id = r.id and r.code ilike 'K-%'
join courses c on cl.course_id = c.id
join terms on terms.name = '19T3' and terms.id = c.term_id
join subjects s on s.id = c.subject_id
join classtypes t on t.id = cl.type_id
order by cl.id, t.name, m.day, m.start_time
;

create or replace view Q8_helper(code, tag)
as
select s.code, t.name
from classes cl
join meetings m on m.class_id = cl.id
join rooms r on m.room_id = r.id and r.code ilike 'K-%'
join courses c on cl.course_id = c.id
join terms on terms.name = '19T3' and terms.id = c.term_id
join subjects s on s.id = c.subject_id
join classtypes t on t.id = cl.type_id
group by s.code, t.name
order by s.code, t.name
;
