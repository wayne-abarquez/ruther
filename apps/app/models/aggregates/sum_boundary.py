from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db

  

    
# Boundaries Aggregation
class SumBoundaryDay (db.Model):
    __tablename__ = 'sum_boundary_day'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    facility_type_id = Column ( Integer )
    
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    actual = Column(Float)
    data_point_count = Column(Integer)

    # Date information for the date flatenned
    calendar_id = Column( Integer ) #ForeignKey('calendar.id')) 
    raw_date = Column ( Date ) 
    day_of_week = Column( Integer ) #ForeignKey('timeframe_dayofweek.id') )
    date_day = Column( Integer )
    date_month = Column( Integer )
    date_year = Column( Integer )
    date_quarter = Column( Integer )
    date_start_of_week = Column( Date )
    date_end_of_week = Column( Date )

class SumBoundaryMonth ( db.Model ):
    __tablename__ = 'sum_boundary_month'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    facility_type_id = Column ( Integer )
    
    kpi = Column (Float)
    actual = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
        
    # Date information for the date flatenned
    date_month = Column(Integer)
    date_year = Column(Integer)
    # date_quarter = Column(Integer)

class SumBoundaryYear ( db.Model ):
    __tablename__ = 'sum_boundary_year'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    facility_type_id = Column ( Integer )
    actual = Column(Float)    
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)

    # Date information for the date flatenned
    date_year = Column(Integer)
    # date_quarter = Column(Integer)
    

    
class SumBoundaryWeek ( db.Model ):
    __tablename__ = 'sum_boundary_week'
    id = Column(Integer, primary_key = True)

    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )

    facility_type_id = Column ( Integer )
    actual = Column(Float)    
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
        
    # Date information for the date flatenned
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)