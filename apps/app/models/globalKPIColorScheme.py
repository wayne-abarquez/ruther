from sqlalchemy import *
from sqlalchemy.orm import *
from geoalchemy import *
from app import db

class GlobalKPIColorScheme(db.Model):
    __tablename__ = 'global_kpi_color_scheme'
    id = Column(Integer, primary_key = True)
    lowerbound = Column(Integer)
    upperbound = Column(Integer)
    rgb= Column(String)

    @property
    def serialize(self):
        # Return object data in easily serializable format
        return {
            'id': self.id,
            'lowerbound': self.lowerbound,
            'upperbound': self.upperbound,
            'rgb': self.rgb,
        }

    # If you want to create it manually
    #create table global_kpi_color_scheme(
    #    id          serial primary key,
    #    lowerbound  integer NOT NULL,
    #    upperbound  integer NOT NULL,
    #    rgb         varchar
    #)
