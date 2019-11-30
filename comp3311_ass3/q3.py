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
select b.name, s.code from courses c
join terms t on t.name = '19T2' and c.term_id = t.id
join subjects s on s.id = c.subject_id
join classes cl on cl.course_id = c.id
join meetings m on m.class_id = cl.id
join rooms r on r.id = m.room_id
join buildings b on b.id = r.within
where SUBSTRING (s.code FROM 1 for 4) = %s
group by b.name, s.code
order by b.name
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
            print(' %s' % tup1[1])
    check = tup[0]
    
conn.close()
