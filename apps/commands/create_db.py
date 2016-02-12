import os, sys, logging, datetime, time, random, simplejson, argparse
from manage import manager
from flask.ext.script import Command, Option

sys.path.append('../')

from app import db

class CreateDB (Command) :
    option_list = (
        Option('--postgis', '-p', dest='postgis'),
        
    )
    
    def run (self, postgis):
        if postgis:
            if not os.path.isfile(os.path.join(postgis, 'postgis.sql')):
                print 'Unable to find ' + os.path.join(postgis, 'postgis.sql')
                
            if not os.path.isfile(os.path.join(postgis, 'spatial_ref_sys.sql')):
                print 'Unable to find ' + os.path.join(postgis, 'spatial_ref_sys.sql')
  
            if not (os.path.isfile(os.path.join(postgis, 'postgis.sql')) or os.path.isfile(os.path.join(postgis, 'spatial_ref_sys.sql'))):
  
                sys.exit(0)
        else:
            print postgis
            print '--postgis parameter not defined'
            sys.exit(0)
        
        print 'Clobbering existing schemas....'
        db.session.execute('''drop schema public cascade; create schema public;''')
        db.session.commit()
        
        print 'Uploading postgis'
        f = open( os.path.join(postgis, 'postgis.sql') )
        s  = f.read()
        f.close()
        db.session.execute(s)

        f = open( os.path.join(postgis, 'spatial_ref_sys.sql') )
        s  = f.read()
        f.close()
        db.session.execute(s)
        
        print 'Creating all Flask Tables...'
        db.create_all()
        
        

        _ = []
        sql_path = os.path.join('sql', 'partition')
        for obj in os.listdir(sql_path):
            _.append(obj)
        
        for obj in _:
            print 'uploading %s' % ( obj, )
            f = open (os.path.join(sql_path, obj),'r')
            s = f.read()
            f.close()
            db.session.execute(s)
        print 'Done'
            
manager.add_command('create_db', CreateDB())