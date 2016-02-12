import os, sys, logging, datetime, time, random
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

# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# kpi_count = 0
def initPartitionKPI(db, year,  month):
    start = datetime.date(day = 1, month = month, year = year)
    end = datetime.date(day = 1, month = month + 1 if month < 12 else 1, year = year if month < 12 else year + 1)
    tablename = 'KPI_y%sm%s' % (year, month)
    

    pt_table= '''
    CREATE TABLE %s (
        CHECK ( date >= DATE '%s'  AND date < DATE '%s' )
    ) INHERITS (kpi);
    CREATE INDEX %s_date ON %s (date);
    
    ''' % (tablename, start.isoformat(), end.isoformat(), tablename, tablename)
    trig_func = '''
CREATE OR REPLACE FUNCTION KPI_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO %s VALUES (NEW.*);
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;
''' % ( tablename, )
    
    add_trig = '''CREATE TRIGGER KPI_insert_trigger
    BEFORE INSERT ON KPI
    FOR EACH ROW EXECUTE PROCEDURE KPI_insert_trigger();'''
    
    ret = db.session.execute(pt_table)
    # for i in ret:
        # log.debug(i)
        
    ret = db.session.execute(trig_func)
    # for i in ret:
        # log.debug(i)
    
    ret = db.session.execute(add_trig)
    # for i in ret:
        # log.debug(i)        
 
def partitionKPI(db, year, month):
    start = datetime.date(day = 1, month = month, year = year)
    end = datetime.date(day = 1, month = month + 1 if month < 12 else 1, year = year if month < 12 else year + 1)
    tablename = 'KPI_y%sm%s' % (year, month)
    pt_table= '''
    CREATE TABLE %s (
        CHECK ( date >= DATE '%s'  AND date < DATE '%s' )
    ) INHERITS (kpi);
    CREATE INDEX %s_date ON %s (date);
    
    ''' % (tablename, start.isoformat(), end.isoformat(), tablename, tablename)
    trig_func = '''
CREATE OR REPLACE FUNCTION KPI_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO %s VALUES (NEW.*);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;
''' % ( tablename, )
    
    ret = db.session.execute(pt_table)
    # for i in ret:
        # log.debug(i)   

    ret = db.session.execute(trig_func)
    # for i in ret:
        # log.debug(i)
        
       

        
        
def initKPI(db, start_date, end_date):
    log.debug("Initializing KPI types")
    activation = KPIType()
    activation.id = 1
    activation.name = "Activation"
    db.session.add(activation)
    
    sellout = KPIType()
    sellout.id = 2
    sellout.name = "Sellout"
    db.session.add(sellout)
    
    stock = KPIType()
    stock.id = 3
    stock.name = "Stock"
    db.session.add(stock)
    
    db.session.commit()
    kpis = (activation, sellout, stock)
    log.debug("Initializing KPI data for %s to %s", start_date.isoformat(" "), end_date.isoformat(" "))
    td = end_date - start_date
    curr = start_date
    
    outlets = Store.query.all()
    products = Product.query.all()
    
    o_count = len(outlets)
    p_count = len(products)
    kpi_count = 1
    for i in range(0, td.days):
        # start = time.time()
        # kpi_count = addKPI(db, curr, outlets, products, kpis, kpi_count)
        # end = time.time()
        # log.debug("Time taken: %0.2f", end - start)
        log.debug("Adding KPI Data for %s across %s outlets with %s products", curr.isoformat(" "), o_count, p_count)
        d = Calendar()
        d.date = curr
        db.session.add(d)
        db.session.commit()
        
        if d.day == 1:
            partitionKPI(db, d.year, d.month)
      
        for o in outlets:
            log.debug('Outlet: %s Date: %s', o.name, d.date.isoformat())
            for p in products:
           
                for t in kpis:
                    db.session.execute('''INSERT INTO KPI (id, product_id, store_id, type, kpi, date, calendar_id ) VALUES (:id, :product_id, :store_id, :type, :kpi, :date, :calendar_id)''', 
                    { 'id' : kpi_count, 'product_id' :p.id, 'store_id' : o.id, 'type': t.id, 'date': d.date, 'kpi': float(random.randint(0, 100)), 'calendar_id': d.id })
                    # k = KPI ()
                    # kpi.id = kpi_count
                    # k.product_id = p.id
                    # k.store_id = o.id 
                    # k.type = t.id
                    # k.kpi = float(random.randint(0, 100))
                    # k.date = d.date
                    # db.session.add(k)
                    time.sleep(0.01) # so we don't kill the server
                    kpi_count += 1
           db.session.commit() 
        db.session.commit() 

        curr += datetime.timedelta(days = 1)


# def addKPI(db, curr, outlets, products, kpis, kpi_count):
    # _ = kpi_count
    # log.debug("Adding KPI Data for %s across %s outlets with %s products", curr.isoformat(" "), len(outlets), len(products))
    # d = Calendar()
    # d.date = curr
    # db.session.add(d)
    # db.session.commit()
    
    # if d.day == 1:
        # partitionKPI(db, d.year, d.month)

    # db.session.commit()
    
    # for o in outlets:
        # for p in products:
            # for t in kpis:
                # db.session.execute('''INSERT INTO KPI (id, product_id, store_id, type, kpi, date) VALUES (:id, :product_id, :store_id, :type, :kpi, :date)''', 
                # { 'id' : _, 'product_id' :p.id, 'store_id' : o.id, 'type': t.id, 'date': d.date, 'kpi': float(random.randint(0, 100)) })
                # # k = KPI ()
                # # kpi.id = kpi_count
                # # k.product_id = p.id
                # # k.store_id = o.id 
                # # k.type = t.id
                # # k.kpi = float(random.randint(0, 100))
                # # k.date = d.date
                # # db.session.add(k)
               
                # _ += 1
                # db.session.commit()
    # # db.session.commit() 
    # db.session.commit()
    # curr += datetime.timedelta(days = 1)
        
    # return _
    
def timeit(func, *args):
    start = time.time()
    func(*args)
    end = time.time()
    
    return end - start
    
if __name__ == '__main__':

    params = { 
    "product_types" : 3, "products_per_type" : 30, 
    "region_count" : 30, "cluster_per_region" : 10, "store_per_cluster": 25,
    }
    
    log.debug("Starting ......")
    log.debug("Dropping all tables")
    db.drop_all()
    log.debug("Creating all tables")
    db.create_all()
  
    t = timeit(initProducts, db, params['product_types'], params['products_per_type']) 
    log.debug("Time taken: %0.2f seconds", t)

    t = timeit(initBoundariesStores,db, params['region_count'], params['cluster_per_region'], params['store_per_cluster'])
    log.debug("Time taken: %0.2f seconds", t)

    t = timeit(initTimeframe, db)
    log.debug("Time taken: %0.2f seconds", t)
    
    t = timeit(initWeek,db, 2011)
    log.debug("Time taken: %0.2f seconds", t)

    t = timeit(initWeek,db, 2012)
    log.debug("Time taken: %0.2f seconds", t)
    
    start_date = datetime.datetime(day = 1, month = 1, year = 2011)
    end_date = datetime.datetime(day=31, month=12, year=2012)

    initPartitionKPI(db, 2010, 2)
    
    t = timeit(initKPI, db, start_date, end_date)
    log.debug("Time taken: %0.2f seconds", t)
