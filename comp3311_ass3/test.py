import sys
import psycopg2
import copy
from itertools import product

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
courses = ['COMP1511', 'MATH1131']
if len(sys.argv) >= 2:
    courses = []
    for i in range(1, len(sys.argv)):
        courses.append(sys.argv[i])
        i += 1

while len(courses) < 3:
    courses.append('None')

courses = [x.upper() for x in courses]

try:
    conn = psycopg2.connect('dbname=a3')
except:
    print("Can't connect to a3 database")
    sys.exit(1)

query = """
select * from q8_helper where (code = %s or code = %s or code = %s)
"""

query1 = """
select * from q8 where code = %s and tag = %s
"""

def sort_timetable_time(timetable, day):
    new = []
    for i in timetable:
        if i['day'] == day:
            new.append(i)
        for k in range(len(new)):
            for j in range(k, len(new)):
                if new[j]['start'] < new[k]['start']:
                    new[j], new[k] =  new[k], new[j]
    return new

def sort_timetable_day(timetable):
    global days
    for k in range(len(timetable)):
        for j in range(k, len(timetable)):
            if days.index(timetable[j][3]) < days.index(timetable[k][3]):
                timetable[j], timetable[k] = timetable[k], timetable[j]
    return timetable

# print our the timetable
def output(best, hours):
    print('Total hours: %.1f' % float(hours))
    global days
    for day in days:
        for class_day in best:
            if class_day['day'] == day:
                print('  ' + class_day['day'])
                all_class_in_day = sort_timetable_time(best, day)
                for c in all_class_in_day:
                    print('    ' + c['course_name'] + ' ' + c['tag'] + ': ' + str(c['start']) + '-' + str(c['end']))
                break

# count the total time for particular timetable
def count_hour(best):
    done = []
    total = 0
    for time in best:
        if time['day'] not in done:
            start, end = 0, 0
            all_class_in_day = sort_timetable_time(best, time['day'])
            for course in all_class_in_day:
                if start == 0:
                    start = course['start']
                end = course['end']
            total += int((end-start) / 100) + abs(end % 100 / 60.0-start % 100 / 60.0)
            done.append(time['day'])

    total += len(done) * 2
    return total

# check clash for a given timtable, day, start time and end time 
def no_clash(timetable, day, start, end):
    for course in timetable:
        if course['day'] == day:
            if start in range(course['start'], course['end']) or end in range(course['start'] + 1, course['end']):
                return False
    return True

def change_format(timetable):
    new = []
    n = 0
    for course in timetable:
        new.append([])
        for detail in course:
            for i in detail:
                if i == 'course_name':
                    continue
                for class_detail in detail[i]:
                    new[n].append({'course_name': detail['course_name'],
                                'tag': i,
                                'day': class_detail['day'],
                                'start': class_detail['start'],
                                'end': class_detail['end'],
                                })
        n += 1
    return new

# find all courses
course_table = []
for course in courses:
    if course != 'None':
        course_table.append({'course_name': course, 'course_detail': []})

# find all courses's class tag
for course in course_table:
    all_type = conn.cursor()
    all_type.execute(query, [courses[0], courses[1], courses[2]])
    for class_type in all_type.fetchall():
        if class_type[0] == course['course_name']:
            course['course_detail'].append({class_type[1]: None})

timetables = []
n = 0
for course in course_table:
    for class_type in course['course_detail']:
        timetables.append([])
        cur = conn.cursor()
        cur.execute(query1, [course['course_name'], list(class_type)[0]])
        count = 0
        flag = 1
        all_time = []
        for first in cur.fetchall():
            all_time.append(first)

        i = 0
        while i < len(all_time):
            flag = 1
            prev = None
            for k in all_time[i:]:
                if prev is not None and prev[0] != k[0]:
                    continue

                if flag:
                    timetables[n].append({'course_name': course['course_name'], list(class_type)[0]: []})
                    count += 1
                    flag = 0

                timetables[n][count - 1][list(class_type)[0]].append({'day': k[3], 'start': k[4], 'end': k[5]})
                prev = k
                i += 1
        n += 1

timetables = [list(item) for item in list(product(*timetables))]
timetables = change_format(timetables)

min_flag = 1
min_h = []
for timetable in timetables:
    flag = 0
    for each_class in timetable:
        timetable.remove(each_class)
        if not no_clash(timetable, each_class['day'], each_class['start'], each_class['end']):
            flag = 1
            timetable.append(each_class)
            break
        timetable.append(each_class)
    if flag == 1:
        timetables.remove(timetable)
        continue
    if min_flag == 1:
        min_h = timetable
        min_flag = 0
    elif count_hour(timetable) == 21:
        count = count_hour(min_h)
        output(min_h, count)
        timetables.remove(min_h)
        min_h = timetable

count = count_hour(min_h)
output(min_h, count)

conn.close()
