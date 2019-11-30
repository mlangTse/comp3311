import sys
import psycopg2

term = '19T1'
if len(sys.argv) == 2:
    term = sys.argv[1]

term = term.upper()

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select * from q7 where term = %s and time > 0
"""

query1 = """
select count(r.id) from rooms r
where r.code like 'K-%'
"""

def covert_time(start, end, n_week):
    return (int((end-start)/100) + abs(end%100/60.0-start%100/60.0)) * n_week

def overlap_week(x, y):
    overlap = 0
    not_overlap = 0
    for i in range(10):
        if y[i] == '1' and x[i] == y[i]:
            y = y[:i] + '0' + y[i+1:]
            overlap += 1
        elif y[i] == '1':
            not_overlap += 1
    return not_overlap, overlap

rooms = conn.cursor()
rooms.execute(query1)
tmp = rooms.fetchone()
conn.commit()
total_room = tmp[0]

cur = conn.cursor()
cur.execute(query, [term])
n_underused = 0
time = 0.0
prev = None
for tup in cur.fetchall():
    if prev is not None and prev[0] == tup[0] and prev[3] == tup[3]:
        if tup[4] >= prev[4] and tup[4] < prev[5] and tup[5] >= prev[5]:
            not_overlap, overlap = overlap_week(prev[6], tup[6])
            time += covert_time(prev[5], tup[5], overlap)
            time += covert_time(tup[4], tup[5], not_overlap)
            # if prev[0] == 100465:
            #     print(prev)
            #     print(tup)
            #     print(covert_time(prev[5], tup[5], overlap))
            #     print(covert_time(tup[4], tup[5], not_overlap))
            #     print()
        elif tup[4] >= prev[5]:
            time += float(tup[7])
    elif prev is not None and prev[0] == tup[0]:
        time += float(tup[7])

    if prev is not None and tup[0] != prev[0]:
        if time >= 200:
            n_underused += 1
        time = float(tup[7])

    prev = tup

avg = (1 - (float(n_underused) / float(total_room))) * 100
print('%.1f%%' % avg)

conn.close()
