import os, sys, logging, datetime, time, random, simplejson, argparse, collections
sys.path.append('../')

from app import db
from app.models import *

                 
log = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))    
stdout_handler.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.addHandler(stdout_handler)

actual = [0, 10 , 20, 30, 40, 50, 60, 70, 80 , 90 , 100]
target = [20, 40, 60, 80, 100, 120]


def createSalesForceData(start_date, end_date):
    print 'Creating Sales Force Mock data from %s to %s' % ( start_date.isoformat(' '), end_date.isoformat(' '))
    _ = SalesForceRoles(id=1, extref_id = 1, name = 'SFA')
    db.session.add(_)
    
    _ = SalesForceRoles(id=2, extref_id = 2, name = 'SGA')
    db.session.add(_)
    
    _ = SalesForceRoles(id=3, extref_id = 3, name = 'Canvasser')
    db.session.add(_)
    
    _ = SalesForceRoles(id=4, extref_id = 4, name = 'Direct Sales')
    db.session.add(_)
    
    _ = SalesForceRoles(id=5, extref_id = 5, name = 'SGP')
    db.session.add(_)
    
    db.session.commit()
    print 'Created Sales Force Roles'
    current = start_date
    
    kpi_type_list = SalesForceKPIType.query.all()
    
    facility_list = collections.deque(Facility.query.filter_by(facility_type_id = 1))
    while len(facility_list):
        print 'There are %d outlet to process' % ( len(facility_list), )
        outlet = facility_list.pop()
        
        sf_list = []            
        print 'Creating Sales Force for outlet %s' % ( outlet.name, )
        
        for role in SalesForceRoles.query.all():
            _ = SalesForce (name = outlet.name + ' - ' + role.name, sf_role_id = role.id)        
            db.session.add(_)
            sf_list.append(_)
            
        db.session.commit()
        current = start_date
        print 'Creating Sales Force KPI Data from %s to %s' % ( start_date.isoformat(' '), end_date.isoformat(' '))
        while ( current <= end_date ):
            calendar_obj = Calendar.query.filter_by ( raw_date = current )[0]

            for sf in sf_list:
                for kpi_type in kpi_type_list:
                    _ = SalesForceFacilityKPIDaily( sales_force_id = sf.id, sales_force_role_id = sf.sf_role_id, kpi_type = kpi_type.id, facility_id = outlet.id, facility_type_id = 1, facility_boundary_id = outlet.boundary_id, facility_boundary_level_id = outlet.boundary.level_id, facility_boundary_parent_id = outlet.boundary.parent_id)
                    _.calendar_id = calendar_obj.id

                    _.raw_date = calendar_obj.raw_date
                    _.date_day = calendar_obj.day
                    _.date_month = calendar_obj.month
                    _.day_of_week = calendar_obj.day_of_week
                    _.date_year = calendar_obj.year
                    _.date_quarter = calendar_obj.quarter 
                    _.date_start_of_week = calendar_obj.start_week
                    _.date_end_of_week = calendar_obj.start_week + datetime.timedelta ( days = 6 )
                    _.actual = actual [ random.randint(0, len(actual) - 1) ]
                    _.target = target [ random.randint(0, len(target) - 1) ]
                    _.kpi = ( float(_.actual) / float(_.target) ) * 100.0

                    db.session.add(_)
                                
            current += datetime.timedelta(days = 1)
            # end for
        # end while
        
        db.session.commit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Boundaries, Products, Stores data.')
    parser.add_argument('--year', dest='year', action='store',
                       help='Input file in JSON format.')

    parser.add_argument('--month', dest='month', action='store',
                       help='Destination filename where SQL output will be generated.')

    args = parser.parse_args()
    
    month = int ( args.month )
    year = int ( args.year )
    
    start_date = datetime.datetime(day = 1, month = month, year = year )
    
    end_date = start_date + datetime.timedelta(days = calendar.monthrange(year, month)[1] -1)
    
    createSalesForceData( start_date, end_date )
    
    
    
    