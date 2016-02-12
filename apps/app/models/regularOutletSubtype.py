from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db

class RegularOutletSubtype(db.Model):
    __tablename__ = 'regular_outlet_subtypes'
    id = Column(Integer, primary_key = True)
    subtype = Column(String)   # [super platinum, platinum, gold, silver]

class BoundaryProductDailySubtype(db.Model):
    __tablename__ = 'boundary_product_daily_subtype'
    id = Column(Integer, primary_key = True)

    boundary_id = Column(Integer, ForeignKey('boundaries.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    regular_outlet_subtype_id = Column(ForeignKey('regular_outlet_subtypes.id'), index=True)
    date = Column(Date, index=True)

    outletCount = Column(Integer)
    activation = Column(Integer)

class BoundaryProductWeeklySubtype(db.Model):
    __tablename__ = 'boundary_product_weekly_subtype'
    id = Column(Integer, primary_key = True)

    boundary_id = Column(Integer, ForeignKey('boundaries.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    regular_outlet_subtype_id = Column(ForeignKey('regular_outlet_subtypes.id'), index=True)
    start_week_date = Column(Date, index=True)
    end_week_date = Column(Date, index=True)

    outletCount = Column(Integer)
    activation = Column(Integer)

class BoundaryProductMonthlySubtype(db.Model):
    __tablename__ = 'boundary_product_monthly_subtype'
    id = Column(Integer, primary_key = True)

    boundary_id = Column(Integer, ForeignKey('boundaries.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    regular_outlet_subtype_id = Column(ForeignKey('regular_outlet_subtypes.id'), index=True)
    month = Column(Integer)
    year = Column(Integer)

    outletCount = Column(Integer)
    activation = Column(Integer)

class BoundaryProductYearlySubtype(db.Model):
    __tablename__ = 'boundary_product_yearly_subtype'
    id = Column(Integer, primary_key = True)

    boundary_id = Column(Integer, ForeignKey('boundaries.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    regular_outlet_subtype_id = Column(ForeignKey('regular_outlet_subtypes.id'), index=True)
    year = Column(Integer)

    outletCount = Column(Integer)
    activation = Column(Integer)
