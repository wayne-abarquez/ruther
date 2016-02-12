import os, sys, logging, datetime, time, random, simplejson, argparse
sys.path.append('../')

from app import db
from app.models import *

                 
log = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))    
stdout_handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(stdout_handler)

def initKPI(db, kpi_id, start_date, end_date, f = None):
    random_kpi_values = lambda: random.randint(0, 100)
    random_actual_values = lambda: random.randint(100, 400)
    #random_kpi_values = [0, 33, 66, 100]
    #random_actual_values = [ 100, 200, 300, 400]
    kpi_count = kpi_id
    # try:
        # log.debug("Initializing KPI types")
        # activation = KPIType()
        # activation.id = 1
        # activation.name = "Activation"
        # db.session.add(activation)
        # db.session.commit()
    # except:
        # db.session.rollback()
    
    # try:
        # sellout = KPIType()
        # sellout.id = 2
        # sellout.name = "Sellout"
        # db.session.add(sellout)
        # db.session.commit()
    # except:
        # db.session.rollback()
    # try:
        # stock = KPIType()
        # stock.id = 3
        # stock.name = "Stock"
        # db.session.add(stock)
        
        # db.session.commit()
    # except:
        # db.session.rollback()
        
    # kpis = (activation, sellout, stock)
    
    kpis = KPIType.query.all()
    log.debug("Initializing KPI data for %s to %s", start_date.isoformat(), end_date.isoformat())
    td = end_date - start_date
    curr = start_date
    
    outlets = Facility.query.all()
    products = Product.query.all()
    
    o_count = len(outlets)
    p_count = len(products)
    # ret = db.session.execute('''SELECT id from KPI ORDER BY ID DESC LIMIT 1''')
    # kpi_count = 1
    # for i in ret:
        # kpi_count = int(i[0]) + 1

    for i in range(0, td.days):
        s = ''
        log.debug("Adding KPI Data for %s across %s outlets with %s products", curr.isoformat(), o_count, p_count)

        d = Calendar.query.filter_by(raw_date = curr)[0]
            
        for o in outlets:
            # log.debug('Outlet: %s Date: %s', o.name, d.date.isoformat())
            for p in products:
                for t in kpis:
                    #_randint = random.randint(0, 3)
                    actual, kpi = random_actual_values(), random_kpi_values()
                    target, kpi = random_actual_values(), random_kpi_values()
                    s+='''%(id)s,%(product_id)s,%(facility_boundary_id)s,%(facility_boundary_level_id)s,%(facility_boundary_parent_id)s,%(facility_id)s,%(facility_type_id)s, %(type)s,%(kpi)s,%(actual)s,%(target)s,'%(date)s',%(date_day)s,%(date_month)s,%(date_year)s,%(date_quarter)s,'%(date_start_of_week)s','%(date_end_of_week)s',%(calendar_id)s\n''' % ( { 'id' : kpi_count, 
                    'product_id' :p.id,  
                    'facility_id' : o.id, 'facility_type_id' : o.facility_type_id, 'facility_boundary_id' : o.boundary_id, 'facility_boundary_parent_id' : o.boundary.parent_id if o.boundary.parent_id else '', 'facility_boundary_level_id' : o.boundary.level_id, 
                    'type': t.id, 'date': d.raw_date.isoformat(), 'date_day' : d.day, 'date_month' : d.month, 'date_year' : d.year, 'date_quarter' : d.quarter, 'date_start_of_week' : d.start_of_week, 'date_end_of_week' : d.end_of_week, 'actual' : actual , 'target': target, 'kpi': kpi, 'calendar_id': d.id })
                    kpi_count += 1
        curr += datetime.timedelta(days = 1)
        f.write(s)
        
    return kpi_count


# def initSalesForce(db, kpi_id, start_date, end_date, f = None):
    # random_kpi_values = lambda: random.randint(0, 100)
    # random_actual_values = lambda: random.randint(100, 400)
    # #random_kpi_values = [0, 33, 66, 100]
    # #random_actual_values = [ 100, 200, 300, 400]
    # kpi_count = kpi_id

    
    # kpis = SalesForceKPIType.query.all()
    # log.debug("Initializing KPI data for %s to %s", start_date.isoformat(), end_date.isoformat())
    # td = end_date - start_date
    # curr = start_date
    
    # outlets = Facility.query.all()
    # products = Product.query.all()
    
    # o_count = len(outlets)
    # p_count = len(products)
    # # ret = db.session.execute('''SELECT id from KPI ORDER BY ID DESC LIMIT 1''')
    # # kpi_count = 1
    # # for i in ret:
        # # kpi_count = int(i[0]) + 1
    # sf = SalesForce.query.all()
    # for i in range(0, td.days):
        # s = ''
        # log.debug("Adding KPI Data for %s across %s outlets with %s products", curr.isoformat(), o_count, p_count)

        # d = Calendar.query.filter_by(raw_date = curr)[0]
            
        # for o in outlets:
            # # log.debug('Outlet: %s Date: %s', o.name, d.date.isoformat())

            # for obj in sf:
                # for t in kpis:
                    # #_randint = random.randint(0, 3)
                    # actual, kpi = random_actual_values(), random_kpi_values()
                    # target, kpi = random_actual_values(), random_kpi_values()
                    # s+='''%(id)s,%(sales_force_id)s, %(sales_force_role_id)s, %(type)s,%(kpi)s,%(actual)s,%(target)s,'%(date)s',%(date_day)s,%(date_month)s,%(date_year)s,%(date_quarter)s,'%(date_start_of_week)s','%(date_end_of_week)s',%(calendar_id)s\n''' % ( { 'id' : kpi_count, 
                    # 'type': t.id, 'sales_force_id' : obj.id, 'sales_force_role_id' : obj.sf_role_id, 'date': d.raw_date.isoformat(), 'date_day' : d.day, 'date_month' : d.month, 'date_year' : d.year, 'date_quarter' : d.quarter, 'date_start_of_week' : d.start_of_week, 'date_end_of_week' : d.end_of_week, 'actual' : actual , 'target': target, 'kpi': kpi, 'calendar_id': d.id })
                    # kpi_count += 1
        # curr += datetime.timedelta(days = 1)
        # f.write(s)
        
    # return kpi_count

def init_subtype_day (db, start_date, end_date, f = None):
    random_kpi_values = lambda: random.randint(0, 100)
    random_actual_values = lambda: random.randint(100, 400)
    #random_kpi_values = [0, 33, 66, 100]
    #random_actual_values = [ 100, 200, 300, 400]

    td = end_date - start_date
    curr = start_date
    
    boundaries = Boundary.query.all()
    products = Product.query.all()
    
    o_count = len(boundaries)
    p_count = len(products)
    # ret = db.session.execute('''SELECT id from KPI ORDER BY ID DESC LIMIT 1''')
    # kpi_count = 1
    # for i in ret:
        # kpi_count = int(i[0]) + 1
    subtypes = SmartfrenOutletProductClassificationType.query.all()
    kpi_count = 0
    for i in range(0, td.days):

        log.debug("Adding outlet subclassification Data for %s across %s boundaries with %s products", curr.isoformat(), o_count, p_count)

        d = Calendar.query.filter_by(raw_date = curr)[0]
            
        for o in boundaries:
            s = ''
            # log.debug('Outlet: %s Date: %s', o.name, d.date.isoformat())
            for p in products:
                for n in subtypes:
                    #_randint = random.randint(0, 3)
                    outlet_count, kpi = random_actual_values(), random_kpi_values()
                    total_activation, kpi = random_actual_values(), random_kpi_values()
                    s+=''''%(outlet_subtype_classification)s',%(id)s,%(product_id)s,%(boundary_id)s,%(boundary_level_id)s,%(boundary_parent_id)s,%(outlet_count)s,%(total_activation)s,'%(date)s',%(date_day)s,%(date_month)s,%(date_year)s,%(date_quarter)s,'%(date_start_of_week)s','%(date_end_of_week)s',%(calendar_id)s\n''' % ( { 'id' : kpi_count, 
                    'product_id' :p.id,  'outlet_subtype_classification' : n.type_name,
                    'boundary_id' : o.id, 'boundary_parent_id' : o.parent_id if o.parent_id else '', 'boundary_level_id' : o.level_id, 
                    'date': d.raw_date.isoformat(), 'date_day' : d.day, 'date_month' : d.month, 'date_year' : d.year, 'date_quarter' : d.quarter, 'date_start_of_week' : d.start_of_week, 'date_end_of_week' : d.end_of_week, 'outlet_count' : outlet_count , 'total_activation': total_activation, 'calendar_id': d.id })
                    kpi_count +=1
            f.write(s)

        curr += datetime.timedelta(days = 1)

def init_subtype_week (db, start_of_week, end_of_week, f = None, kpi_count = 0):
    random_kpi_values = lambda: random.randint(0, 100)
    random_actual_values = lambda: random.randint(100, 400)
    #random_kpi_values = [0, 33, 66, 100]
    #random_actual_values = [ 100, 200, 300, 400]

    td = end_date - start_date
    curr = start_date
    
    boundaries = Boundary.query.all()
    products = Product.query.all()
    
    o_count = len(boundaries)
    p_count = len(products)
    # ret = db.session.execute('''SELECT id from KPI ORDER BY ID DESC LIMIT 1''')
    # kpi_count = 1
    # for i in ret:
        # kpi_count = int(i[0]) + 1
    subtypes = SmartfrenOutletProductClassificationType.query.all()
    

    s = ''
    log.debug("Adding outlet subclassification Data for week %s across %s boundaries with %s products", start_of_week.isoformat(), o_count, p_count)

    t = kpi_count
    for o in boundaries:
        s = ''
        # log.debug('Outlet: %s Date: %s', o.name, d.date.isoformat())
        for p in products:
            for n in subtypes:
                #_randint = random.randint(0, 3)
                outlet_count, kpi = random_actual_values(), random_kpi_values()
                total_activation, kpi = random_actual_values(), random_kpi_values()
                
                s+=''''%(outlet_subtype_classification)s',%(id)s,%(product_id)s,%(boundary_id)s,%(boundary_level_id)s,%(boundary_parent_id)s,%(outlet_count)s,%(total_activation)s,'%(date_start_of_week)s','%(date_end_of_week)s'\n''' % ( { 'id' : t, 
                'product_id' :p.id,  'outlet_subtype_classification' : n.type_name,
                'boundary_id' : o.id, 'boundary_parent_id' : o.parent_id if o.parent_id else '', 'boundary_level_id' : o.level_id, 
                'date_start_of_week' : start_of_week, 'date_end_of_week' : end_of_week, 'outlet_count' : outlet_count , 'total_activation': total_activation })
                t += 1

        f.write(s)
    return t
        
def init_subtype_month (db, month, year, f = None):
    random_kpi_values = lambda: random.randint(0, 100)
    random_actual_values = lambda: random.randint(100, 400)
    #random_kpi_values = [0, 33, 66, 100]
    #random_actual_values = [ 100, 200, 300, 400]

    td = end_date - start_date
    curr = start_date
    
    boundaries = Boundary.query.all()
    products = Product.query.all()
    
    o_count = len(boundaries)
    p_count = len(products)

    subtypes = SmartfrenOutletProductClassificationType.query.all()
    
 
    
    log.debug("Adding outlet subclassification Data for month %s year %s across %s boundaries with %s products", month, year, o_count, p_count)

    kpi_count = 0
    for o in boundaries:
        s = ''
        for p in products:
            for n in subtypes:

                outlet_count, kpi = random_actual_values(), random_kpi_values()
                total_activation, kpi = random_actual_values(), random_kpi_values()
                s+=''''%(outlet_subtype_classification)s',%(id)s,%(product_id)s,%(boundary_id)s,%(boundary_level_id)s,%(boundary_parent_id)s,%(outlet_count)s,%(total_activation)s,%(date_month)s,%(date_year)s\n''' % ( { 'id' : kpi_count, 
                'product_id' :p.id,  'outlet_subtype_classification' : n.type_name,
                'boundary_id' : o.id, 'boundary_parent_id' : o.parent_id if o.parent_id else '', 'boundary_level_id' : o.level_id, 
                'date_month' : int(month), 'date_year' : int(year), 'outlet_count' : outlet_count , 'total_activation': total_activation })
                kpi_count += 1
        f.write(s)      
    
def init_subtype_year (db, year, f = None):
    random_kpi_values = lambda: random.randint(0, 100)
    random_actual_values = lambda: random.randint(100, 400)

    td = end_date - start_date
    curr = start_date
    
    boundaries = Boundary.query.all()
    products = Product.query.all()
    
    o_count = len(boundaries)
    p_count = len(products)

    subtypes = SmartfrenOutletProductClassificationType.query.all()
 
    s = ''
    log.debug("Adding outlet subclassification Data for year %s across %s boundaries with %s products", year, o_count, p_count)
    kpi_count = 0
    for o in boundaries:
        s = ''
        for p in products:
            for n in subtypes:
                outlet_count, kpi = random_actual_values(), random_kpi_values()
                total_activation, kpi = random_actual_values(), random_kpi_values()
                s+=''''%(outlet_subtype_classification)s',%(id)s,%(product_id)s,%(boundary_id)s,%(boundary_level_id)s,%(boundary_parent_id)s,%(outlet_count)s,%(total_activation)s,%(date_year)s\n''' % ( { 'id' : kpi_count, 
                'product_id' :p.id,  'outlet_subtype_classification' : n.type_name,
                'boundary_id' : o.id, 'boundary_parent_id' : o.parent_id if o.parent_id else '', 'boundary_level_id' : o.level_id, 
                'date_year' : int(year), 'outlet_count' : outlet_count , 'total_activation': total_activation })
                kpi_count += 1
        f.write(s)        


def timeit(func, *args):
    start = time.time()
    ret = func(*args)
    end = time.time()
    
    return end - start, ret
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Boundaries, Products, Stores data.')
    parser.add_argument('--year', dest='year', action='store',
                       help='Input file in JSON format.')

    parser.add_argument('--month', dest='month', action='store',
                       help='Destination filename where SQL output will be generated.')

    parser.add_argument('--day', dest='day', action='store',
                       help='Destination filename where SQL output will be generated.')
    parser.add_argument('--dest', dest='dest', action='store',
                       help='Destination filename where SQL output will be generated.')
    args = parser.parse_args()
    
    year = int(args.year)
    month = 0
    path = os.getcwd()
    if args.dest:
        path = os.path.join(path, args.dest)

    if args.month:
        month = int(args.month)
  
    day = 0
    if args.day:
        day = int(args.day)

    ret = db.session.execute('''SELECT id from KPI ORDER BY ID DESC LIMIT 1''')
    kpi_id = 1
    for i in ret:
        kpi_id = int(i[0]) + 1
    
    if args.year and args.month and args.day:
        f = open(os.path.join(path,'kpi.sql'),'w')    
        start_date = datetime.date(day = args.day, month = args.month, year =args. year)
        end_date = start_date + datetime.timedelta(days=1)
        s += '''SELECT add_KPI_partition_table('%(year)s', '%(month)s');\n''' % ( { 'year' : args.year, 'month' : args.month })
        s+= '''COPY  %s (id, product_id, facility_id, type, kpi, raw_date, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week, calendar_id ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'kpi.csv' ))
        f.write(s)
        f.close()
        
        f = open('kpi.csv', 'w')
        t, kpi_id = timeit(initKPI, db, kpi_id, start_date, end_date, f)
        log.debug("Time taken: %0.2f seconds", t)
        f.close()
    elif args.year and args.month:
        f = open(os.path.join(path, 'kpi_y%s_m%s.sql' % (int(args.year), args.month)),'w')
        start_date = datetime.date(day = 1, month = int(args.month), year = int(args.year))
        end_date = datetime.date(day=1, month = int(args.month) + 1, year = int(args.year) if (int(args.month) + 1 ) <= 12 else ( args.year + 1)) - datetime.timedelta(days=1)
        tablename = 'kpi_y%s_m%s' % ( year, month)
        s= ''
        s += '''SELECT add_KPI_partition_table('%(year)s', '%(month)s');\n''' % ( { 'year' : int(args.year), 'month' : int( args.month ) })
        s += '''COPY  %s (id, product_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, facility_id, facility_type_id, kpi_type, kpi, actual, target, raw_date, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week, calendar_id ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'kpi_y%s_m%s.csv' % (year, month)))
       
        f.write(s)
        f.close()
        
        f = open(os.path.join(path, 'kpi_y%s_m%s.csv' % (args.year, args.month)),'w')
        t, kpi_id = timeit(initKPI, db,  kpi_id, start_date, end_date, f)
        f.close()
        log.debug("Time taken: %0.2f seconds", t)
        
        f = open(os.path.join(path, 'subtype_y%s_m%s.sql' % (int(args.year), args.month)),'w')
        start_date = datetime.date(day = 1, month = int(args.month), year = int(args.year))
        end_date = datetime.date(day=1, month = int(args.month) + 1, year = int(args.year) if (int(args.month) + 1 ) <= 12 else ( args.year + 1)) - datetime.timedelta(days=1)
        tablename = 'smartfren_outlet_product_classification_day'
        s= ''
        #s += '''SELECT add_KPI_partition_table('%(year)s', '%(month)s');\n''' % ( { 'year' : int(args.year), 'month' : int( args.month ) })
        s += '''COPY  %s (outlet_subtype_classification, id, product_id, boundary_id, boundary_level_id, boundary_parent_id, outlet_count, total_activation, raw_date, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week, calendar_id ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'subtype_day_y%s_m%s.csv' % (year, month)))
        tablename = 'smartfren_outlet_product_classification_month'
        s += '''COPY  %s (outlet_subtype_classification, id, product_id, boundary_id, boundary_level_id, boundary_parent_id, outlet_count, total_activation, date_month, date_year ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'subtype_month_y%s_m%s.csv' % (year, month)))
        tablename = 'smartfren_outlet_product_classification_year'
        s += '''COPY  %s (outlet_subtype_classification, id, product_id, boundary_id, boundary_level_id, boundary_parent_id, outlet_count, total_activation, date_year ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'subtype_year_y%s_m%s.csv' % (year, month)))
        tablename = 'smartfren_outlet_product_classification_week'
        s += '''COPY  %s (outlet_subtype_classification, id, product_id, boundary_id, boundary_level_id, boundary_parent_id, outlet_count, total_activation, date_start_of_week, date_end_of_week ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'subtype_week_y%s_m%s.csv' % (year, month)))

        f.write(s)
        f.close()
        
        f = open(os.path.join(path, 'subtype_day_y%s_m%s.csv' % (args.year, args.month)),'w')
        t = timeit(init_subtype_day, db, start_date, end_date, f)
        f.close()
        
        f = open(os.path.join(path, 'subtype_month_y%s_m%s.csv' % (args.year, args.month)),'w')
        t = timeit(init_subtype_month, db, int(args.month), int(args.year), f)
        f.close()
        
        f = open(os.path.join(path, 'subtype_year_y%s_m%s.csv' % (args.year, args.month)),'w')
        t = timeit(init_subtype_year, db, int(args.year), f)
        f.close()
        
        f = open(os.path.join(path, 'subtype_week_y%s_m%s.csv' % (args.year, args.month)),'w')
        start_weeks = set()
        
        for obj in Calendar.query.filter_by(month = int(args.month), year = int(args.year)):
            start_weeks.add(obj.start_week)
        kpi_count = 0
        for obj in start_weeks:
            t, kpi_count = timeit(init_subtype_week, db, obj, obj + datetime.timedelta(days = 6 ), f, kpi_count)
        f.close()
        
        #log.debug("Time taken: %0.2f seconds", t[0])
        
        
        # f = open(os.path.join(path, 'sales_force_y%s_m%s.sql' % (int(args.year), args.month)),'w')
        # start_date = datetime.date(day = 1, month = int(args.month), year = int(args.year))
        # end_date = datetime.date(day=1, month = int(args.month) + 1, year = int(args.year) if (int(args.month) + 1 ) <= 12 else ( args.year + 1)) - datetime.timedelta(days=1)
        # tablename = 'ruther_sales_force_kpi_daily'
        # s= ''
        # # s += '''SELECT add_KPI_partition_table('%(year)s', '%(month)s');\n''' % ( { 'year' : int(args.year), 'month' : int( args.month ) })
        # s += '''COPY  %s (id, sales_force_id, sales_force_role_id, data_type, kpi, actual, target, raw_date, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week, calendar_id ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'sf_y%s_m%s.csv' % (year, month)))
       
        # f.write(s)
        # f.close()
        
        # f = open(os.path.join(path, 'sf_y%s_m%s.csv' % (args.year, args.month)),'w')
        # t, kpi_id = timeit(initSalesForce, db,  kpi_id, start_date, end_date, f)
        # f.close()
        # log.debug("Time taken: %0.2f seconds", t)
    elif args.year:
        s=''
        year = int(args.year)
        for i in range (7, 8):
        
            f=open(os.path.join(path, 'kpi_y%s_m%s.csv' % (year, i)), 'w')
            start_date = datetime.date(day = 1, month = i, year = year)
            end_date = datetime.date(day=1, month = i + 1 if i < 12 else 1, year = year if i < 12 else year + 1)
            tablename = 'kpi_y%s_m%s' % ( year, i)
            s += '''SELECT add_KPI_partition_table('%(year)s', '%(month)s');\n''' % ( { 'year' : year, 'month' : i })
            s += '''COPY  %s (id, product_id, facility_boundary_id, facility_boundary_level_id, facility_boundary_parent_id, facility_id, facility_type_id, kpi_type, kpi, actual, target, raw_date, date_day, date_month, date_year, date_quarter, date_start_of_week, date_end_of_week, calendar_id ) FROM '%s'  DELIMITER ',' CSV;\n ''' % (tablename, os.path.join(path, 'kpi_y%s_m%s.csv' % (year, i)))

            t, kpi_id = timeit(initKPI, db, kpi_id, start_date, end_date, f)
            f.close()
            log.debug("Time taken: %0.2f seconds", t)
        # end for
        f = open(os.path.join(path, 'kpi_y%s.sql' % (args.year,)), 'w')
        f.write(s)
        f.close()
        
  
