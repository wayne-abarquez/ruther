import os, imp, zlib, base64, simplejson
from app import db, app, config
from app.auth_modules import AuthModuleFactory as auth_factory
from sqlalchemy import *
from sqlalchemy.orm import *
    



class AccountStatusType:
    ACTIVE = 1
    SUSPENDED = 0
class TemporaryLockoutStatus:
    LOCKED = 1
    UNLOCKED = 0
class UserAccount(db.Model):
    
    __tablename__ = 'ruther_user'
    id = Column(Integer, primary_key = True)
    username = Column (String)
    password = Column (String)
    account_status = Column (Integer)
    auth_module_name = Column (String)
    
    last_login_datetime = Column(DateTime)
    last_access_datetime = Column(DateTime)
    account_create_time = Column(DateTime)
    
    temporary_login_lockout = Column (Integer, default = TemporaryLockoutStatus.UNLOCKED)
    
    
    def authenticate (self, passwd):
        return auth_factory.Authenticate(self.auth_module_name, user = self, password=passwd)

    @property
    def UserRoles(self):
        return UserRole.query.outerjoin(Role, Role.id == UserRole.role_id).filter(UserRole.user_id == self.id).add_entity(Role).all()

class UserRole (db.Model):
    __tablename__ = 'ruther_user_role'
   
    user_id = Column (Integer, primary_key = True)
    role_id = Column (Integer, primary_key = True)
    
class Role(db.Model):
    __tablename__ = 'ruther_role'
    
    id = Column(Integer, primary_key = True)
    name = Column(String)
    
    boundary_permission = relationship("RoleBoundaryViewPermission", uselist=False, backref="ruther_role") 
    page_permission = relationship("RolePageViewPermission", uselist=False, backref="ruther_role")
    product_permission = relationship("RoleProductViewPermission", uselist=False, backref="ruther_role")
    
    def __repr__(self):
        return '<role %r>' % (self.name)
   
   
   
class RolePageViewPermission(db.Model):
    __tablename__ = 'ruther_role_pageview_permissions'
    __available_permission_set__ =  set ( [ ('view_admin', 'Administration') ])
    
    AvailablePermission = dict ( [ ( s, True ) for s in __available_permission_set__])
    
    id = Column(Integer, primary_key = True)
    role_id = Column(Integer, ForeignKey('ruther_role.id')) 
    
    permissions_raw = Column(String)
    
    @property
    def permissions(self):
        if not hasattr(self, '_permissions'):
            if self.permissions_raw:
                self._permissions = simplejson.loads(zlib.decompress(base64.b64decode(self.permissions_raw)))
            else:
                self._permissions = {}
        
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        self._permissions = permissions
        self.permissions_raw = base64.b64encode(zlib.compress(simplejson.dumps(self._permissions)))
        
    
    
class RoleBoundaryViewPermission(db.Model):
    __tablename__ = 'ruther_role_boundaryview_permissions'
    
    id = Column(Integer, primary_key = True)
    role_id = Column(Integer, ForeignKey('ruther_role.id')) 
    
    permissions_raw = Column(String)
    
    
    @property
    def permissions(self):
        if not hasattr(self, '_permissions'):
            if self.permissions_raw:
                self._permissions = simplejson.loads(zlib.decompress(base64.b64decode(self.permissions_raw)))
            else:
                self._permissions = {}
        
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        self._permissions = permissions
        self.permissions_raw = base64.b64encode(zlib.compress(simplejson.dumps(self._permissions)))
    
"""
    product_group { id: [ parent_id, view_permissions ] }
    products { id : [ group_id, view_permissions ]  }
"""
class RoleProductViewPermission(db.Model):
    __tablename__ = 'ruther_role_productview_permissions'
    
    id = Column(Integer, primary_key = True)
    role_id = Column(Integer, ForeignKey('ruther_role.id')) 
    
    permissions_raw = Column(String)
    
    @property
    def permissions(self):
        if not hasattr(self, '_permissions'):
            if self.permissions_raw:
                self._permissions = simplejson.loads(zlib.decompress(base64.b64decode(self.permissions_raw)))
            else:
                self._permissions = {}
        
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        self._permissions = permissions
        self.permissions_raw = base64.b64encode(zlib.compress(simplejson.dumps(self._permissions)))