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

def delete_aggregation_boundary_month_table():
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductMonth.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumFacilityProductGroupMonth.__tablename__ } )    
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductGroupMonth.__tablename__ } )
    db.session.execute('DELETE FROM %(tablename)s' % { 'tablename' : SumBoundaryProductMonth.__tablename__ } )    
    db.session.commit()

def sum_aggregate_stores():
    log.info('Sum Aggregation of store monthly')
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM KPI'):
        timeframe.append((ret[0], ret[1]))

    for ret in timeframe:
        month, year = ret[0], ret[1]
        log.debug('[%s] Doing month: %s, year %s', SumFacilityProductMonth.__tablename__, month, year)
        db.session.execute('SELECT aggregate_facility_product_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
   
    for ret in timeframe:
        month, year = ret[0], ret[1]
        log.debug('[%s] Doing month: %s, year %s', SumFacilityProductGroupMonth.__tablename__, month, year)
        db.session.execute('SELECT aggregate_facility_productgroup_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

def sum_aggregate_stores_to_boundary():
    timeframe = []
    for ret in db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM KPI'):
        timeframe.append((ret[0], ret[1]))
        
    for ret in db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM KPI'):
        month, year = ret[0], ret[1]
        log.debug('[%s] Doing month: %s, year %s', SumBoundaryProductMonth.__tablename__, month, year)
        db.session.execute('SELECT aggregate_boundary_product_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()      
    
    for ret in db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM KPI'):
        month, year = ret[0], ret[1]
        log.debug('[%s] Doing month: %s, year %s', SumBoundaryProductGroupMonth.__tablename__, month, year)
        db.session.execute('SELECT aggregate_boundary_productgroup_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()      
          
if __name__ == '__main__':
    # get the bottom level aggregation

    log.info('Deleting aggregating boundaries')
    timeit(delete_aggregation_boundary_month_table)
    
    # we have to do all for the sum ( help us on average aggregation too) 
    timeit(sum_aggregate_stores)
    timeit(sum_aggregate_stores_to_boundary)

    