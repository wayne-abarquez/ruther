import os, sys, time, logging
sys.path.append('../')

from sqlalchemy import *
from sqlalchemy.orm import *

from app import db
from app.models import *

log = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))    
stdout_handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(stdout_handler)

def timeit(func, *args):
    start = time.time()
    ret = func(*args)
    end = time.time()
    
    log.info('Time taken %0.2f seconds\n', end - start)
    return ret

def delete_aggregation_boundary_week_table():
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductWeek.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductWeek.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductGroupWeek.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductGroupWeek.__tablename__ } )
    db.session.commit()

def sum_aggregate_stores():
    log.info('Sum Aggregation of store weekly')
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON ( date_month, date_year)  date_month, date_year FROM KPI'):
        timeframe.append((ret[0], ret[1]))
        
    for ret in timeframe:
        month, year = ret[0], ret[1]
        log.debug('Doing year: %s',  year)
        db.session.execute('SELECT aggregate_facility_product_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
    
    for ret in timeframe:
        month, year = ret[0], ret[1]
        db.session.execute('SELECT aggregate_facility_productgroup_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year }  )
        db.session.commit()

def sum_aggregate_stores_to_boundary():
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON ( date_month, date_year)  date_month, date_year FROM KPI'):
        timeframe.append((ret[0], ret[1]))
        
    for ret in timeframe:
        month, year = ret[0], ret[1]
        log.debug('Doing year: %s', year)
        db.session.execute('SELECT aggregate_boundary_product_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()         
    
    for ret in timeframe:
        month, year = ret[0], ret[1]
        log.debug('[%s] Doing month: %s, year %s', SumBoundaryProductGroupWeek.__tablename__, month, year)
        db.session.execute('SELECT aggregate_boundary_productgroup_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
          
if __name__ == '__main__':
    # get the bottom level aggregation

    log.info('Deleting aggregating boundaries')
    timeit(delete_aggregation_boundary_week_table)
    
    # we have to do all for the sum ( help us on average aggregation too) 
    timeit(sum_aggregate_stores_to_boundary)
    timeit(sum_aggregate_stores)

    