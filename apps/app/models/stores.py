from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db
from boundary import *
from aggregates.base import AggregateFunctionType, AggregationFunctionMap
from aggregates.sum_aggregates import SumAggregationStoreMonth,  SumAggregationBoundaryWeek, SumAggregationBoundaryYear, SumAggregationBoundaryDay
from kpi import KPI
class Store(db.Model):
    __tablename__ = 'store'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    geom = GeometryColumn(Point(2), nullable=True)
    boundary_id = Column( Integer, ForeignKey('boundaries.id') )
    # boundary = relationship ( 'Boundary' )
    @property
    def boundary(self):
        if not hasattr(self, '_boundary'):
            self._boundary = Boundary.query.filter_by(id = self.boundary_id)[0]
        return self._boundary
    
    def kpi(self, products, timeframe):
        if timeframe['type'] == 'year':
            t = SumAggregationStoreYear
            q = t.query.filter_by(store_id = self.id, date_year = timeframe['date_year'])

        if timeframe['type'] == 'month':
            t = SumAggregationStoreMonth
            q = t.query.filter_by(store_id = self.id, date_year = timeframe['date_year'], date_month = timeframe['date_month'])

        if timeframe['type'] == 'week':
            t = SumAggregationStoreWeek
            q = t.query.filter_by(store_id = self.id, date_start_of_week = timeframe['date_start_week'])
        
        if timeframe['type'] == 'day':
            t = KPI
            q = t.query.filter_by(store_id = self.id, date_day = timeframe['date_day'], date_year = timeframe['date_year'], date_month = timeframe['date_month'])
                    
        func_map_q = KPIType.query.outerjoin(AggregationFunctionMap, KPIType.id == AggregationFunctionMap.kpi_type).add_entity(AggregationFunctionMap)
        
        app.logger.debug(products)
        if products.get('type','') == 'product':
            app.logger.debug(int(products.get('id','')))
            q = q.filter_by(product_id = int(products.get('id','')))
        else:
            q = q.outerjoin(ProductGroupMap, ProductGroupMap.product_id == t.product_id and ProductGroupMap.group_id == int(products.get('id','')))
        
        ret = {}
        count = q.count()
        for kpi_type, func_map in func_map_q:
            value, data_points, normalized_value = 0, 0, 0
            found = False
            if timeframe['type'] == 'day':
                for i in q.filter(t.type == kpi_type.id):
                    found = True
                    value += i.kpi
                    data_points += 1
                    app.logger.debug('%s %s %s', i.product_id, i.type, i.raw_date)
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
        
GeometryDDL(Store.__table__)

class StoreSchema(db.Model):
    __tablename__ = 'store_schema'
    id = Column(Integer, primary_key = True)
    column_name = Column(String)
    data_type = Column(Integer)

class StoreColumnSchema_DataType:
    Integer = 0
    String = 1
    Double = 2
    
class StoreCustomData(db.Model):
    __tablename__  = 'store_custom_data'
    id = Column(Integer, primary_key = True)
    schema_id = Column(Integer, ForeignKey('store_schema.id'))
    store_id = Column(Integer, ForeignKey('store.id'))
    data = Column(String)

    # creates a bidirectional relationship
    # from StoreCustomData to Store it's Many-to-One
    # from Store to StoreCustomData it's One-to-Many
    store = relation(Store, backref=backref('StoreCustomData', order_by=id))

    # creates a bidirectional relationship
    # from StoreSchema to StoreCustomData it's Many-to-One
    # from StoreCustomData to StoreSchema it's One-to-Many
    schema = relation(StoreSchema, backref=backref('StoreCustomData', order_by=id))
