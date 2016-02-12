from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db

   

class AggregationTableStatus ( db.Model ):
    __tablename__ = "aggregation_status"
    id = Column(Integer, primary_key = True)
    last_aggregation = Column (DateTime)
    table_name = Column(String)

class AggregateFunctionType:
    SUM = 0
    AVERAGE = 1

# maybe useful to optimize aggregation so we don't have to create two aggregation for same type.
class AggregationFunctionMap (db.Model):
    __tablename__ = "aggregation_function_map"
    id = Column ( Integer, primary_key = True )
    kpi_type = Column(Integer)
    function_type = Column(Integer)
    