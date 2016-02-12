from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Date
from sqlalchemy.orm import relationship, backref
from app import db
import datetime
START_WEEK = 0
END_WEEK = 6

class Week ( db.Model ):
    __tablename__ = 'timeframe_week'
    start_of_week = Column(DateTime, primary_key = True)
    end_of_week = Column(DateTime)
 
    @property
    def end_week( self ):
        return self.start_week + datetime.timedelta(days = 6)
    
class Quarter( db.Model ):
    __tablename__ = 'timeframe_quarter'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    
class DayOfWeek( db.Model ):
    __tablename__ = 'timeframe_dayofweek'
    id = Column(Integer, primary_key = True)
    name = Column(String)

class Month( db.Model ):
    __tablename__ = 'timeframe_month'
    id = Column(Integer, primary_key = True)
    name = Column(String)

class Calendar( db.Model ):
    __tablename__ = 'calendar'
    id = Column (Integer, primary_key = True)
    raw_date = Column(Date)
    day = Column(Integer, nullable = True)
    day_of_week = Column( ForeignKey('timeframe_dayofweek.id') )
    month = Column(ForeignKey('timeframe_month.id'))
    quarter = Column(ForeignKey('timeframe_quarter.id'))
    year = Column(Integer, nullable = True)
    start_week = Column( ForeignKey('timeframe_week.start_of_week' ) )

    @property
    def date(self):
        return self.raw_date

    @date.setter
    def date(self, d):
        self.raw_date = d
        self.day = d.day
        self.month = d.month
        self.day_of_week = d.weekday()
        self.year = d.year
        self.quarter = self.__getQuarter(d) 
        self.start_week = self.__getStartWeek(d)
    
    @property
    def start_of_week(self):
        return self.start_week
    @property
    def end_of_week(self):
        if not hasattr(self, '_week'):
            self._week = Week.query.filter_by(start_of_week = self.start_week)[0]
        return self._week.end_of_week
    def __getStartWeek(self, d):
        dow = d.weekday()
        start_week = d - datetime.timedelta(days = dow)
        return start_week
    
    def __getQuarter(self, d):
        return ( d.month // 4 ) + 1
    
    
        