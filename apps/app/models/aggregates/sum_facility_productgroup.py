from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db

  

class SumFacilityProductGroupMonth ( db.Model ):
    __tablename__ = "sum_facility_productgroup_month"
    
    id = Column(Integer, primary_key = True)
    
    # products
    product_group_id = Column(Integer)
    product_group_parent_id = Column ( Integer )
    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    # KPI Information
    kpi = Column (Float)
    actual = Column(Float)
    target = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
    
    # Date information for the date flatenned
    date_month = Column( Integer ) #ForeignKey('timeframe_month.id'))
    date_year = Column(Integer)
    date_quarter = Column(Integer)

class SumFacilityProductGroupYear ( db.Model ):
    __tablename__ = 'sum_facility_productgroup_year'
    id = Column(Integer, primary_key = True)
    
    # products
    product_group_id = Column(Integer)
    product_group_parent_id = Column ( Integer )
    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    # KPI Information
    kpi = Column (Float)
    actual = Column(Float)
    target = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)
        
    # Date information for the date flatenned
    date_year = Column(Integer)
    
class SumFacilityProductGroupWeek ( db.Model ):
    __tablename__ = 'sum_facility_productgroup_week'
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
    target = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    function_type = Column ( Integer )  

    # product information for this KPI Flattened
    product_group_id = Column( Integer ) #ForeignKey('products.id'))
    product_group_parent_id = Column ( Integer )
    # Date information for the date flatenned
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

class SumFacilityProductGroupDay ( db.Model ):
    __tablename__ = 'sum_facility_productgroup_day'
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
    target = Column(Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    function_type = Column ( Integer )  

    # product information for this KPI Flattened
    product_group_id = Column( Integer ) #ForeignKey('products.id'))
    product_group_parent_id = Column ( Integer )
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
