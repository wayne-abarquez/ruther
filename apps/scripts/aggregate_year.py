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

def delete_aggregation_boundary_year_table():
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductYear.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductGroupYear.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductYear.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductGroupYear.__tablename__ } )
    db.session.commit()

def sum_aggregate_stores():
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON ( date_year) date_year FROM KPI'):
        timeframe.append(ret[0])
        
    log.info('Sum Aggregation of store yearly')
    for ret in timeframe:
        year = ret
        log.debug('[%s] Doing year %s', SumFacilityProductYear.__tablename__, year)
        db.session.execute('SELECT aggregate_facility_product_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()

    for ret in timeframe:
        year = ret
        log.debug('[%s] Doing year %s', SumFacilityProductGroupYear.__tablename__, year)
        db.session.execute('SELECT aggregate_facility_productgroup_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()
 
def sum_aggregate_stores_to_boundary():
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON ( date_year) date_year FROM KPI'):
        timeframe.append(ret[0])
        
    for ret in timeframe:
        year = ret
        log.debug('[%s] Doing year %s', SumBoundaryProductYear.__tablename__, year)
        db.session.execute('SELECT aggregate_boundary_product_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()         

    for ret in timeframe:
        year = ret
        log.debug('[%s] Doing year %s', SumBoundaryProductGroupYear.__tablename__, year)
        db.session.execute('SELECT aggregate_boundary_productgroup_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()         
if __name__ == '__main__':
    # get the bottom level aggregation

    log.info('Deleting aggregating boundaries')
    timeit(delete_aggregation_boundary_year_table)
    
    # we have to do all for the sum ( help us on average aggregation too) 
    timeit(sum_aggregate_stores)
    timeit(sum_aggregate_stores_to_boundary)
