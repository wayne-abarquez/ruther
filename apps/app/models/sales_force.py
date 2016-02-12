from sqlalchemy import Table, Column, Integer, ForeignKey, String, Date, Float
from sqlalchemy.orm import relationship, backref
from app import db

class SalesForceRoles (db.Model):
    __tablename__ = 'ruther_sales_force_roles'
    
    id = Column(Integer, primary_key = True)
    extref_id = Column(String)
    name = Column(String)
    
class SalesForce(db.Model):
    __tablename__ = 'ruther_sales_force'
    
    id = Column(Integer, primary_key = True)
    extref_id = Column(String)
    name = Column(String)
    sf_role_id = Column (Integer)
    
class SalesForceKPIType ( db.Model ):
    __tablename__ = 'ruther_sales_force_kpi_type'
    id = Column ( Integer, primary_key = True )
    name = Column ( String )
    
class SalesForceFacilityKPIDaily (db.Model):
    __tablename__ = 'ruther_sales_force_facility_kpi_daily'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
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

    
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )
    
class SalesForceBoundaryKPIDaily (db.Model):
    __tablename__ = 'ruther_sales_force_boundary_kpi_daily'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    facility_type_id = Column ( Integer )
    
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

    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )

class SalesForceFacilityKPIWeekly (db.Model):
    __tablename__ = 'ruther_sales_force_facility_kpi_weekly'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary and Facility information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )
    
class SalesForceBoundaryKPIWeekly (db.Model):
    __tablename__ = 'ruther_sales_force_boundary_kpi_weekly'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    facility_type_id = Column ( Integer )
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)

    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )

class SalesForceFacilityKPIMonth (db.Model):
    __tablename__ = 'ruther_sales_force_facility_kpi_month'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    date_month = Column(Integer)
    date_year = Column(Integer)
    
    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )
    
class SalesForceBoundaryKPIMonth (db.Model):
    __tablename__ = 'ruther_sales_force_boundary_kpi_month'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    facility_type_id = Column ( Integer )
    
    date_month = Column(Integer)
    date_year = Column(Integer)
    
    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )

class SalesForceFacilityKPIYear (db.Model):
    __tablename__ = 'ruther_sales_force_facility_kpi_year'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    facility_id = Column( Integer ) #ForeignKey('facility.id'))
    facility_type_id = Column ( Integer )
    facility_boundary_id = Column( Integer )
    facility_boundary_level_id = Column ( Integer )
    facility_boundary_parent_id = Column ( Integer )
    
    date_year = Column(Integer)
    
    data_point_count = Column ( Integer )
    kpi_type = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )
    
class SalesForceBoundaryKPIYear (db.Model):
    __tablename__ = 'ruther_sales_force_boundary_kpi_year'
    
    id = Column ( Integer, primary_key = True )
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    facility_type_id = Column ( Integer )
    date_year = Column(Integer)
    
    kpi_type = Column ( Integer )
    
    data_point_count = Column ( Integer )
    actual = Column ( Float )
    target = Column ( Float )
    kpi = Column ( Float )
    
    sales_force_id = Column ( Integer )
    sales_force_role_id = Column ( Integer )
    