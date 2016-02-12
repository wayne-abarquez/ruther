from app import db
from app.models import *

import os, sys, logging, datetime, time, random


log = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))    
stdout_handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(stdout_handler)


# class AggregationStoreMonth ( db.Model ):
    # __tablename__ = "aggregation_store_month"
    # id = Column(Integer, primary_key = True)
    # month_id = Column(ForeignKey('timeframe_month.id'))
    # year = Column(Integer)
    # kpi = Column(Float)
    # kpi_type = Column(Integer)
    # store_id = Column(Integer)
    # product_id = Column(Integer)
    
    
def aggregate_store_month(db):
    result = db.session.execute("SELECT ")
    return result
if __name__ == '__main__':
    for i in aggregate_store_month(db):
        print i