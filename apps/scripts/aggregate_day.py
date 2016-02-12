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

MAX_RECORDS_IN_TRANSACTIONS = 10000

def timeit(func, *args):
    start = time.time()
    ret = func(*args)
    end = time.time()
    
    log.info('Time taken %0.2f seconds\n', end - start)
    return ret
    

def delete_aggregation_boundary_day_table():
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductGroupDay.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductGroupDay.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductDay.__tablename__ } )    
    db.session.commit()

def sum_aggregate_stores_to_boundary(direct = False):
    ret = db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM KPI')
    timeframes = []
    for obj in ret:
        timeframes.append([obj[0], obj[1]])
        
        
    for obj in timeframes:
        month, year = obj[0], obj[1]
        log.debug('[%s] Doing month: %s, year %s', SumBoundaryProductDay.__tablename__, month, year)
        db.session.execute('SELECT aggregate_boundary_product_day_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
        
    for obj in timeframes:
        month, year = obj[0], obj[1]
        log.debug('[%s] Doing month: %s, year %s', SumBoundaryProductGroupDay.__tablename__, month, year)
        db.session.execute('SELECT aggregate_boundary_productgroup_day_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
        
    for obj in timeframes:
        month, year = obj[0], obj[1]
        log.debug('[%s] Doing month: %s, year %s', SumFacilityProductGroupDay.__tablename__, month, year)
        db.session.execute('SELECT aggregate_facility_productgroup_day_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

if __name__ == '__main__':
    # get the bottom level aggregation

    log.info('Deleting aggregating boundaries')
    timeit(delete_aggregation_boundary_day_table)
    
    # we have to do all for the sum ( help us on average aggregation too) 
    timeit(sum_aggregate_stores_to_boundary, True)

    
    