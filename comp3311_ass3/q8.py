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

# print our the timetable
def output(best, hours):
    print('Total hours: %.1f' % float(hours))
    global days
    for day in days:
        for class_day in best:
            if class_day['day'] == day:
                print('  {}'.format(class_day['day']))
                all_class_in_day = sort_timetable_time(best, day)
                for c in all_class_in_day:
                    print('    {} {}: {}-{}'.format(c['course_name'], c['tag'], str(c['start']), str(c['end'])))
                break

# count the total time for particular timetable
def count_hour(best):
    done = []
    total = 0
    for time in best:
        if time['day'] not in done:
            all_class_in_day = sort_timetable_time(best, time['day'])
            start = all_class_in_day[0]['start']
            end = all_class_in_day[-1]['end']
            total += int((end-start) / 100) + abs(end % 100 / 60.0-start % 100 / 60.0)
            done.append(time['day'])

    total += len(done) * 2
    return total, len(done)

# check clash for a given timtable, day, start time and end time 
def no_clash(timetable, one_class):
    for course in timetable:
        if course['day'] == one_class['day'] and course != one_class:
            if one_class['start'] >= course['start'] and one_class['start'] < course['end']:
                return False
            if one_class['end'] > course['start'] and one_class['end'] <= course['end']:
                return False
            if one_class['start'] == course['start'] and one_class['end'] == course['end']:
                return False
    return True

def find_min(timetable):
    new = []
    best = None
    min_h = 24*7
    min_d = 8
    for course in timetable:
        new.append([y for x in course for y in x])

        clash = 0
        for each_class in new[-1]:
            if not no_clash(new[-1], each_class):
                clash = 1
                break

        if clash:
            new = new[:len(new)-1]
            continue

        count, min_day = count_hour(new[-1])
        if count <= min_h and min_day <= min_d:
            best = new[-1]
            min_h = count
            min_d = min_day
        else:
            new = new[:len(new)-1]
            continue

    return best, min_h

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
                    timetables[n].append([{'course_name': course['course_name'], 'tag': list(class_type)[0], 'day': k[3], 'start': k[4], 'end': k[5]}])
                    count += 1
                    flag = 0
                else:
                    timetables[n][count - 1].append({'course_name': course['course_name'], 'tag': list(class_type)[0], 'day': k[3], 'start': k[4], 'end': k[5]})
                prev = k
                i += 1
        n += 1

timetables = [list(item) for item in list(product(*timetables))]
best, min_hours = find_min(timetables)
output(best, min_hours)

conn.close()
