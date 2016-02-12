from sqlalchemy import Table, Column, Integer, ForeignKey, String, Date, Float
from sqlalchemy.orm import relationship, backref
from app import db
from timeframe import Calendar

class AggregateFunctionType:
    SUM = 0
    AVERAGE = 1
    
class KPIType (db.Model):
    __tablename__ = 'kpi_type'
    id = Column( Integer, primary_key = True )
    facility_type_id = Column( ForeignKey('facility_types.id') )
    name = Column(String)
    # aggregation_function_type = Column( Integer )
    
# Denormalized to make queries simple and straightforward.
# UI and Web App logic implementation has to be strict to ensure integrity of data.
class KPI ( db.Model ):
    __tablename__ = 'kpi'
    id = Column(Integer, primary_key = True)
    
    # Boundary and Store information flatenned
    facility_id = Column( ForeignKey('facilities.id'))
    facility_type_id = Column( ForeignKey('facility_types.id') )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer, nullable=True )

    #KPI
    kpi = Column ( Float )
    kpi_type = Column( ForeignKey('kpi_type.id'))
    actual = Column (Float)
    target = Column (Float)
    
    # product information for this KPI Flattened
    product_id = Column( ForeignKey('products.id'))
 
    # Date information for the date flatenned
    calendar_id = Column( ForeignKey('calendar.id')) 
    raw_date = Column ( Date ) 
    day_of_week = Column( ForeignKey('timeframe_dayofweek.id') )
    date_day = Column(Integer)
    date_month = Column(Integer)
    date_year = Column(Integer)
    date_quarter = Column(Integer)
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

    
    @property
    def date(self):
        return self.raw_date

    @date.setter
    def date(self, d):
        calendar = Calendar.query.filter_by(raw_date = d)[0]
        self.raw_date = d
        self.date_day = calendar.day
        self.date_month = calendar.month
        self.date_day_of_week = calendar.day_of_week
        self.date_year = calendar.year
        self.date_quarter = calendar.quarter 
        self.date_start_of_week = calendar.start_of_week 
        self.date_end_of_week = calendar.end_of_weel

class FacilityKPI (db.Model):
    __tablename__ = 'ruther_facility_kpi'
    id = Column(Integer, primary_key = True)
    
    # Boundary and Store information flatenned
    facility_id = Column( ForeignKey('facilities.id'))
    facility_type_id = Column( ForeignKey('facility_types.id') )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer, nullable=True )

    #KPI
    kpi = Column ( Float )
    kpi_type = Column( ForeignKey('kpi_type.id'))
    actual = Column (Float)
    
    # Date information for the date flatenned
    calendar_id = Column( ForeignKey('calendar.id')) 
    raw_date = Column ( Date ) 
    day_of_week = Column( ForeignKey('timeframe_dayofweek.id') )
    date_day = Column(Integer)
    date_month = Column(Integer)
    date_year = Column(Integer)
    date_quarter = Column(Integer)
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

    
    @property
    def date(self):
        return self.raw_date

    @date.setter
    def date(self, d):
        calendar = Calendar.query.filter_by(raw_date = d)[0]
        self.raw_date = d
        self.date_day = calendar.day
        self.date_month = calendar.month
        self.date_day_of_week = calendar.day_of_week
        self.date_year = calendar.year
        self.date_quarter = calendar.quarter 
        self.date_start_of_week = calendar.start_of_week 
        self.date_end_of_week = calendar.end_of_weel
