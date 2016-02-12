from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db




class SumFacilityMonth ( db.Model ):
    __tablename__ = "sum_facility_month"
    
    id = Column(Integer, primary_key = True)
    
    
    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    # KPI Information
    kpi = Column (Float)
    actual = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
    
    # Date information for the date flatenned
    date_month = Column( Integer ) #ForeignKey('timeframe_month.id'))
    date_year = Column(Integer)
    date_quarter = Column(Integer)

class SumFacilityYear ( db.Model ):
    __tablename__ = 'sum_facility_year'
    id = Column(Integer, primary_key = True)


    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    # KPI Information
    kpi = Column (Float)
    actual = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
        
    # Date information for the date flatenned
    date_year = Column(Integer)
    
class SumFacilityWeek ( db.Model ):
    __tablename__ = 'sum_facility_week'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    data_point_count = Column(Integer)
    
    kpi = Column (Float)
    actual = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
        
    # Date information for the date flatenned
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)
    