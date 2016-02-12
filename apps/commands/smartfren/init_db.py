import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv, simplejson,calendar
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
from app.views.wrappers.permissions import RolePermission
sys.path.append('../')

from app import db
OUTLET_FACILITY_TYPE_ID = 1

class SmartfrenInitDB (Command) :

    START_OF_WEEK = 3 # Thursday
    
    option_list = (
        Option('--action', '-a', dest='action'),
    )
    
    def run(self, action):
        if action == 'localuser':
            print 'Load initial user'
            self.load_initial_user()
        else:
            print 'Loading calendars'
            self.load_calendar()
            
            print 'Loading facility types'
            self.load_facility_types()
            
            print 'Loading boundary levels'
            self.load_boundary_levels()
            
            print 'Loading kpi type'
            self.load_kpi_type()

            print 'Loading Sales Force KPI Type'
            self.load_sales_force_kpi_type()
            
            print 'smartfren outlet subtype'
            self.load_smartfren_outlet_subtype_classification()
        db.session.commit()

            
    def load_calendar (self):
        start_year = 2013
        end_year = 2050
        
        # start_date = datetime.date(day = 1, month = 1, year = start_year)
        print 'Timeframe'
        db.session.execute (initTimeframe ())
        print 'Week'
        db.session.execute( initWeek ( start_year, end_year, SmartfrenInitDB.START_OF_WEEK ) )
        print 'Days'
        for i in range(start_year, end_year+1):
            initCalendar ( i, SmartfrenInitDB.START_OF_WEEK, db )
        
        
    
    def load_facility_types(self):
        f = FacilityType(id = 1, extref_id = 1, name = 'Outlet')
        db.session.add(f)
        db.session.commit()

        
    boundary_levels = [[1, 'National'], [2, 'Region'], [3,'Cluster'], [4, 'Outlet'] ]
    def load_boundary_levels (self):
        for obj in SmartfrenInitDB.boundary_levels:
            b = BoundaryLevelDesc(id = obj[0], description = obj[1])
            db.session.add(b)
        db.session.commit()
    
    def load_kpi_type(self):
        # add Activations KPI Type
        activation = KPIType ( name = 'Activations', facility_type_id = 1, id = 1)
        db.session.add(activation)
        
        sellout = KPIType ( name = 'Sellouts', facility_type_id = 1, id = 2)
        db.session.add(sellout)
        
        stocks = KPIType ( name = 'Stocks', facility_type_id = 1, id = 3)
        db.session.add(stocks)
        db.session.commit()
        
        _ = AggregationFunctionMap ( id = 1, kpi_type = activation.id, function_type = 0)
        db.session.add(_)
        
        _ = AggregationFunctionMap ( id = 2, kpi_type = sellout.id, function_type = 0)
        db.session.add(_)
        
        _ = AggregationFunctionMap ( id = 3, kpi_type = stocks.id, function_type = 1)
        db.session.add(_)
        
        db.session.commit()
    
    def load_smartfren_outlet_subtype_classification ( self ):
        _ = SmartfrenOutletProductClassificationType( type_name = 'Super Platinum' )
        db.session.add( _ )
        
        _ = SmartfrenOutletProductClassificationType( type_name = 'Platinum' )
        db.session.add( _ )

        _ = SmartfrenOutletProductClassificationType( type_name = 'Gold' )
        db.session.add( _ )        
        
        _ = SmartfrenOutletProductClassificationType( type_name = 'Silver' )
        db.session.add( _ )
        
        db.session.commit()
        
    def load_initial_user (self):
        r = Role()
              
        r.name = 'Administrator'
        
        db.session.add(r)
        db.session.commit()
      

    
        _r = RolePermission(r.id)

        _ = []
        for p in RolePageViewPermission.__available_permission_set__:
            _.append(p[0])
        _p = RolePageViewPermission.query.filter_by(role_id = r.id)[0]
        _p.permissions = {'date_updated' : datetime.datetime.now().isoformat(), 'values' : _}
        

        _ = _r.getBoundaryPermissionsHierarchy(default_permission = True)
        _p = RoleBoundaryViewPermission.query.filter_by(role_id = r.id)[0]
        _p.permissions = {'date_updated' : datetime.datetime.now().isoformat(), 'values' : _}
        

        _ = _r.getProductPermissionsHierarchy(default_permission = True)
        _p = RoleProductViewPermission.query.filter_by(role_id = r.id)[0]
        _p.permissions = {'date_updated' : datetime.datetime.now().isoformat(), 'values' : _}
        

        db.session.commit()
        
        u = UserAccount()
        u.username = 'localuser'
        u.account_status = AccountStatusType.ACTIVE

        u.password = 'localuser'

        u.auth_module_name = 'ruther_local'
        db.session.add(u)
        db.session.commit()

        ur = UserRole()
        ur.role_id = r.id
        ur.user_id = u.id
        db.session.add(ur)
        
        db.session.commit()

        
    def load_sales_force_kpi_type(self):
        # add Activations KPI Type
        _ = SalesForceKPIType ( name = 'Activations', id = 1)
        db.session.add(_)
        
        _ = SalesForceKPIType ( name = 'Sellouts', id = 2)
        db.session.add(_)
        
        _ = SalesForceKPIType ( name = 'Sellins',  id = 3)
        db.session.add(_)

        
        db.session.commit()
        
    
def initWeek(start_year, end_year, start_week_day, previous_year = True):
    # log.debug("Initializing weeks for year %s", year)
    s=''
    start = datetime.date(day = 1, month = 1, year = start_year)
    
    end =  datetime.date(day = 1, month = 1, year = end_year + 1)
    
    start_week = start - datetime.timedelta( days = start.weekday() + 7 ) + datetime.timedelta(days = start_week_day )
    
    # we only generate for weeks that started on the year
    if not previous_year:
        while start_week.year != start_year:
            start_week += datetime.timedelta(days = 7) 
 
    while start_week < end:
        t = '''INSERT INTO %(tablename)s ( start_of_week, end_of_week ) VALUES ( DATE '%(start)s', DATE '%(end)s');\n'''
        s += t % { 'tablename' : Week.__tablename__, 'start' : start_week.isoformat(), 'end' : ( start_week + datetime.timedelta(days = 6 ) ).isoformat()}

        start_week += datetime.timedelta(days = 7)

    return s

def initCalendar(year, start_week_day, db):
    start = datetime.date(day = 1, month = 1, year = year)
    end = start + datetime.timedelta(days = 365 if not calendar.isleap(year) else 366)
    d = Calendar()    
    curr = start
    s = ''

    while curr < end:
        d.date = curr
        
        
        # if curr.weekday < start_week_day:
            # start_week = curr - datetime.timedelta(days = 7 - ( start_week_day - curr.weekday() ))
        # else:
            # start_week = curr - datetime.timedelta(days = curr.weekday() - start_week_day)
            
        start_week = curr - datetime.timedelta( days = curr.weekday() ) + datetime.timedelta(days = start_week_day )
        if start_week > curr:
            start_week -= datetime.timedelta (days = 7 )
            
        t = '''INSERT INTO %(tablename)s ( raw_date, day, month, year, quarter, day_of_week, start_week ) VALUES ( DATE '%(raw_date)s', %(day)s, %(month)s, %(year)s, %(quarter)s, %(day_of_week)s, DATE '%(start_week)s');\n'''
        s = t % { 'tablename' : Calendar.__tablename__, 'raw_date' : curr.isoformat(), 'day' : d.day, 'month': d.month, 'year' : d.year, 'quarter' : d.quarter, 'day_of_week' : d.day_of_week, 'start_week' : start_week.isoformat() }
        curr += datetime.timedelta(days = 1)

        db.session.execute(s)

def initTimeframe():    
    s = ''


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 1, 'name' : "First Quarter"}


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 2, 'name' : "Second Quarter"}

    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 3, 'name' : "Third Quarter"}

    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Quarter.__tablename__, 'id' : 4, 'name' : "Fourth Quarter"}
        



    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 0, 'name' : "Monday"}


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 1, 'name' : "Tuesday"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 2, 'name' : "Wednesday"}

    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 3, 'name' : "Thursday"}


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 4, 'name' : "Friday"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 5, 'name' : "Saturday"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : DayOfWeek.__tablename__, 'id' : 6, 'name' : "Sunday"}
    


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 1, 'name' : "January"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 2, 'name' : "February"}
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 3, 'name' : "March"}
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 4, 'name' : "April"}


    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 5, 'name' : "May"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 6, 'name' : "June"}

    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 7, 'name' : "July"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 8, 'name' : "August"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 9, 'name' : "September"}
    
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 10, 'name' : "October"}

   
    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 11, 'name' : "November"}

    t = '''INSERT INTO %(tablename)s ( id, name ) VALUES ( %(id)s, '%(name)s');\n'''
    s += t % { 'tablename' : Month.__tablename__, 'id' : 12, 'name' : "December"}

    
    return s    
            

manager.add_command('smartfren_initdb', SmartfrenInitDB())
