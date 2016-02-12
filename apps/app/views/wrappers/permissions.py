from app import app, lm, db 
from app.models import *
from sqlalchemy import *
import config
from datetime import datetime, date, timedelta
import os, simplejson, time, traceback, re, pprint
from flask import abort
log = app.logger

class AuthenticatedUser:
    def __init__(self, id):
    
        self.user = UserAccount.query.get(id)
        role_q = UserRole.query.outerjoin(Role, UserRole.role_id == Role.id).filter(UserRole.user_id == id).add_entity(Role).all()

        if len(role_q) > 0:
            self.role = role_q[0][1]
            self._role_permission = RolePermission(self.role.id)

        else:
            self._role = None
            self._role_permission = None
    
    @property
    def username (self):
        return self.user.username
        
    @property
    def role_permission(self):
        return self._role_permission

    def is_authenticated(self):
        return True

    def is_active(self):
        return ( self.user.account_status == AccountStatusType.ACTIVE )

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.user.id)
            
    
    def update_last_login_time(self, autosave = False):
        self.user.last_login_datetime = datetime.now()
        if autosave:
            db.session.commit()
    
    def update_last_access_time(self, autosave = False):
        self.user.last_access_datetime = datetime.now()
        if autosave:
            db.session.commit()
            
    def save():
        db.session.commit()
    
    @property
    def page_view_permission (self):
        return self.role_permission.page_view_permission_context()
        
    def __repr__(self):
        return '<Authenticated User %r>' % (self.user.username)
    
        

    
# wrapper class for Role and its permissions.
class RolePermission:

    def __init__(self, id):
        self.Role = Role.query.get(id)
        
        q = RoleBoundaryViewPermission.query.filter_by(role_id = self.Role.id).all()
        
        if len(q) > 0:
            _p = q[0]
        else:
            _p = RoleBoundaryViewPermission()
            _p.role_id = self.Role.id
            db.session.add(_p)
            db.session.commit()
            
        self.RoleBoundaryViewPermission = _p
        
        q = RoleProductViewPermission.query.filter_by(role_id = self.Role.id).all()
        if len(q) > 0:
            _p = q[0]
        else:
            _p = RoleProductViewPermission()
            _p.role_id = self.Role.id
            db.session.add(_p)
            db.session.commit()
        print _p.permissions    
        self.RoleProductViewPermission = _p

        q = RolePageViewPermission.query.filter_by(role_id = self.Role.id).all()
        if len(q) > 0:
            _p = q[0]
        else:
            _p = RolePageViewPermission()
            _p.role_id = self.Role.id
            db.session.add(_p)
            db.session.commit()
            
        self.RolePageViewPermission = _p
    
    

        
    def validate(self):
        _ = self.RoleBoundaryViewPermission.permissions
        if not _.has_key('values'):
            return False
        _ = _['values']
        
        if len (_) < 1:  
            return False
        
        if len(_['boundaries']) < 1 and not _['top_lvl_permission']:
            return False
            
        _ = self.RoleProductViewPermission.permissions
        
        if not _.has_key('values'):
            return False
        
        _ = _['values']
        

        if len( _ ) < 1:
            return False

        # return True
         
        return True
    def __get_boundary_permissions_table (self, default_permission = False):
        id = self.Role.id
        def recursive_populate(level_id, content, result):
            if not result.has_key(level_id):
                result[level_id] = {}
            # end if
            
            for obj in content:
                result[level_id][obj['id']] = obj['permission']
            
                if obj.has_key('children'):
                    recursive_populate(level_id+1, obj['children'], result)
                # end if
            # end for            
        # end def  
                  
        permission = self.RoleBoundaryViewPermission.permissions
        
        result = dict ( [ (obj.id, {}) for obj in BoundaryLevelDesc.query.all()])
        

        if permission.has_key('date_updated') and permission.has_key('values'):
            _ = permission['values']
            result['top_lvl_permission'] = _['top_lvl_permission']
            recursive_populate(1, _['boundaries'], result)
        else:
            result['top_lvl_permission'] = default_permission
        # end if
        
        return permission, result
    
    def getBoundaryPermissionsHierarchy (self, full = True , default_permission = False):
        boundary_level_max = db.session.query(func.max(BoundaryLevelDesc.id))[0][0]
        # --- recursive_populate internal function ---
        def recursive_populate(level_id, permission_table, parent_id=None):
            tmp = []
            if level_id == boundary_level_max:
                for store in list(Facility.query.filter_by(boundary_id = parent_id).order_by(Facility.id.asc()).values(Facility.id, Facility.name)):
                    permission = False
                    if permission_table[level_id].has_key(store[0]):
                        permission = permission_table[level_id][store[0]]
                        
                    tmp.append({
                        'id': store[0], 
                        'name': store[1],
                        'level': level_id,
                        'permission' : permission 
                    })
            else:
                if parent_id:
                    boundary_list = list(Boundary.query.filter_by(level_id = level_id, parent_id = parent_id).order_by(Boundary.name.asc()).values(Boundary.id, Boundary.name))
                else:
                    boundary_list = list(Boundary.query.filter_by(level_id = level_id).order_by(Boundary.name.asc()).values(Boundary.id, Boundary.name))

                for boundary in boundary_list: 
                    permission = False
                    if permission_table[level_id].has_key(boundary[0]):
                        permission = permission_table[level_id][boundary[0]]
                    tmp.append({
                        'id': boundary[0],
                        'name': boundary[1],
                        'level': level_id, 
                        'children': [],
                        'permission' : permission
                    })

                    tmp[-1]['children'] = recursive_populate(level_id + 1, permission_table, boundary.id)

            return tmp
        # --- end recursive_populate internal function ---
       
        if full:
            permissions, permission_table = self.__get_boundary_permissions_table(default_permission)
                      
            data = {
                'boundaries': recursive_populate(1, permission_table), 
                'top_lvl_desc': BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.asc()).all()[0].description,
                'facilities_lvl': BoundaryLevelDesc.query.order_by(BoundaryLevelDesc.id.desc()).all()[0].id,
                'top_lvl_permission' : permission_table['top_lvl_permission']
            }  
                
        return data

    def getBoundaryFilterHierarchy (self):
        return self.RoleBoundaryViewPermission.permissions['values']
        
    def updateBoundaryPermission (self, permission ):
        _ = { 'date_updated' : datetime.today().isoformat(), 'values' : permission }
        self.RoleBoundaryViewPermission.permissions = _
    
    
    
    def __get_products_permissions_table(self, default_permission = False):

        def recurse( content, product, product_group ):
            for obj in content:
                if obj.has_key('isLowest'):
                    product[obj['id']] = obj['permission']
                else:
                    product_group[obj['id']] = obj['permission']
                # end if
                
                if obj.has_key('children'):
                    recurse ( obj['children'], product, product_group)
                # end if
            # end for
        # end def
            
        permission = self.RoleProductViewPermission.permissions

        _p ={}
        _pg = {}
        
        for obj in ProductGroup.query.all():
            _pg[obj.id] = default_permission
        for obj in Product.query.all():
            _p[obj.id] = default_permission
        
        if permission.has_key('date_updated') and permission.has_key('values'):
            recurse ( permission['values'], _p, _pg )
            
        return _p, _pg
        
    def getProductPermissionsHierarchy(self, default_permission = False):

        def recursive_populate(p_permission, pg_permission, level_id, parent_id=None):
            tmp = []
            pgs = ProductGroup.query.filter_by(parent_id = parent_id)

            if not pgs.count():
                for pgm in ProductGroupMap.query.filter_by(group_id = parent_id):
                    product = Product.query.filter_by(id = pgm.product_id)[0];
                    
                    tmp.append({
                        'id': pgm.product_id,
                        'name': product.name,
                        'level': level_id,
                        'isLowest': True,
                        'permission' : p_permission[pgm.product_id]
                    })
            else:
                for pg in pgs:
                    tmp.append({
                        'level': level_id,
                        'id': pg.id,
                        'name': pg.description,
                        'children': recursive_populate(p_permission, pg_permission, level_id + 1, pg.id),
                        'permission' : pg_permission[pg.id]
                    })
            return tmp
        
        # --- end recursive_populate internal function ---
       
        _p_permission, _pg_permission = self.__get_products_permissions_table (default_permission)
        
        products = []
        for pg in ProductGroup.query.filter_by(parent_id = None):
            products.append({
                'level': 1,
                'id': pg.id,
                'name': pg.description,
                'children': recursive_populate(_p_permission, _pg_permission, 2, pg.id),
                'permission' : _pg_permission[pg.id]
            })
        
        return products
    
    def updateProductPermission (self, permission):
        _ = { 'date_updated' : datetime.today().isoformat(), 'values' : permission }
        self.RoleProductViewPermission.permissions = _
    
    def getProductFilterHierarchy (self):
        return self.RoleProductViewPermission.permissions['values']
        
    def __get_page_permissions_table(self, default_permission):
        permission = self.RolePageViewPermission.permissions
        
        _ = {}
        
        for p in RolePageViewPermission.__available_permission_set__:
            _[p[0]] = default_permission
        
        if permission.has_key('date_updated') and permission.has_key('values'):            
            for p in permission['values']:
                try:
                    _[p] = True
                except:
                    pass
            # end for
        return _
        

     # array context of page permission, can be used to check whether a particular permission exists.        
    class _page_view_permission_context:
            
        def __init__(self, page_permissions, permission = '', fail_func = None):
            self.permission = permission
            self.page_permissions = set ( page_permissions )
            self.fail_func = fail_func
            
        def __enter__(self):                   
            if ( self.permission == '' or not self.permission in self ) and self.fail_func:
                self.fail_func( )
            return self
            
        def __exit__(self, type, value, traceback):
            if isinstance(type, Exception):
                raise type
             
        def __getitem__(self, index):
            print 'getting item %s' & ( index, )
            if isinstance(index, Integer):
                return self.page_permisions[key]
            else:
                if index in self:
                    return index
                return None
        def __getattr__(self, item):
            return item in self.page_permissions
            
        def __contains__ (self, item):
            return item in self.page_permissions
            
        def has_permission(self, permission):
            return permission in self 

    
    def page_view_permission_context(self, permission = '', fail_func = None):
        if not hasattr(self, '_page_view_permission'):
            self._page_view_permission = dict ( [ (p, True ) for p in self.RolePageViewPermission.permissions.get('values',[]) ] ) 
     
        return RolePermission._page_view_permission_context ( self._page_view_permission, permission, fail_func)
    

    def getPagePermissionHierarchy (self, default_permission = False):
        _p_permission = self.__get_page_permissions_table(default_permission)
        
        pages = []
        
        for p in RolePageViewPermission.__available_permission_set__:
            pages.append({'id' : p[0], 'name' : p[1], 'permission' : _p_permission[p[0]]})
        
        return pages
        
    def updatePagePermission (self, permission ):
        _p = []
        for p in permission:
            _p.append(p['id'])
        # end for
        
        _ = { 'date_updated' : datetime.today().isoformat(), 'values' : _p }
        
        self.RolePageViewPermission.permissions = _
        
        self._page_view_permission = dict ( [ (p, True ) for p in self.RolePageViewPermission.permissions.get('values',[]) ] ) 
        
    def savePermission(self):
        db.session.commit()

class PermissionDoesNotExist ( Exception ):
    def __init__(self, permission_name ):
        Exception.__init__(self, 'Permission ( %s ) does not exist' % ( permission_name, ))

