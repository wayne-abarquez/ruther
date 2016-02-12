import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
sys.path.append('../')

from app import db
OUTLET_FACILITY_TYPE_ID = 1

class SmartfrenOutletMasterList (Command) :
    option_list = (
        Option('--filename', '-p', dest='filename'),
        Option('--logfile', '-l', dest='logfile'),
        Option('--action', '-a', dest='action'),
    )
    
    valid_actions = ['dump','load']
    def run(self, filename, logfile, action):
        
        if action:
            if action in SmartfrenOutletMasterList.valid_actions:
                _action = action
            else:
                print 'specified action is not valid'
                print 'valid actions:'
                for _ in SmartfrenOutletMasterList.valid_actions:
                    print _
                # end for
                sys.exit(0)
            # end if
        else:
            print 'missing action parameter'
            sys.exit(0)

        if not filename:
            print 'no filename specified'
            sys.exit(0)
        #end if
        
        if action == 'dump':
            self.dump(filename)
            
        if action == 'load':
            self.load(filename)
    def _add_icon_to_outlet(self, facility, f_type):
        icon = SmartfrenOutletMasterList.OUTLET_ICON[f_type]    
        
        if not bool(FacilitySchema.query.filter_by(column_name='icon').count()):
            icon_schema = FacilitySchema(column_name = 'icon', data_type = FacilityColumnSchema_DataType.String)
            db.session.add(icon_schema)
            db.session.commit()
            
        else:
            icon_schema = FacilitySchema.query.filter_by(column_name = 'icon').one()

            
        q = FacilityCustomData.query.filter_by(schema_id = icon_schema.id, facility_id = facility.id).all()
        if len(q) < 1:
            store_to_add_icon = FacilityCustomData(schema_id = icon_schema.id, facility_id = facility.id, data = icon)
            db.session.add(store_to_add_icon)     
        else:
            store_icon = q[0]
            store_icon.data = icon
        db.session.commit()
    def load(self, filename):
        with open(filename, 'r') as f:
            list_reader = csv.reader(f, delimiter=',')
            
            for obj in list_reader:
                outletID, outlet_name, _type, _subType, clusterID, latitude, longitude = obj
              
                q = Facility.query.filter_by(extref_id = str(outletID)).all()
                
                boundary = Boundary.query.filter_by(extref_id = int(clusterID))[0]
                
                _facility = None
                
                if len(q):
                
                    _facility = q[0]
                    _facility.name = outlet_name
                
                    _facility.boundary_id = boundary.id
                    
                    _facility.geom = WKTSpatialElement("POINT(%s %s)"%(latitude, longitude))
                    
                    
                
                else:
                    _facility = Facility(name = outlet_name, facility_type_id = 1, extref_id = str(outletID), boundary_id = boundary.id, geom = WKTSpatialElement("POINT(%s %s)"%(latitude, longitude)))
                    self._add_icon_to_outlet(_facility, _type)
                    db.session.add(_facility)
                
                db.session.commit()
                
                self._add_icon_to_outlet(_facility, _type)
                
                if _facility:
                    self.go_through_facility_types(_facility, [_type, _subType] )
                # end if
            # end for
    
    
    # THis is because our existing OLD schema don't have these.
    RANDOM_OUTLET_TYPE = [ 'Regular', 'Star', 'Prime', 'SGO', 'Smile' ]
    RANDOM_OUTLET_SUBTYPE = [ 'GOLD', 'SILVER', 'BRONZE' ]
    OUTLET_ICON =  { 'Regular': 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=R|336699|FFFFFF', 
                            'Star' : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=S|FF0000|FFFFFF',
                            'Prime' : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=P|00FF00|FFFFFF',
                            'SGO' : 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=G|660066|FFFFFF',
                            'Smile': 'http://chart.apis.google.com/chart?chst=d_map_pin_letter&amp;chld=I|FF9900|FFFFFF' }
    def dump(self, filename):
        with open(filename, 'w') as f:
            list_writer = csv.writer(f, delimiter=',')
            for f in Facility.query.all():
                points = f.geom.coords(db.session)
                type_name, sub_type_name ,icon = self.get_random_outlet_type()
                outletID, outlet_name, clusterID, latitude, longitude = f.id, f.name, f.boundary_id, points[0], points[1], icon
                list_writer.writerow([outletID, outlet_name, type_name, sub_type_name, clusterID, latitude, longitude])
                
            # end for
        # end with
        
    # end def
            
            
            
    def get_random_outlet_type(self):
        _type = random.randint(0,4)
        
        _type_name = SmartfrenOutletMasterList.RANDOM_OUTLET_TYPE[_type]

        _sub_type_name = ''
        if _type == 1:
            _sub_type = random.randint(0,2)
            _sub_type_name = SmartfrenOutletMasterList.RANDOM_OUTLET_SUBTYPE[_sub_type]
        
        return _type_name, _sub_type_name, _icon
        
    def go_through_facility_types (self, facility, types):
        for obj in FacilityTagMapping.query.filter_by ( facility_id = facility.id ).all():
            db.session.delete(obj)
        db.session.commit()
           
           
        for _type in types:
            if _type:
                tag = FacilityTagMapping()
                tag.facility_id = facility.id
                tag.facility_tag_name = _type
                db.session.add(tag)
        db.session.commit()

manager.add_command('smartfren_outlet_master_list', SmartfrenOutletMasterList())
