from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Float, Date
from sqlalchemy.orm import relationship, backref
from app import db


class SmartfrenOutletProductClassificationType ( db.Model ):
    __tablename__ = 'smartfren_outlet_product_classification_type'
    
    type_name = Column ( String, primary_key = True )

    
# Boundaries Aggregation
class SmartfrenOutletProductClassificationDay (db.Model):
    __tablename__ = 'smartfren_outlet_product_classification_day'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    outlet_subtype_classification = Column ( String )
    
    outlet_count = Column ( Integer )
    total_activation = Column ( Float )

    # product information for this KPI Flattened
    product_id = Column( Integer ) #ForeignKey('products.id'))

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

class SmartfrenOutletProductClassificationMonth ( db.Model ):
    __tablename__ = 'smartfren_outlet_product_classification_month'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
       
    outlet_subtype_classification = Column ( String )   
       
    outlet_count = Column ( Integer )
    total_activation = Column ( Float )

    # product information for this KPI Flattened
    product_id = Column( Integer ) #ForeignKey('products.id'))
        
    # Date information for the date flatenned
    date_month = Column(Integer)
    date_year = Column(Integer)
    # date_quarter = Column(Integer)

class SmartfrenOutletProductClassificationYear ( db.Model ):
    __tablename__ = 'smartfren_outlet_product_classification_year'
    id = Column(Integer, primary_key = True)
    
    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )
    
    outlet_subtype_classification = Column ( String )
    
    outlet_count = Column ( Integer )
    total_activation = Column ( Float )

    # product information for this KPI Flattened
    product_id = Column( Integer ) #ForeignKey('products.id'))
        
    # Date information for the date flatenned
    date_year = Column(Integer)
    # date_quarter = Column(Integer)
    

    
class SmartfrenOutletProductClassificationWeek ( db.Model ):
    __tablename__ = 'smartfren_outlet_product_classification_week'
    id = Column(Integer, primary_key = True)

    # Boundary information flatenned
    boundary_id = Column( Integer )
    boundary_level_id = Column ( Integer )
    boundary_parent_id = Column ( Integer )

    outlet_subtype_classification = Column ( String )
    
    outlet_count = Column ( Integer )
    total_activation = Column ( Float )

    # product information for this KPI Flattened
    product_id = Column( Integer )# ForeignKey('products.id'))
        
    # Date information for the date flatenned
    date_start_of_week = Column(Date)
    date_end_of_week = Column(Date)
