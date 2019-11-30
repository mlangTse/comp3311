import sys
import psycopg2

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

all_combination = """
select weeks from meetings group by weeks 
"""

query = """
update meetings
set weeks_binary = %s
where weeks = %s
"""

def set_one(weeks_binary, start, end):
    if start - 1 < 0:
        return '1' * (end - start + 1) + weeks_binary[end + 1:]
    elif start == end:
        return weeks_binary[:start] + '1' + weeks_binary[end + 1:]
    else:
        return weeks_binary[:start] + '1' * (end - start + 1) + weeks_binary[end + 1:]

all_combine_week = conn.cursor()
all_combine_week.execute(all_combination)
for tup in all_combine_week.fetchall():
    weeks_binary = '0' * 11

    if 'N' in tup[0] or '<' in tup[0]:
        pass
    else:
        n_week = tup[0].split(',')
        for week in n_week:
            if '-' in week:
                s_and_e = week.split('-')
                start = s_and_e[0]
                end = s_and_e[1]
                weeks_binary = set_one(weeks_binary, int(start) - 1, int(end) - 1)
            else:
                weeks_binary = set_one(weeks_binary, int(week) - 1, int(week) - 1)

    cur = conn.cursor()
    cur.execute(query, (weeks_binary[:11], tup[0]))
    conn.commit()
conn.close()
