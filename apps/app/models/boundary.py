import datetime, calendar
from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db, app
from kpi import KPIType
from aggregates.base import AggregateFunctionType, AggregationFunctionMap
from aggregates.sum_boundary_productgroup import SumBoundaryProductGroupYear, SumBoundaryProductGroupDay, SumBoundaryProductGroupWeek, SumBoundaryProductGroupMonth
from aggregates.sum_boundary_product import SumBoundaryProductYear, SumBoundaryProductDay, SumBoundaryProductWeek, SumBoundaryProductMonth
# from aggregates.sum_aggregates import SumAggregationBoundaryMonth, SumAggregationBoundaryWeek, SumAggregationBoundaryYear, SumAggregationBoundaryDay
import config
from products import ProductGroupMap
BOUNDARY_LEVELS_DESC = {
    1: 'Region',
    2: 'Cluster',
    3: 'Stores',
}

class BoundaryLevelDesc(db.Model):
    __tablename__ = 'boundary_level_desc'
    id = Column(Integer, primary_key = True)
    description = Column(String)

class Boundary(db.Model):
    __tablename__ = 'boundaries'
    id = Column(Integer, primary_key = True)
    extref_id = Column ( Integer )
    name = Column(String)
    level_id = Column(Integer, ForeignKey('boundary_level_desc.id'))
    parent_id = Column(Integer, ForeignKey('boundaries.id'), nullable=True)    # self-referencing id of BoundaryLevels table. Need to create triggers to ensure integrity of this value
    
    # creates a bidirectional relationship
    # from Boundary to BoundaryLevelDesc it's Many-to-One
    # from BoundaryLevelDesc to Boundary it's One-to-Many
    level = relation(BoundaryLevelDesc, backref=backref('Boundary', order_by=id))
	
    def kpi(self, products, timeframe, kpi_type = None):
        days = 0
        if kpi_type:
            func_map_q = KPIType.query.outerjoin(AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type).filter(KPIType.id == kpi_type).add_entity(AggregationFunctionMap)
        else:
            func_map_q = KPIType.query.outerjoin(AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type).filter(KPIType.facility_type_id == config.STORE_TYPE_ID).add_entity(AggregationFunctionMap)
        
        if products['type'] == 'product':
            product_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumBoundaryProductYear
                q = t.query.filter_by(boundary_id = self.id, product_id = product_id, date_year = timeframe['date_year'])
                days = 366 if calendar.isleap(timeframe['date_year']) else 365

            if timeframe['type'] == 'month':
                t = SumBoundaryProductMonth
                q = t.query.filter_by(boundary_id = self.id, product_id = product_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
                
            if timeframe['type'] == 'week':
                t = SumBoundaryProductWeek
                q = t.query.filter_by(boundary_id = self.id, product_id = product_id, date_start_of_week = datetime.date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']))
                days = 7

            if timeframe['type'] == 'day':
                t = SumBoundaryProductDay
                q = t.query.filter_by(boundary_id = self.id, product_id = product_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days = 1

        else:
            product_group_id = int(products['id'])
            if timeframe['type'] == 'year':
                t = SumBoundaryProductGroupYear
                q = t.query.filter_by(boundary_id = self.id, product_group_id = product_group_id, date_year = timeframe['date_year'])
                days = 366 if calendar.isleap(timeframe['date_year']) else 365

            if timeframe['type'] == 'month':
                t = SumBoundaryProductGroupMonth
                q = t.query.filter_by(boundary_id = self.id, product_group_id = product_group_id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days =  calendar.monthrange(timeframe['date_year'], timeframe['date_month'])[1]
                
            if timeframe['type'] == 'week':
                t = SumBoundaryProductGroupWeek
                q = t.query.filter_by(boundary_id = self.id, product_group_id = product_group_id, date_start_of_week = datetime.date(timeframe['date_year'], timeframe['date_month'], timeframe['date_day']))
                days = 7

            if timeframe['type'] == 'day':
                t = SumBoundaryProductGroupDay
                q = t.query.filter_by(boundary_id = self.id, product_group_id = product_group_id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                days = 1            
        
        # if products['type'] == 'product':
            # q = q.filter_by(product_id = int(products['id']))
        # else:
            # q = q.outerjoin(ProductGroupMap, ProductGroupMap.product_id == t.product_id and ProductGroupMap.group_id == int(products['id']))
        
        ret = {}
        count = q.count()

        for kpi_type, func_map in func_map_q:
            value, data_points, normalized_value = 0, 0, 0
            found = False

            for i in q.filter(t.kpi_type == kpi_type.id):
                found = True
                value += i.kpi
                data_points += i.data_point_count

            if func_map.function_type == AggregateFunctionType.AVERAGE:
                
                value = value / ( data_points if data_points else 1 )
            
            if func_map.function_type == AggregateFunctionType.AVERAGE:
                normalized_value = value
            else:
                normalized_value = value / ( data_points if data_points else 1 )
            ret[kpi_type.id] = [ kpi_type.id, kpi_type.name, value, normalized_value ]


        ret['count'] = count
        return ret
 
class BoundaryPolygons(db.Model):
    __tablename__ = 'boundary_polygons'
    id = Column(Integer, primary_key = True)
    boundary_id = Column(Integer, ForeignKey('boundaries.id'))
    geom = GeometryColumn(Polygon(2), nullable=True)
    encoded_poly = Column(String)
    encoded_levels = Column(String)
    
    # creates a bidirectional relationship
    # from BoundaryPolygons to Boundary it's Many-to-One
    # from Boundary to BoundaryPolygons it's One-to-Many
    boundary = relation(Boundary, backref=backref('BoundaryPolygons', order_by=id))

GeometryDDL(BoundaryPolygons.__table__)
