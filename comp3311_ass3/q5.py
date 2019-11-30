import sys
import psycopg2

course = 'COMP1521'
if len(sys.argv) == 2:
    course = sys.argv[1]

course = course.upper()

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select t.name, cl.tag, cl.quota, count(e.person_id)
from classes cl
join terms on terms.name = '19T3'
join courses c on c.id = cl.course_id
join subjects s on c.subject_id = s.id and s.code = %s
join class_enrolments e on cl.id = e.class_id
join classtypes t on t.id = cl.type_id
group by cl.tag, t.name, cl.quota
having count(e.person_id) < cl.quota / 2
order by t.name
"""

cur = conn.cursor()
cur.execute(query, [course])
check = None
for tup in cur.fetchall():
    n_dull = tup[3] / tup[2] * 100
    print("%s %s is %d%% full" % (tup[0], ' '.join(tup[1].split()), n_dull))
    check = tup

conn.close()
