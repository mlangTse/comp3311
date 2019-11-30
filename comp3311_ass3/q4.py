import sys
import psycopg2

code = 'ENGG'
if len(sys.argv) == 2:
    code = sys.argv[1]

code = code.upper()

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select t.name, s.code, count(*) from course_enrolments e
inner join courses c on c.id = e.course_id
join terms t on c.term_id = t.id
join subjects s on s.id = c.subject_id
where SUBSTRING (s.code FROM 1 for 4) = %s
group by t.name, s.code
order by t.name, s.code
"""

cur = conn.cursor()
cur.execute(query, [code])
check = None
for tup in cur.fetchall():
    if check == tup[0]:
        continue
    
    print(tup[0])
    cur1 = conn.cursor()
    cur1.execute(query, [code])
    for tup1 in cur1.fetchall():
        if tup1[0] == tup[0]:
            print(' %s(%s)' % (tup1[1], tup1[2]))
    check = tup[0]
    
conn.close()
