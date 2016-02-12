import os, sys, logging, datetime, time, random, simplejson, calendar

sys.path.append('../')

from app import db
from app.models import *


import argparse
                 
log = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))    
stdout_handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(stdout_handler)

def timeit(func, *args):
    start = time.time()
    func(*args)
    end = time.time()
    
    return end - start

def initTimeframe(db, f = None):    
    s = ''
    log.debug("Initializing quarters")
    # q1 = Quarter()
    # q1.id = 1
    # q1.name = "First Quarter"
    # db.session.add(q1)
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 1, 'name' : "First Quarter"}

    # q2 = Quarter()
    # q2.id = 2
    # q2.name = "Second Quarter"
    # db.session.add(q2)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 2, 'name' : "Second Quarter"}
  
    # q3 = Quarter()
    # q3.id = 3
    # q3.name = "Third Quarter"
    # db.session.add(q3)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 3, 'name' : "Third Quarter"}

    # q4 = Quarter()
    # q4.id = 4
    # q4.name = "Fourth Quarter"
    # db.session.add(q4)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 4, 'name' : "Fourth Quarter"}
        
    log.debug("Initializing day of week")
    # dow = DayOfWeek()
    # dow.id = 0
    # dow.name = "Monday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 0, 'name' : "Monday"}

    # dow = DayOfWeek()
    # dow.id = 1
    # dow.name = "Tuesday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 1, 'name' : "Tuesday"}
    
    # dow = DayOfWeek()
    # dow.id = 2
    # dow.name = "Wednesday"
    # db.session.add(dow)
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 2, 'name' : "Wednesday"}

    # dow = DayOfWeek()
    # dow.id = 3
    # dow.name = "Thursday"
    # db.session.add(dow)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 3, 'name' : "Thursday"}
    
    # dow = DayOfWeek()
    # dow.id = 4
    # dow.name = "Friday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 4, 'name' : "Friday"}

    # dow = DayOfWeek()
    # dow.id = 5
    # dow.name = "Saturday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 5, 'name' : "Saturday"}

    # dow = DayOfWeek()
    # dow.id = 6
    # dow.name = "Sunday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 6, 'name' : "Sunday"}
    
    log.debug("Initializing months")
    # month = Month()
    # month.id = 1
    # month.name = "January"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 1, 'name' : "January"}
    
    # month = Month()
    # month.id = 2
    # month.name = "Febuary"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 2, 'name' : "February"}
    
    # month = Month()
    # month.id = 3
    # month.name = "March"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 3, 'name' : "March"}

    # month = Month()
    # month.id = 4
    # month.name = "April"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 4, 'name' : "April"}

    # month = Month()
    # month.id = 5
    # month.name = "May"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 5, 'name' : "May"}

    # month = Month()
    # month.id = 6
    # month.name = "June"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 6, 'name' : "June"}

    # month = Month()
    # month.id = 7
    # month.name = "July"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 7, 'name' : "July"}

    # month = Month()
    # month.id = 8
    # month.name = "August"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 8, 'name' : "August"}

    # month = Month()
    # month.id = 9
    # month.name = "September"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 9, 'name' : "September"}

    
    # month = Month()
    # month.id = 10
    # month.name = "October"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 10, 'name' : "October"}

    # month = Month()
    # month.id = 11
    # month.name = "November"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 11, 'name' : "November"}

    
    # month = Month()
    # month.id = 12
    # month.name = "December"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 12, 'name' : "December"}

    # db.session.commit()
    if f:
        f.write(s)
    return s
    
def initWeek(db, start_year, end_year, f = None, previous_year = True):
    # log.debug("Initializing weeks for year %s", year)
    s=''
    start = datetime.date(day = 1, month = 1, year = start_year)
    
    end =  datetime.date(day = 1, month = 1, year = end_year + 1)
    
    start_week = start - datetime.timedelta( days = start.weekday()) 
    
    # we only generate for weeks that started on the year
    if not previous_year:
        while start_week.year != start_year:
            start_week += datetime.timedelta(days = 7) 
 
    while start_week < end:
        #w = Week()
        
        # w.start = start_week
        # w.end = start_week + datetime.timedelta(days = 6 )
        t = '''INSERT INTO %(tablename)s ( start_of_week, end_of_week ) VALUES ( DATE '%(start)s', DATE '%(end)s');\n'''
        s += t % { 'tablename' : Week.__tablename__, 'start' : start_week.isoformat(), 'end' : ( start_week + datetime.timedelta(days = 6 ) ).isoformat()}

        # db.session.add(w)
        start_week += datetime.timedelta(days = 7)
    # db.session.commit()
    if f:
        f.write(s)
    return s

def initCalendar(db, year, f = None):
    start = datetime.date(day = 1, month = 1, year = year)
    end = start + datetime.timedelta(days = 365 if not calendar.isleap(year) else 366)
    d = Calendar()    
    curr = start
    s = ''
    while curr < end:
        d.date = curr
        t = '''INSERT INTO %(tablename)s ( raw_date, day, month, year, quarter, day_of_week, start_week ) VALUES ( DATE '%(raw_date)s', %(day)s, %(month)s, %(year)s, %(quarter)s, %(day_of_week)s, DATE '%(start_week)s');\n'''
        s += t % { 'tablename' : Calendar.__tablename__, 'raw_date' : curr.isoformat(), 'day' : d.day, 'month': d.month, 'year' : d.year, 'quarter' : d.quarter, 'day_of_week' : d.day_of_week, 'start_week' : d.start_week.isoformat() }
        curr += datetime.timedelta(days = 1)
    f.write(s)
    

def initTimeframe(db, f = None):    
    s = ''
    log.debug("Initializing quarters")
    # q1 = Quarter()
    # q1.id = 1
    # q1.name = "First Quarter"
    # db.session.add(q1)
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 1, 'name' : "First Quarter"}

    # q2 = Quarter()
    # q2.id = 2
    # q2.name = "Second Quarter"
    # db.session.add(q2)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 2, 'name' : "Second Quarter"}
  
    # q3 = Quarter()
    # q3.id = 3
    # q3.name = "Third Quarter"
    # db.session.add(q3)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 3, 'name' : "Third Quarter"}

    # q4 = Quarter()
    # q4.id = 4
    # q4.name = "Fourth Quarter"
    # db.session.add(q4)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 4, 'name' : "Fourth Quarter"}
        
    log.debug("Initializing day of week")
    # dow = DayOfWeek()
    # dow.id = 0
    # dow.name = "Monday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 0, 'name' : "Monday"}

    # dow = DayOfWeek()
    # dow.id = 1
    # dow.name = "Tuesday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 1, 'name' : "Tuesday"}
    
    # dow = DayOfWeek()
    # dow.id = 2
    # dow.name = "Wednesday"
    # db.session.add(dow)
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 2, 'name' : "Wednesday"}

    # dow = DayOfWeek()
    # dow.id = 3
    # dow.name = "Thursday"
    # db.session.add(dow)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 3, 'name' : "Thursday"}
    
    # dow = DayOfWeek()
    # dow.id = 4
    # dow.name = "Friday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 4, 'name' : "Friday"}

    # dow = DayOfWeek()
    # dow.id = 5
    # dow.name = "Saturday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 5, 'name' : "Saturday"}

    # dow = DayOfWeek()
    # dow.id = 6
    # dow.name = "Sunday"
    # db.session.add(dow)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 6, 'name' : "Sunday"}
    
    log.debug("Initializing months")
    # month = Month()
    # month.id = 1
    # month.name = "January"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 1, 'name' : "January"}
    
    # month = Month()
    # month.id = 2
    # month.name = "Febuary"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 2, 'name' : "February"}
    
    # month = Month()
    # month.id = 3
    # month.name = "March"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 3, 'name' : "March"}

    # month = Month()
    # month.id = 4
    # month.name = "April"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 4, 'name' : "April"}

    # month = Month()
    # month.id = 5
    # month.name = "May"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 5, 'name' : "May"}

    # month = Month()
    # month.id = 6
    # month.name = "June"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 6, 'name' : "June"}

    # month = Month()
    # month.id = 7
    # month.name = "July"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 7, 'name' : "July"}

    # month = Month()
    # month.id = 8
    # month.name = "August"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 8, 'name' : "August"}

    # month = Month()
    # month.id = 9
    # month.name = "September"
    # db.session.add(month)

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 9, 'name' : "September"}

    
    # month = Month()
    # month.id = 10
    # month.name = "October"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 10, 'name' : "October"}

    # month = Month()
    # month.id = 11
    # month.name = "November"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 11, 'name' : "November"}

    
    # month = Month()
    # month.id = 12
    # month.name = "December"
    # db.session.add(month)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 12, 'name' : "December"}

    # db.session.commit()
    if f:
        f.write(s)
    return s

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate all basic time data for ruther.')
    parser.add_argument('--start', dest='start_year', action='store',
                       help='The configuration file used to generate')

    parser.add_argument('--end', dest='end_year', action='store',
                       help='Destination filename where SQL output will be generated.')

    parser.add_argument('--output', dest='filename', action='store',
                       help='Destination filename where SQL output will be generated.')
    args = parser.parse_args()
    
    curr_path = os.getcwd()
    

    f = open(os.path.join(curr_path, args.filename),'w')


    
    log.debug("Starting ......")

    t = timeit(initTimeframe, db, f)
    log.debug("Time taken: %0.2f seconds", t)
    
    start_year = int (args.start_year)
    end_year = int (args.end_year)
    
    # start_date = datetime.date(day = 1, month = 1, year = start_year)

    f.write('BEGIN;\n')
    
    # curr = start_date
    # for i in range(start_year, end_year+1):
        # t = timeit(initWeek,db, i, f)
        # log.debug("Time taken: %0.2f seconds", t)
    t = timeit(initWeek,db, start_year, end_year, f)
    log.debug("Time taken: %0.2f seconds", t)

    for i in range(start_year, end_year+1):
        t = timeit(initCalendar,db, i, f)
        log.debug("Time taken: %0.2f seconds", t)
    f.write('COMMIT;\n')
    f.close()