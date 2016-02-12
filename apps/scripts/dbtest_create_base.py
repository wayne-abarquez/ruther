import os, sys, logging, datetime, time, random, simplejson

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

aggr_kpi = '''
INSERT INTO kpi_type ( name ) VALUES ('Activations');
INSERT INTO kpi_type ( name ) VALUES ('Sellouts');
INSERT INTO kpi_type ( name ) VALUES ('Stocks');
INSERT INTO aggregation_function_map ( kpi_type, function_type ) VALUES (1, 0); 
INSERT INTO aggregation_function_map ( kpi_type, function_type ) VALUES (2, 0);
INSERT INTO aggregation_function_map ( kpi_type, function_type ) VALUES (3, 1);''';

def timeit(func, *args):
    start = time.time()
    func(*args)
    end = time.time()
    
    return end - start
def insertProduct(db, id, name):
    # p = Product()
    # p.id = id
    # p.name = id
    # p.group_id = group_id
    # db.session.add(p)
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s' );\n'''
    return t % { 'tablename' : Product.__tablename__, 'id' : id, 'name' : name }

def insertProductGroup(db, id, description, parent_id):
    # p = ProductGroup()
    # p.id = id
    # p.description = description
    # p.level_id = level_id
    # p.parent_level_id = parent_level_id
    # db.session.add(p)
    t = '''INSERT INTO %(tablename)s ( id, description, parent_id ) VALUES ( %(id)s, '%(desc)s', %(parent_id)s );\n'''
    return t % { 'tablename' : ProductGroup.__tablename__, 'id' : id, 'desc' : description, 'parent_id' : parent_id if parent_id else 'NULL'}
    
def insertProductGroupMap(db, product_id, group_id):
    # p = ProductGroupType()
    # p.id = id
    # p.name = name
    # p.level = level
    # db.session.add(p)
    # return p

    t = '''INSERT INTO %(tablename)s ( product_id, group_id ) VALUES ( %(product_id)s, %(group_id)s );\n'''
    return t % { 'tablename' : ProductGroupMap.__tablename__, 'product_id' : product_id, 'group_id' : group_id }

def initProducts( db, product_type_count, product_count_per_type, f = None):
    log.debug("initialize Products in database. %s product types, and %s products per type", product_type_count, product_count_per_type)
    p_count = 1
    s = ''
    # for i in range(1, product_type_count + 1): # product group type
        # pgt = insertProductGroupType(db, i, "product_group_%s" % ( i, ), 1)
        # s += pgt
       
    # db.session.commit()
    
    for i in range(1, product_type_count + 1): # product group type
        pg = insertProductGroup(db, i, "product_group_type_%s" % ( i, ), None)
        s+= pg
    # db.session.commit()

    
    for i in range(1, product_type_count + 1): # product group type        
        for j in range(1, product_count_per_type + 1):
            p = insertProduct(db, p_count, "Product_%s" % ( p_count, ), )
            s += p            

            p = insertProductGroupMap(db, i, p_count)
            s += p

            p_count += 1
    # db.session.commit()  
    if f:
        f.write(s)
    return s

def insertBoundaryLevelDesc(db, id, desc):
    # bt = BoundaryType()
    # bt.id = id
    # bt.name = name
    # bt.placemark_type = type
    # db.session.add(bt)
    # return bt
    t = '''INSERT INTO %(tablename)s ( id, description ) VALUES ( %(id)s, '%(description)s');\n'''
    return t % { 'tablename' : BoundaryLevelDesc.__tablename__, 'id' : id, 'description' : desc }

    
def insertBoundary(db, id, parent_id, type_id, name):
    # b = Boundary()
    # b.id = id
    # b.parent_id = parent_id
    # b.name = name
    # b.type_id = type_id
    # db.session.add(b)
    # return b 

    t = '''INSERT INTO %(tablename)s ( id, parent_id, name, level_id ) VALUES ( %(id)s, %(parent_id)s, '%(name)s', %(type)s );\n'''
    return t % { 'tablename' : Boundary.__tablename__, 'id' : id, 'parent_id': parent_id if parent_id else 'NULL', 'name' : name, 'type' : type_id }
    
def insertStore(db, id, name, boundary_id):
    # s = Store()
    # s.id = id,
    # s.name = name
    # s.boundary_id = boundary_id
    # db.session.add(s)
    # return s
    t = '''INSERT INTO %(tablename)s ( id, name, boundary_id ) VALUES ( %(id)s, '%(name)s', %(boundary_id)s );\n'''
    return t % { 'tablename' : Store.__tablename__, 'id' : id, 'name' : name, 'boundary_id' : boundary_id }


def initBoundariesStores(db, number_of_region, cluster_count_per_region, store_count_on_per_cluster, f = None):
    
    log.debug("Initialize boundaries, and stores. Number of regions: %s, Number of Cluster per region: %s, Number of outlets per cluster: %s",number_of_region, cluster_count_per_region, store_count_on_per_cluster)
    s = ''
    region = insertBoundaryLevelDesc(db, 1, "Region")
    cluster = insertBoundaryLevelDesc(db, 2, "Cluster")

    s += region
    s += cluster

    store_count = 0   
    region_count = 0
    cluster_count = 0
    
    for i in range(1, number_of_region + 1):        
        b = insertBoundary(db, i,None, 1, "Region_%s" % (i, ))
        s+=b
  # db.session.commit()
    
    cluster_count = number_of_region + 1
    for i in range(1, number_of_region + 1):           
        for j in range(1 , cluster_count_per_region + 1):
            c = insertBoundary(db, cluster_count, i, 2, "Cluster_%s" % (j,))
            cluster_count += 1
            s += c
    # db.session.commit()
    

    cluster_count = number_of_region + 1
    store_count = 1
    for i in range(1, number_of_region + 1):           
        for j in range(1, cluster_count_per_region + 1):
            for k in range (1, store_count_on_per_cluster + 1 ):
                st = insertStore(db, store_count, "Store_%s" % (store_count,), cluster_count) 
                store_count+=1 
                s += st
            cluster_count += 1
    if f:
        f.write(s)
    return s
    # db.session.commit()


# def initTimeframe(db, f = None):    
    # s = ''
    # log.debug("Initializing quarters")
    # # q1 = Quarter()
    # # q1.id = 1
    # # q1.name = "First Quarter"
    # # db.session.add(q1)
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Quarter.__tablename__, 'id' : 1, 'name' : "First Quarter"}

    # # q2 = Quarter()
    # # q2.id = 2
    # # q2.name = "Second Quarter"
    # # db.session.add(q2)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Quarter.__tablename__, 'id' : 2, 'name' : "Second Quarter"}
  
    # # q3 = Quarter()
    # # q3.id = 3
    # # q3.name = "Third Quarter"
    # # db.session.add(q3)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Quarter.__tablename__, 'id' : 3, 'name' : "Third Quarter"}

    # # q4 = Quarter()
    # # q4.id = 4
    # # q4.name = "Fourth Quarter"
    # # db.session.add(q4)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Quarter.__tablename__, 'id' : 4, 'name' : "Fourth Quarter"}
        
    # log.debug("Initializing day of week")
    # # dow = DayOfWeek()
    # # dow.id = 0
    # # dow.name = "Monday"
    # # db.session.add(dow)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 0, 'name' : "Monday"}

    # # dow = DayOfWeek()
    # # dow.id = 1
    # # dow.name = "Tuesday"
    # # db.session.add(dow)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 1, 'name' : "Tuesday"}
    
    # # dow = DayOfWeek()
    # # dow.id = 2
    # # dow.name = "Wednesday"
    # # db.session.add(dow)
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 2, 'name' : "Wednesday"}

    # # dow = DayOfWeek()
    # # dow.id = 3
    # # dow.name = "Thursday"
    # # db.session.add(dow)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 3, 'name' : "Thursday"}
    
    # # dow = DayOfWeek()
    # # dow.id = 4
    # # dow.name = "Friday"
    # # db.session.add(dow)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 4, 'name' : "Friday"}

    # # dow = DayOfWeek()
    # # dow.id = 5
    # # dow.name = "Saturday"
    # # db.session.add(dow)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 5, 'name' : "Saturday"}

    # # dow = DayOfWeek()
    # # dow.id = 6
    # # dow.name = "Sunday"
    # # db.session.add(dow)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 6, 'name' : "Sunday"}
    
    # log.debug("Initializing months")
    # # month = Month()
    # # month.id = 1
    # # month.name = "January"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 1, 'name' : "January"}
    
    # # month = Month()
    # # month.id = 2
    # # month.name = "Febuary"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 2, 'name' : "February"}
    
    # # month = Month()
    # # month.id = 3
    # # month.name = "March"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 3, 'name' : "March"}

    # # month = Month()
    # # month.id = 4
    # # month.name = "April"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 4, 'name' : "April"}

    # # month = Month()
    # # month.id = 5
    # # month.name = "May"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 5, 'name' : "May"}

    # # month = Month()
    # # month.id = 6
    # # month.name = "June"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 6, 'name' : "June"}

    # # month = Month()
    # # month.id = 7
    # # month.name = "July"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 7, 'name' : "July"}

    # # month = Month()
    # # month.id = 8
    # # month.name = "August"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 8, 'name' : "August"}

    # # month = Month()
    # # month.id = 9
    # # month.name = "September"
    # # db.session.add(month)

    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 9, 'name' : "September"}

    
    # # month = Month()
    # # month.id = 10
    # # month.name = "October"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 10, 'name' : "October"}

    # # month = Month()
    # # month.id = 11
    # # month.name = "November"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 11, 'name' : "November"}

    
    # # month = Month()
    # # month.id = 12
    # # month.name = "December"
    # # db.session.add(month)
    
    # t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    # s += t % { 'tablename' : Month.__tablename__, 'id' : 12, 'name' : "December"}

    # # db.session.commit()
    # if f:
        # f.write(s)
    # return s
    
def initWeek(db, year, f = None):
    log.debug("Initializing weeks for year %s", year)
    s=''
    start = datetime.date(day = 1, month = 1, year = year)
    end = start + datetime.timedelta(days = 365)
    
    start_week = start - datetime.timedelta( days = start.weekday())
    
    while start_week.year != year:
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
    end = start + datetime.timedelta(days = 365)
    d = Calendar()    
    curr = start
    s = ''
    while curr < end:
        d.date = curr
        t = '''INSERT INTO %(tablename)s ( raw_date, day, month, year, quarter, day_of_week, start_week ) VALUES ( DATE '%(raw_date)s', %(day)s, %(month)s, %(year)s, %(quarter)s, %(day_of_week)s, DATE '%(start_week)s');\n'''
        s += t % { 'tablename' : Calendar.__tablename__, 'raw_date' : curr.isoformat(), 'day' : d.day, 'month': d.month, 'year' : d.year, 'quarter' : d.quarter, 'day_of_week' : d.day_of_week, 'start_week' : d.start_week.isoformat() }
        curr += datetime.timedelta(days = 1)
    f.write(s)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate all basic data for ruther, minus KPI, in SQL format.')
    parser.add_argument('--json-input', dest='json_filename', action='store',
                       help='The configuration file used to generate')

    parser.add_argument('--output-filename', dest='filename', action='store',
                       help='Destination filename where SQL output will be generated.')
    
    args = parser.parse_args()
    
    curr_path = os.getcwd()
    
    f = open(os.path.join(curr_path, args.json_filename),'r')
    params = simplejson.loads(f.read())
    f.close()
    
    f = open(os.path.join(curr_path, args.filename),'w')
    f.write(aggr_kpi)
    f.write('BEGIN;\n')

    
    log.debug("Starting ......")
    
    t = timeit(initProducts, db, params['product_types'], params['products_per_type'], f) 
    log.debug("Time taken: %0.2f seconds", t)

    t = timeit(initBoundariesStores,db, params['region_count'], params['cluster_per_region'], params['store_per_cluster'], f)
    log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initTimeframe, db, f)
    # log.debug("Time taken: %0.2f seconds", t)
    
    # start = datetime.date(day = 1, month = 1, year = 2009)
    # start_week = start - datetime.timedelta( days = start.weekday())
    # t = '''INSERT INTO %(tablename)s ( start_of_week, end_of_week ) VALUES ( DATE '%(start)s', DATE '%(end)s');\n'''
    # t = t % { 'tablename' : Week.__tablename__, 'start' : start_week.isoformat(), 'end' : ( start_week + datetime.timedelta(days = 6 ) ).isoformat()}
    # f.write (t)
    
    # t = timeit(initWeek,db, 2009, f)
    # log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initWeek,db, 2010, f)
    # log.debug("Time taken: %0.2f seconds", t)
   
    # t = timeit(initWeek,db, 2011, f)
    # log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initWeek,db, 2012, f)
    # log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initCalendar,db, 2009, f)
    # log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initCalendar, db, 2010, f)
    # log.debug("Time taken: %0.2f seconds", t)
    
    # t = timeit(initCalendar,db, 2011, f)
    # log.debug("Time taken: %0.2f seconds", t)

    # t = timeit(initCalendar, db, 2012, f)
    # log.debug("Time taken: %0.2f seconds", t)
    f.write('COMMIT;\n')
    f.close()