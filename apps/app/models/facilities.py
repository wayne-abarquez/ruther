from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db
from boundary import *
from aggregates.base import AggregateFunctionType, AggregationFunctionMap
from aggregates.sum_facility_productgroup import SumFacilityProductGroupYear, SumFacilityProductGroupMonth, SumFacilityProductGroupWeek, SumFacilityProductGroupDay
from aggregates.sum_facility_product import SumFacilityProductYear, SumFacilityProductMonth, SumFacilityProductWeek
# from aggregates.sum_aggregates import SumAggregationFacilityMonth,  SumAggregationBoundaryWeek, SumAggregationBoundaryYear, SumAggregationBoundaryDay
from kpi import KPI

class FacilityType (db.Model):
    __tablename__ = 'facility_types'
    id = Column(Integer, primary_key = True)
    extref_id = Column( Integer )
    name = Column(String)

# class FacilitySubType (db.Model):
    # __tablename__ = 'facility_types'
    # id = Column(Integer, primary_key = True)
    # extref_id = Column( Integer )
    # name = Column(String)

# class FacilityTag (db.Model):
    # __tablename__ = 'ruther_facility_tags'
    
    # name = Column (String)
    
class FacilityTagMapping (db.Model):
    __tablename__ = 'ruther_facility_tag_mapping'
    id = Column(Integer, primary_key = True)
    facility_id = Column ( Integer )
    facility_tag_name = Column( String )

class Facility(db.Model):
    __tablename__ = 'facilities'
    id = Column(Integer, primary_key = True)
    extref_id = Column( String )
    name = Column(String)
    facility_type_id = Column(Integer, ForeignKey('facility_types.id'))
    geom = GeometryColumn(Point(2), nullable=True)
    boundary_id = Column( Integer, ForeignKey('boundaries.id') )

    @property
    def boundary(self):
        if not hasattr(self, '_boundary'):
            self._boundary = Boundary.query.filter_by(id = self.boundary_id)[0]
        return self._boundary
    
    def kpi(self, products, timeframe):
        if products.get('type','') == 'product':
            product_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumFacilityProductYear
                q = t.query.filter_by(facility_id = self.id, product_id = product_id, date_year = timeframe['date_year'])

            if timeframe['type'] == 'month':
                t = SumFacilityProductMonth
                q = t.query.filter_by(facility_id = self.id, product_id = product_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])

            if timeframe['type'] == 'week':
                t = SumFacilityProductWeek
                q = t.query.filter_by(facility_id = self.id, product_id = product_id, date_start_of_week = timeframe['date_start_week'])
            
            if timeframe['type'] == 'day':
                t = KPI
                q = t.query.filter_by(facility_id = self.id,  product_id = product_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
        else:
            product_group_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumFacilityProductGroupYear
                q = t.query.filter_by(facility_id = self.id, product_group_id = product_group_id, date_year = timeframe['date_year'])

            if timeframe['type'] == 'month':
                t = SumFacilityProductGroupMonth
                q = t.query.filter_by(facility_id = self.id, product_group_id = product_group_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])

            if timeframe['type'] == 'week':
                t = SumFacilityProductGroupWeek
                q = t.query.filter_by(facility_id = self.id, product_group_id = product_group_id, date_start_of_week = timeframe['date_start_week'])
            
            if timeframe['type'] == 'day':
                t = SumFacilityProductGroupDay
                q = t.query.filter_by(facility_id = self.id, product_group_id = product_group_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                
        func_map_q = KPIType.query.outerjoin(AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type).filter(KPIType.facility_type_id == self.facility_type_id).add_entity(AggregationFunctionMap)

        ret = {}
        count = q.count()
        for kpi_type, func_map in func_map_q:
            value, data_points, normalized_value = 0, 0, 0
            found = False
            if timeframe['type'] == 'day':
                for i in q.filter(t.kpi_type == kpi_type.id):
                    found = True
                    value += i.kpi
                    data_points += 1

            else:
                for i in q.filter(t.kpi_type == kpi_type.id):
                    found = True
                    value += i.kpi
                    data_points += i.data_point_count
            
            if func_map.function_type == AggregateFunctionType.AVERAGE:
                value = value / ( data_points if data_points else 1 )
            normalized_value = value / ( data_points if data_points else 1 ) 
            ret[kpi_type.id] = [kpi_type.id, kpi_type.name, value, normalized_value ]
        ret['count'] = count
        
        return ret
        
GeometryDDL(Facility.__table__)
    
class FacilitySchema(db.Model):
    __tablename__ = 'facility_schema'
    id = Column(Integer, primary_key = True)
    column_name = Column(String)
    data_type = Column(Integer)

class FacilityColumnSchema_DataType:
    Integer = 0
    String = 1
    Double = 2
    
class FacilityCustomData(db.Model):
    __tablename__  = 'facility_custom_data'
    id = Column(Integer, primary_key = True)
    schema_id = Column(Integer, ForeignKey('facility_schema.id'))
    facility_id = Column(Integer, ForeignKey('facilities.id'))
    data = Column(String)

    # creates a bidirectional relationship
    # from FacilityCustomData to Facility it's Many-to-One
    # from Facility to FacilityCustomData it's One-to-Many
    facility = relation(Facility, backref=backref('FacilityCustomData', order_by=id))

    # creates a bidirectional relationship
    # from FacilitySchema to FacilityCustomData it's Many-to-One
    # from FacilityCustomData to FacilitySchema it's One-to-Many
    schema = relation(FacilitySchema, backref=backref('FacilityCustomData', order_by=id))
