import sys
import psycopg2

incommon = 2
if len(sys.argv) == 2:
    incommon = sys.argv[1]

incommon = incommon.upper()

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select SUBSTRING (s.code FROM 5), count(*) from subjects s
group by SUBSTRING (s.code FROM 5)
having count(*) = %s
order by SUBSTRING (s.code FROM 5)
"""

query1 = """
select s.code from subjects s
where SUBSTRING (s.code FROM 5) = %s
order by s.code
"""

cur = conn.cursor()
cur.execute(query, [incommon])
for tup in cur.fetchall():
    cur1 = conn.cursor()
    cur1.execute(query1, [tup[0]])
    print('%s:' % tup[0], end = '')
    for tup1 in cur1.fetchall():
        print(' %s' % tup1[0][:4], end='')
    print()

conn.close()
