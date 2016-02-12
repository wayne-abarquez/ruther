from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db

  

    

    
class SumBoundaryProductGroupDay (db.Model):
    __tablename__ = 'sum_boundary_productgroup_day'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    facility_type_id = Column ( Integer )
    actual = Column(Float)    
    target = Column(Float)
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)

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

class SumBoundaryProductGroupMonth ( db.Model ):
    __tablename__ = 'sum_boundary_productgroup_month'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    facility_type_id = Column ( Integer )
    actual = Column(Float)    
    target = Column(Float)
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)

    # product information for this KPI Flattened
    product_group_id = Column( Integer ) #ForeignKey('products.id'))
    product_group_parent_id = Column ( Integer )
    # Date information for the date flatenned
    date_month = Column(Integer)
    date_year = Column(Integer)
    # date_quarter = Column(Integer)

class SumBoundaryProductGroupYear ( db.Model ):
    __tablename__ = 'sum_boundary_productgroup_year'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )

    facility_type_id = Column ( Integer )

    product_group_id = Column ( Integer )
    product_group_parent_id = Column ( Integer )
    actual = Column(Float)
    target = Column(Float)
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)

    # product information for this KPI Flattened
    product_group_id = Column( Integer ) #ForeignKey('products.id'))
        
    # Date information for the date flatenned
    date_year = Column(Integer)
    # date_quarter = Column(Integer)
    

    
class SumBoundaryProductGroupWeek ( db.Model ):
    __tablename__ = 'sum_boundary_productgroup_week'
    id = Column(Integer, primary_key = True)

    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )

    facility_type_id = Column ( Integer )
    actual = Column(Float)    
    target = Column(Float)
    kpi = Column (Float)
    kpi_type = Column( Integer ) #ForeignKey('kpi_type.id'))
    data_point_count = Column(Integer)

    # product information for this KPI Flattened
    product_group_id = Column( Integer )# ForeignKey('products.id'))
    product_group_parent_id = Column ( Integer )
    # Date information for the date flatenned
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

