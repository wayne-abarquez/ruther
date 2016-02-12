from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db

class OutletType(db.Model):
    __tablename__ = 'outlettypes'
    id = Column(Integer, primary_key = True)
    maintype = Column(String)   # [premium, star, smile, smartfren gadget outlet, regular]

class FacilityOutletTypeMapping(db.Model):
    __tablename__ = 'facility_outlettype_mapping'
    id = Column(Integer, primary_key = True)
    facility_id = Column(ForeignKey('facilities.id'), index=True)
    outlettype_id = Column(ForeignKey('outlettypes.id'), index=True)

    # creates a bidirectional relationship
    outlettype = relation(OutletType)

# To create manually
#create table outlettypes(
#    id                   serial primary key,
#    maintype        varchar,
#    subtype          varchar
#);
#
#create table facility_outlettype_mapping(
#    id                  serial primary key,
#    facility_id       int references facilities(id),
#    outlettype_id  int references outlettypes(id),
#    date               date
#);
#
#create index FOM_facility_id on facility_outlettype_mapping(facility_id);
#create index FOM_outlettype_id on facility_outlettype_mapping(outlettype_id);
#create index FOM_date on facility_outlettype_mapping(date);
