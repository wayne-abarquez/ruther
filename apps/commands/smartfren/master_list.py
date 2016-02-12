import os, sys, logging, datetime, time, random, simplejson, argparse, random, csv
from manage import manager
from flask.ext.script import Command, Option
from geoalchemy import *
from app.models import *
sys.path.append('../')

class ProductIntegration:
    def __init__(self, log):
        self.log_object = log
        
    def dump( self, filename ):
        pass
    def load (self, filename ):
        f = open ( filename , 'r')
        reader = csv.reader(f, delimiter=',')
        
        existing_products = {}
        p = Product.query.all()
        for obj in p:
            existing_products[obj.extref_id] = obj
        
        reader.next() # skip header
        for row in reader:
            product_id, product_name, product_family_id = row
            
            if existing_products.has_key(product_id):
                self.log_object.info ( 'Products exists. Updating .... id: %s, name: %s, family_name: %s.' , product_id, product_name, product_family_id)
                _ = existing_products[product_id]
                
                ProductGroupMap.query.filter_by(product_id = _.id).delete()
                
                _.name = product_name
                db.session.commit()

                pg = ProductGroup.query.filter_by(extref_id = product_family_id).all()
                if len ( pg ) < 1:
                    self.log_object.info ('Error - No Product Family for this product. id: %s, name: %s, family_name: %s', product_id, product_name, product_family_id )
                else:
                    pg = pg[0]
                    _ = ProductGroupMap(product_id = _.id, group_id = pg.id)
                    db.session.add(_)
                    db.session.commit()
            else:
                pg = ProductGroup.query.filter_by(extref_id = product_family_id).all()
                if len(pg) > 0 :
                    pg = pg[0]
                    _ = Product(extref_id = product_id, name = product_name)
                    db.session.add(_)
                    db.session.commit()
                    
                    _ = ProductGroupMap(product_id = _.id, group_id = pg.id)
                    db.session.add(_)
                    db.session.commit()
                    self.log_object.info ('Success - Products added. id: %s, name: %s, family_name: %s', product_id, product_name, product_family_id)
                else:
                    self.log_object.info ('Error - No Product Family for this product. id: %s, name: %s, family_name: %s', product_id, product_name, product_family_id )
                
class ProductFamiliesIntegration:
    
    def __init__(self, log):
        self.log_object = log

    def log(self, msg):
        self.log_object.info(msg)
        
    def dump (self, filename ):
        pass
        
    def load ( self, filename, log = None ):
        f = open ( filename , 'r')
        reader = csv.reader(f, delimiter=',')
        
        existing_families = {}
        
        pf = ProductGroup.query.all()
        
        for obj in pf:
            existing_families[obj.extref_id] = obj
        # end for
        
        reader.next()
        for row in reader:
            product_family_id, product_family_name = row
            
            if existing_families.has_key(product_family_id):
                self.log_object.info (  'Error - Product Family already exists. id: %s name: %s' ,product_family_id, product_family_name )
            else:
                _ = ProductGroup(extref_id =product_family_id, description = product_family_name)
                db.session.add(_)
                db.session.commit ()
                
                self.log_object.info (  'Success - Product Family added. id: %s name: %s', product_family_id, product_family_name )
                
            # end if
        # end for


class SalesForceRolesIntegration:
    
    def __init__(self, log):
        self.log_object = log

    def log(self, msg):
        self.log_object.info(msg)
        
    def dump (self, filename ):
        pass
        
    def load ( self, filename, log = None ):
        f = open ( filename , 'r')
        reader = csv.reader(f, delimiter=',')
        print 'hi'
        existing_roles = {}
        
        pf = SalesForceRoles.query.all()
        
        for obj in pf:
            existing_roles[obj.extref_id] = obj
        # end for
        
        reader.next()
        for row in reader:
            role_id, role_name = row
            
            if existing_roles.has_key(role_id):
                self.log_object.info ('Error - Sales Force Role already exists. id: %s name: %s', role_id, role_name )
            else:
                _ = SalesForceRoles(extref_id =role_id, name = role_name)
                db.session.add(_)
                db.session.commit ()
                
                self.log_object.info ('Success - Sales Force Role added. id: %s name: %s', role_id, role_name )
                
            # end if
        # end for
        
class SalesForceIntegration:
    
    def __init__(self, log):
        self.log_object = log

    def log(self, msg):
        self.log_object.info(msg)
        
    def dump (self, filename ):
        pass
        
    def load ( self, filename, log = None ):
        f = open ( filename , 'r')
        reader = csv.reader(f, delimiter=',')
        
        existing = {}
        
        pf = SalesForce.query.all()
        
        for obj in pf:
            existing[obj.extref_id] = obj
        # end for
        
        reader.next()
        for row in reader:
            id, name, role_id = row
            id = id.decode('utf-8')
            r = SalesForceRoles.query.filter_by(extref_id = role_id).all()
            
            if len(r) > 0:
                r = r[0]
                if existing.has_key(id):
                    
                    _ = existing[id]
                    _.name = name
                    _.sf_role_id = r.id
                    db.session.commit()
                    
                    self.log_object.info ('Success - Sales Force already exists. Updating id: %s name: %s role: %s', id, name, role_id )
                    
                else:
                    _ = SalesForce(extref_id =id, name = name, sf_role_id = r.id)
                    db.session.add(_)
                    db.session.commit ()
                    
                    self.log_object.info ('Success - Sales Force added. id: %s name: %s role: %s', id, name, role_id )
                # end if
            # end if
        # end for

class OutletIntegration:
    
    def __init__(self, log):
        self.log_object = log

    def log(self, msg):
        self.log_object.info(msg)
        
    def dump (self, filename ):
        pass
        
    def load ( self, filename, log = None ):
        f = open ( filename , 'r')
        reader = csv.reader(f, delimiter=',')
        
        existing = {}
        
        f = Facility.query.all()
        
        for obj in f:
            existing[obj.extref_id] = obj
        # end for
        
        reader.next()
        for row in reader:
            outlet_id, outlet_name, outlet_type, clusterid, gps_latitude, gps_longitude , owner_name,  address , image_path = row
            id = id.decode('utf-8')
            r = SalesForceRoles.query.filter_by(extref_id = role_id).all()
            
            if len(r) > 0:
                r = r[0]
                if existing.has_key(id):
                    
                    _ = existing[id]
                    _.name = name
                    _.sf_role_id = r.id
                    db.session.commit()
                    
                    self.log_object.info ('Success - Sales Force already exists. Updating id: %s name: %s role: %s', id, name, role_id )
                    
                else:
                    _ = facility(extref_id =id, name = name, sf_role_id = r.id)
                    db.session.add(_)
                    db.session.commit ()
                    
                    self.log_object.info ('Success - Sales Force added. id: %s name: %s role: %s', id, name, role_id )
                # end if
            # end if
        # end for
        
class SmartfrenIntegrationFactory:

    def getProductFamilies(self, log):
        return ProductFamiliesIntegration(log)
    
    def getProducts(self,log):
        return ProductIntegration(log)
    
    def getSalesForceRoles(self, log):
        return SalesForceRolesIntegration(log)
    
    def getSalesForce(self, log):
        return SalesForceIntegration(log)

class SmartfrenMasterList( Command ):
    option_list = (
        Option('--source-directory', '-s', dest='source_directory'),
        Option('--logfile', '-l', dest='logfile'),
        # Option('--action', '-a', dest='action'),
    )
  
        
    
    def run(self, source_directory, logfile):
        factory = SmartfrenIntegrationFactory()
        logger = logging.getLogger('SmartrenMasterList')
        
        if logfile:
            file_handler = logging.FileHandler(logfile)
            file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))    
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)
        else:
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))    
            stdout_handler.setLevel(logging.INFO)
            logger.addHandler(stdout_handler)
        
        # end if
        
        logger.setLevel(logging.INFO)
 
        if not source_directory:
            print '--source-directory not specified'
            
        else:
            pf_csv = os.path.join(source_directory, 'product_family_master_list.csv')
            if os.path.exists( pf_csv ):
                _ = factory.getProductFamilies(logger)
                _.load(pf_csv)
                
            p_csv = os.path.join(source_directory, 'product_master_list.csv')
            if os.path.exists( p_csv ):
                _ = factory.getProducts (logger)
                _.load(p_csv)
                
            sfr_csv = os.path.join(source_directory, 'sales_force_role_master_list.csv')
            if os.path.exists( sfr_csv ):
                _ = factory.getSalesForceRoles(logger)
                print 'hi'
                _.load(sfr_csv)

            sf_csv = os.path.join(source_directory, 'sales_force_master_list.csv')
            if os.path.exists( sf_csv ):
                _ = factory.getSalesForce(logger)
                _.load(sf_csv)
                
manager.add_command('smartfren_master_list', SmartfrenMasterList())