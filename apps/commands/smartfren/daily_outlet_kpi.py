import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
sys.path.append('../')

from app import db
OUTLET_FACILITY_TYPE_ID = 1

class SmartfrenOutletOverallData (Command) :
    option_list = (
        Option('--filename', '-p', dest='filename'),
        Option('--action', '-a', dest='action'),
        Option('--date', '-d', dest='date_str'),
    )
    
    valid_actions = ['dump','load', 'aggregate']
    def run(self, filename, action, date_str):
        
        if action:
            if action in SmartfrenOutletOverallData.valid_actions:
                _action = action
            else:
                print 'specified action is not valid'
                print 'valid actions:'
                for _ in SmartfrenOutletOverallData.valid_actions:
                    print _
                # end for
                sys.exit(0)
            # end if
        else:
            print 'missing action parameter'
            sys.exit(0)

        if not date_str:
            print 'missing --date parameter'
            sys.exit(0)
      
        if action == 'dump':
            self.dump(filename)
            
        if action == 'load':
            self.load(filename, date_str)
        
        if action == 'aggregate':
            self.aggregate(date_str)
            
    def load(self, filename, date_str):
        if not filename:
            print 'no filename specified'
            sys.exit(0)
        #end if

        
        with open(filename, 'r') as f:
            list_reader = csv.reader(f, delimiter=',')
            year, month, day = date_str.split('-')
            
            kpi_date = datetime.date(int(year), int(month), int(day))
            calendar = Calendar.query.filter_by( raw_date = kpi_date)[0]
            
            for obj in list_reader:
                outletID, activationKPI, sellOutKPI, stockKPI  = obj
              
                q = Facility.query.filter_by(extref_id = int(outletID)).all()
                
               
                if len(q):             
                    _facility = q[0]

                    boundary = Boundary.query.get(_facility.boundary_id)
                    _ = FacilityKPI(facility_id = _facility.id, facility_type_id = _facility.facility_type_id, facility_boundary_id = _facility.boundary_id, facility_boundary_level_id = boundary.level_id, facility_boundary_parent_id = boundary.parent_id, kpi_type = 1, kpi = activationKPI)
                    _.calendar_id = calendar.id
                    _.date_day_of_week = calendar.day_of_week
                    _.date_day = calendar.day
                    _.date_month = calendar.month
                    _.date_year = calendar.year
                    _.date_start_of_week = calendar.start_week
                    _.date_end_of_week = calendar.start_week + datetime.timedelta( days = 6 )
                    _.raw_date = kpi_date
                    _.date_quarter = calendar.quarter
               
                    db.session.add(_)
                    
                    _ = FacilityKPI(facility_id = _facility.id, facility_type_id = _facility.facility_type_id, facility_boundary_id = _facility.boundary_id, facility_boundary_level_id = boundary.level_id, facility_boundary_parent_id = boundary.parent_id, kpi_type = 2, kpi = sellOutKPI)
                    _.calendar_id = calendar.id
                    _.date_day_of_week = calendar.day_of_week
                    _.date_day = calendar.day
                    _.date_month = calendar.month
                    _.date_year = calendar.year
                    _.date_start_of_week = calendar.start_week
                    _.date_end_of_week = calendar.start_week + datetime.timedelta( days = 6 )
                    _.raw_date = kpi_date
                    _.date_quarter = calendar.quarter
                    
                    db.session.add(_)         
                    
                    _ = FacilityKPI(facility_id = _facility.id, facility_type_id = _facility.facility_type_id, facility_boundary_id = _facility.boundary_id, facility_boundary_level_id = boundary.level_id, facility_boundary_parent_id = boundary.parent_id, kpi_type = 3, kpi = stockKPI)
                    _.calendar_id = calendar.id
                    _.date_day_of_week = calendar.day_of_week
                    _.date_day = calendar.day
                    _.date_month = calendar.month
                    _.date_year = calendar.year
                    _.date_start_of_week = calendar.start_week
                    _.date_end_of_week = calendar.start_week + datetime.timedelta( days = 6 )
                    _.raw_date = kpi_date
                    _.date_quarter = calendar.quarter
                    
                    db.session.add(_)                    
 
                else:
                    print error 
            db.session.commit()
                
                # end if
            # end for
    
    #dump create 
    def dump(self, filename):
        if not filename:
            print 'no filename specified'
            sys.exit(0)
        #end if

        with open(filename, 'w') as f:
           
            list_writer = csv.writer(f, delimiter=',')
            for f in Facility.query.all():
                _ = db.session.query( KPI.kpi_type, func.sum(KPI.kpi), func.sum( KPI.actual), KPI.facility_id, KPI.raw_date).filter_by(facility_id = f.id, raw_date = datetime.date(2013, 8, 12)).group_by( KPI.facility_id, KPI.raw_date,KPI.kpi_type)  #.group_by(KPI.facility_id, KPI.facility_type_id, KPI.facility_boundary_id, KPI.facility_boundary_level_id, KPI.facility_boundary_parent_id, KPI.kpi_type, KPI.calendar_id, KPI.raw_date, KPI.day_of_week, KPI.date_day, KPI.date_month, KPI.date_quarter, KPI.date_start_of_week, KPI.date_end_of_week)
                _t = {}
                

                for obj in _:
                    # print obj
                    _t[obj[0]] = obj[1]
                
                outletID, activationKPI, sellOutKPI, stockKPI = f.extref_id, _t[1], _t[2], _t[3]
                

                list_writer.writerow([outletID, activationKPI, sellOutKPI, stockKPI])
                
            # end for
        # end with
        
    # end def
    
    def aggregate (self, date_str):
        year, month, day = [ int(obj) for obj in date_str.split('-') ]
        start_week = self.determine_weekdate(year, month, day)
        print start_week
        print 'Deleting'
        self.delete_tables ( SumBoundaryDay.__tablename__, year, month, day )
        self.delete_tables ( SumBoundaryWeek.__tablename__, start_week =  start_week)
        self.delete_tables ( SumBoundaryMonth.__tablename__, year, month )
        self.delete_tables ( SumBoundaryYear.__tablename__, year )
        
        print 'aggregating boundary'
        db.session.execute('SELECT aggregate_boundary_day_sum(:date_day, :date_month, :date_year)', { 'date_day' : day, 'date_month' : month, 'date_year' : year } )
        db.session.commit()     
        
        db.session.execute('SELECT aggregate_boundary_week_sum(:date_day, :date_month, :date_year)', { 'date_day': start_week.day , 'date_month' :start_week.month, 'date_year' : start_week.year } )
        db.session.commit() 
        
        db.session.execute('SELECT aggregate_boundary_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

        db.session.execute('SELECT aggregate_boundary_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit() 
        
        print 'deleting'
        self.delete_tables ( SumFacilityWeek.__tablename__, start_week = self.determine_weekdate(year, month, day) )
        self.delete_tables ( SumFacilityMonth.__tablename__, year, month )
        self.delete_tables ( SumFacilityYear.__tablename__, year )
        
        print 'aggregating facility'
        db.session.execute('SELECT aggregate_facility_week_sum(:date_day, :date_month, :date_year)', { 'date_day': start_week.day, 'date_month' :start_week.month, 'date_year' : start_week.year } )
        db.session.commit()   

        db.session.execute('SELECT aggregate_facility_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
    
        db.session.execute('SELECT aggregate_facility_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit() 
        
        # self.sum_aggregate_facility(int(month), int (year))
    
    def determine_weekdate (self, year, month, day):

        c = Calendar.query.filter_by(raw_date = datetime.date(year, month, day))[0]
        return c.start_week
        
    def delete_tables(self, tablename, year = None, month = None, day = None, start_week = None):        
        sql_params_dict = { }
        sql_str = 'DELETE FROM %(tablename)s' % { 'tablename' : tablename }

        if start_week:
            sql_str += ' WHERE date_start_of_week = :date_start_week'
            sql_params_dict['date_start_week'] = start_week
        else:
            if year:
                sql_str += ' WHERE date_year = :date_year'
                sql_params_dict['date_year'] = year
      
            if year and month:
                sql_str += ' AND date_month = :date_month'
                sql_params_dict['date_month'] = month
      
            if year and month and day:
                sql_str += ' AND date_day = :date_day'
                sql_params_dict['date_day'] = day
                       
        db.session.execute(sql_str, sql_params_dict)
        db.session.commit()
    
    def sum_aggregate_boundary(self,):
        db.session.execute('SELECT aggregate_boundary_day_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()   
        
        db.session.execute('SELECT aggregate_boundary_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()   

        db.session.execute('SELECT aggregate_boundary_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

        db.session.execute('SELECT aggregate_boundary_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()          

    def sum_aggregate_facility (self, month, year):
        
        db.session.execute('SELECT aggregate_facility_week_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()   

        db.session.execute('SELECT aggregate_facility_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

        db.session.execute('SELECT aggregate_facility_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit() 
manager.add_command('smartfren_outlet_overall_data', SmartfrenOutletOverallData())
