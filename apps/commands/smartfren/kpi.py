import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv, simplejson
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
import cgpolyencode
sys.path.append('../')

from app import db
OUTLET_FACILITY_TYPE_ID = 1

class SmartfrenKPI (Command) :
    option_list = (
        Option('--filename', '-p', dest='filename'),
        Option('--logfile', '-l', dest='logfile'),
        Option('--action', '-a', dest='action'),
    )
    
    valid_actions = ['dump','load']
    def run(self, filename, logfile, action):
        
        if action:
            if action in SmartfrenRegionMasterList.valid_actions:
                _action = action
            else:
                print 'specified action is not valid'
                print 'valid actions:'
                for _ in SmartfrenRegionMasterList.valid_actions:
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
 
    def load(self, filename):
        with open(filename, 'r') as f:
            encoder = cgpolyencode.GPolyEncoder()
            list_reader = csv.reader(f, delimiter=',')
            
            for obj in list_reader:
                boundary_id, boundary_name, boundary_parent_id, boundary_level_id, polygons_filename = obj
                           
                boundary = Boundary.query.filter_by(extref_id = int(boundary_id), level_id = 1).all()
                
                if not len(boundary):
                    b = Boundary(extref_id = boundary_id, name = boundary_name, level_id = boundary_level_id)
                    db.session.add(b)
                    db.session.commit()
                    
                    _f = open(polygons_filename, 'r')
                    
                    _psf = simplejson.loads(_f.read())
                    for _ps in _psf:
                        poly = BoundaryPolygons(boundary_id = b.id, geom=WKTSpatialElement("POLYGON((%s))"%(', '.join([' '.join([ str(j) for j in i]) for i in _ps]))   ))
                        encoded = encoder.encode([i[::-1] for i in poly.geom.coords(db.session)[0]])['points']
                        poly.encoded_poly = encoded
                        db.session.add( poly )
                                    
                db.session.commit()
                

    def dump(self, filename):
        with open(filename, 'w') as f:
            list_writer = csv.writer(f, delimiter=',')
            for _b in Boundary.query.filter_by( level_id = 1 ):
                
                
                boundary_id, boundary_name, boundary_parent_id, boundary_level_id, polygons_filename = _b.id, _b.name, _b.parent_id, _b.level_id, 'polygons_%s.json' % (_b.id,)
                list_writer.writerow([boundary_id, boundary_name, boundary_parent_id, boundary_level_id, polygons_filename])
                
                all_polygons = []
                for poly in BoundaryPolygons.query.filter_by(boundary_id = boundary_id):
                    polygons =  [ i for i in poly.geom.coords(db.session)[0]]
                    all_polygons.append(polygons)
                open(polygons_filename,'w').write(simplejson.dumps(all_polygons))
                
                
            # end for
        # end with
        
    # end def           
            

manager.add_command('smartfren_kpi_list', SmartfrenRegionMasterList())
