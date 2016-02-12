import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
sys.path.append('../')

from app import db
OUTLET_FACILITY_TYPE_ID = 1

class SmartfrenSalesForceKPI (Command) :
    option_list = (
        Option('--filename', '-p', dest='filename'),
        Option('--action', '-a', dest='action'),
        Option('--date', '-d', dest='date_str'),
    )
    
    valid_actions = ['dump','load', 'aggregate']
    def run(self, filename, action, date_str):
        
        if action:
            if action in SmartfrenSalesForceKPI.valid_actions:
                _action = action
            else:
                print 'specified action is not valid'
                print 'valid actions:'
                for _ in SmartfrenSalesForceKPI.valid_actions:
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
            print 'missing --filename parameter'
            sys.exit(0)
        #end if

        if not date_str:
            print 'missing --date parameter'
        

        print 'Not Implemented'
        sys.exit(0)
    #dump create 
    def dump(self, filename):
        if not filename:
            print 'missing --filename parameter'
            sys.exit(0)
        #end if

        if not date_str:
            print 'missing --date parameter'
            sys.exit(0)
      
        print 'Not Implemented'
    # end def
    
    def aggregate (self, date_str):
    
        if not date_str:
            print 'missing --date parameter'
            sys.exit(0)
        
        if date_str == 'all':
            ret = db.session.execute('SELECT DISTINCT ON (date_day, date_month, date_year) date_day, date_month, date_year FROM ruther_sales_force_facility_kpi_daily')
            for obj in ret:
                day, month, year = obj[0], obj[1], obj[2]
                print 'aggregating day %s-%s-%s' % ( year, month, day )
                self.aggregate_day(day, month, year)
            # end for
            
            ret = db.session.execute('SELECT DISTINCT ON (date_start_of_week) date_start_of_week FROM ruther_sales_force_facility_kpi_daily')
            for obj in ret:
                start_week = obj[0]
                print 'aggregating week %s' % ( start_week.isoformat() )
                self.aggregate_week(start_week)
            # end for
            
            ret = db.session.execute('SELECT DISTINCT ON (date_month, date_year) date_month, date_year FROM ruther_sales_force_facility_kpi_daily')
            for obj in ret:
                month, year = obj[0], obj[1]
                print 'aggregating month %s-%s' % ( year, month)
                self.aggregate_month(month, year)
            # end for
            
            ret = db.session.execute('SELECT DISTINCT ON ( date_year) date_year FROM ruther_sales_force_facility_kpi_daily')
            for obj in ret:
                year = obj[0]
                print 'aggregating %s' % ( year, )
                self.aggregate_year(year)
            # end for
        else:
        
            print 'Not Implemented. only all option available'
        # else:
            # try:
                # year, month, day = [ int(obj) for obj in date_str.split('-') ]
            # except:
                # print 'invalid --date parameter'
                # sys.exit(0)

            # start_week = self.determine_weekdate(year, month, day)
            
            # print 'aggregating day %s-%s-%s' % ( year, month, year )
            # self.aggregate_day(day, month, year)

            # print 'aggregating week %s' % ( start_week.isoformat() )
            # self.aggregate_week(start_week)
            
            # print 'aggregating month %s-%s' % ( year, month)
            # self.aggregate_month(month, year)
            
            # print 'aggregating %s' % ( year, )
            # self.aggregate_year(year)
        
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
        
    def aggregate_month(self, month, year):
        self.delete_tables ( SalesForceBoundaryKPIMonth.__tablename__, year, month )        
        db.session.execute('SELECT aggregate_boundary_sales_force_kpi_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()
        
        self.delete_tables ( SalesForceFacilityKPIMonth.__tablename__, year, month )
        db.session.execute('SELECT aggregate_facility_sales_force_kpi_month_sum(:date_month, :date_year)', { 'date_month' : month, 'date_year' : year } )
        db.session.commit()

        
    def aggregate_day (self, day, month, year):
        self.delete_tables ( SalesForceBoundaryKPIDaily.__tablename__, year, month, day )     
        db.session.execute('SELECT aggregate_boundary_sales_force_kpi_day_sum(:date_day, :date_month, :date_year)', { 'date_day' : day, 'date_month' : month, 'date_year' : year } )
        db.session.commit()       
    
    def aggregate_week (self, week_date):
        day, month, year = week_date.day, week_date.month, week_date.year
        self.delete_tables ( SalesForceBoundaryKPIWeekly.__tablename__, start_week = week_date )   
        db.session.execute('SELECT aggregate_boundary_sales_force_kpi_week_sum(:date_day, :date_month, :date_year)', {'date_day' : day, 'date_month' : month, 'date_year' : year } )
        db.session.commit()
        
        self.delete_tables ( SalesForceFacilityKPIWeekly.__tablename__, start_week = week_date )         
        db.session.execute('SELECT aggregate_facility_sales_force_week_sum(:date_day, :date_month, :date_year)', { 'date_day' : day, 'date_month' : month, 'date_year' : year } )
        db.session.commit()
        

    def aggregate_year(self, year):
        self.delete_tables ( SalesForceBoundaryKPIYear.__tablename__, year )        
        db.session.execute('SELECT aggregate_boundary_sales_force_kpi_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()
        
        self.delete_tables ( SalesForceFacilityKPIYear.__tablename__, year )            
        db.session.execute('SELECT aggregate_facility_sales_force_kpi_year_sum(:date_year)', { 'date_year' : year } )
        db.session.commit()

        
manager.add_command('smartfren_salesforce_kpi', SmartfrenSalesForceKPI())
