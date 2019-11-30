import sys
import psycopg2

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select s.code, c.quota, count(*) from courses c
inner join terms t on t.name like '%T3' and c.term_id = t.id
inner join course_enrolments e on c.id = e.course_id
inner join subjects s on s.id = c.subject_id
where c.quota is not null and c.quota > 50
group by s.code, c.quota
having count(*) > c.quota
order by s.code
"""

cur = conn.cursor()
cur.execute(query)
for tup in cur.fetchall():
    exceed = tup[2] / tup[1] * 100
    print(tup[0], '%d%%' % round(exceed))

conn.close()
