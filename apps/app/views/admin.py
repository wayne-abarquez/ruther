from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, lm, db 
import config
from app.models import *
from datetime import datetime, date, timedelta
import os, simplejson, time, traceback, re, HTMLParser, pprint
from sqlalchemy import *
from functools import update_wrapper
from app.auth_modules import AuthModuleFactory as auth_factory
from wrappers.permissions import RolePermission
from wrappers.audit_logs import log_access
log = app.logger

@app.route('/Roles', methods=['GET', 'POST'])
@login_required
@log_access
def Roles():
    with g.user.role_permission.page_view_permission_context ( 'view_admin', access_forbidden ):
        http_method = request.method
        
        if http_method == 'GET':
            roles = []
            for obj in Role.query.all():
            
                if obj.boundary_permission:
                    permissions = obj.boundary_permission.permissions
                    boundary_permission = permissions
                else:
                    boundary_permission = []
                    
                role = { 'id' : obj.id, 'name' : obj.name,
                'boundary_permission' : boundary_permission, 'boundary_filter_count' : 0
                }
                roles.append( role )
            # b = { obj.id : [ obj.id, obj.name, o ] for obj in Role.query.all() }

            
            return jsonify({
                'ErrorCode': 'OK',
                'ErrorMessage': 'OK', 
                'Data': roles ,
                'RequestParams' : {}})

@app.route('/Users', methods=['GET', 'POST'])
@login_required
@log_access
def Users():
    with g.user.role_permission.page_view_permission_context ( 'view_admin', access_forbidden ):
        http_method = request.method
        
        if http_method == 'GET':
            users = []
            for user in UserAccount.query.all():
                _ = { 'id' : user.id, 'username' : user.username, 'roles' : [], 'roles_txt' : ''}
                
                for ur, role in user.UserRoles:
                    _['roles'].append({'name' : role.name, 'id' : role.id})
                _['roles_txt'] = ','.join([ i['name'] for i in _['roles']])
                
                users.append(_)    

            return jsonify({
                'ErrorCode': 'OK',
                'ErrorMessage': 'OK', 
                'Data': users,
                'RequestParams' : {}})


@app.route('/RolePermissions/', methods=['GET', 'POST'])
@login_required
@log_access
def RolePermissions():
    with g.user.role_permission.page_view_permission_context ( 'view_admin', access_forbidden ):
        http_method = request.method
        
        if http_method == 'GET':
            role_id = request.args.get('role_id','')
            if not role_id:
                return jsonify({ 'ErrorCode': 'ERROR',
                    'ErrorMessage': 'No role id specified in request parameters', 
                    'Data' : {},
                    'RequestParams' : {'role_id' : role_id}
                    })
                    
            _r = RolePermission (role_id)
            boundary_permissions_hierarchy = _r.getBoundaryPermissionsHierarchy()
            product_permissions_hierarchy = _r.getProductPermissionsHierarchy()
            page_permissions_hierarchy = _r.getPagePermissionHierarchy()
            
            data = { 'products' : product_permissions_hierarchy, 'boundary' : boundary_permissions_hierarchy, 'pages' : page_permissions_hierarchy }
            
            return jsonify({ 'ErrorCode': 'OK',
                'ErrorMessage': 'OK', 
                'Data' : data,
                'RequestParams' : {'role_id' : role_id}
                })
        
        elif http_method == 'POST':
            data = request.json
            print data
            
            permissions = data['boundary_permissions']
            role_id = data['role_id']
            
            if not role_id:
                return jsonify({ 'ErrorCode': 'ERROR',
                    'ErrorMessage': 'No role id specified in request parameters', 
                    'Data' : {},
                    'RequestParams' : {'role_id' : role_id}
                    })
                    
            _r = RolePermission (role_id)

            _r.updateBoundaryPermission ( data['boundary_permissions'] )
            _r.updateProductPermission ( data['product_permissions'] )
            _r.updatePagePermission( data['page_permissions'] )
            _r.savePermission()
            
            return jsonify({
                'ErrorCode': 'OK',
                'ErrorMessage': 'OK', 
                'Data' : '',
                'RequestParams' : {'role_id' : role_id, 'permissions' : permissions}
                }) 
@app.route('/LDAPSync', methods=['GET', 'POST'])
@login_required
@log_access
def LDAPSync():
    with g.user.role_permission.page_view_permission_context ( 'view_admin', access_forbidden ):
        http_method = request.method

        if http_method == 'GET':
            error, _ = auth_factory.getList('ruther_ldap')
            
            roles = [{'rolename' : i['RoleName'] } for i in _]
            
            _users = {}
            
            for role in _:
                for member in role['Members']:
                    if _users.has_key(member['uid']):
                        _users[member['uid']]['roles'].append(role)
                    else:
                        _users[member['uid']] =  { 'member' : member, 'roles' : [ role ] }
                # end for
            # end for
           
            b = [ { 'roles' : obj} for obj in _ ] 
            
            new_roles, defunct_roles = check_roles_changes(roles)
            new_users, defunct_users, changed = check_user_changes(_users)
            
            return jsonify({
                'ErrorCode': 'OK',
                'ErrorMessage': 'OK', 
                'Data': {'need_sync' :  ( len(new_roles) > 0 ) or ( len(defunct_roles) > 0 ) or ( len (new_users) > 0 ) or ( len (defunct_users) ) or ( len (changed) > 0), 
                    'new_roles' : new_roles, 'defunct_roles' : defunct_roles, 
                    'new_users' : new_users, 'defunct_users' : defunct_users,
                    'changed' : changed,
                    'roles' : roles, 'users' : [ obj for key, obj in _users.items()]} ,
                'RequestParams' : {}})            
        # end if
        
        if http_method == 'POST':
            data = request.json

            new_roles = data['new_roles'] #request.args.get['new_roles']
            defunct_roles = data['defunct_roles'] #request.args.get('defunct_roles')
            new_users = data['new_users']
            defunct_users = data['defunct_users']
            changed_userroles = data['changed']
            ret = confirm_changes(new_roles, defunct_roles, new_users, defunct_users, changed_userroles)
            
            return jsonify({
                'ErrorCode': 'OK' if ret == 1 else 'ERROR',
                'ErrorMessage': 'OK' if ret == 1 else 'ERROR', 
                'Data': {                 
                    'new_roles' : new_roles, 'defunct_roles' : defunct_roles, 
                    'new_users' : new_users, 'defunct_users' : defunct_users,
                    'changed' : changed_userroles, },
                'RequestParams' : {}})       

def check_roles_changes(roles):
    master_list = set([ r['rolename'] for r in roles ]) 
    db_list = set ( [ r.name for r in Role.query.all() ] )
    intersected = master_list.intersection(db_list)

    new_roles = []
    for r in master_list:
        if not ( r in intersected) :
            new_roles.append(r)
        # end if
    # # end for

    deleted_roles = []
    for r in db_list:
        if not (r in intersected):
            if r != 'Administrator':
                deleted_roles.append(r)
            
        # end if
    # end for

    return new_roles, deleted_roles    

def check_user_changes(users):
    master_list = set( [ ( u['member']['uid'] + '@' + config.ldap['base_pretty'] ).lower() for u in users.values()  ] )
    db_list = set ( [ u.username.lower() for u in UserAccount.query.filter_by(auth_module_name='ruther_ldap')] )
    intersected = db_list.intersection(master_list)

    # check for new users
    new_users = []
    for r in master_list:
        if not ( r in intersected) :
            roles = users[r.split('@')[0]]['roles']
            roles = [ role['RoleName'] for role in roles ]
            new_users.append({'username' : r, 'roles' : roles, 'roles_txt' : ','.join(roles) } )
        # end if
    
    # check for deleted users
    deleted_users = []
    for r in db_list:
        if not (r in intersected):
            deleted_users.append(r)
        # end if
    # end for

    
    # check for user whose roles has changed.
    current = {}
    for user in UserAccount.query.filter(UserAccount.username.in_(intersected)):
        current[user.username.lower()] = set()
        for obj in user.UserRoles:
            user_role, role = obj
            if current.has_key(user.username.lower()):
                current[user.username.lower()].add(role.name)
            else:
                current[user.username.lower()] = set ( [role.name] )
            # end if
        # end for
    # end for
    
    master = {}
    for u in users.values():
        username = ( u['member']['uid'] + '@' + config.ldap['base_pretty'] ).lower()
        master[username] = set()
        for role in u['roles']:
            if master.has_key(username):
                master[username].add ( role['RoleName'] )
            else:
                master[username] = set ( [role['RoleName']])

    
    changed = [ ]
    for user, user_role_set in current.items():
        if master.has_key(user):
            if not ( master[user].issubset(user_role_set) and user_role_set.issubset(master[user])):
                new_roles =  list(master[user])
                old_roles = list(current[user])
                changed.append({'username' : user, 'new_roles' :new_roles, 'old_roles' : old_roles, 'new_roles_txt' : ','.join(new_roles), 'old_roles_txt' : ','.join(old_roles)})
                
    return new_users, deleted_users, changed

def confirm_changes(new_roles, deleted_roles, new_users, deleted_users, userrole_changes):
    log = app.logger
    try:
        # add Role
        new_roles_count = len(new_roles)
        defunct_roles_count = len (deleted_roles)
        new_users_count = len(new_users)
        defunct_users_count = len(deleted_users)
        userrole_changes_count = len (userrole_changes)
        
        if new_roles_count > 0:
            for r in new_roles:
                _ = Role()
                _.name = r
                db.session.add(_)
            # end for
            db.session.commit()
            
            for role in Role.query.filter(Role.name.in_ ( new_roles ) ):
                _ = RoleBoundaryViewPermission ()
                _.role_id = role.id
                db.session.add(_)
                
                _ = RoleProductViewPermission ()
                _.role_id = role.id
                db.session.add(_)
                
                _ = RolePageViewPermission()
                _.role_id = role.id
                db.session.add(_)
            db.session.commit()
        # end if
        
        if defunct_roles_count > 0:
            for r in Role.query.filter(Role.name.in_(deleted_roles)):
                _q = RoleBoundaryViewPermission.query.filter_by(role_id = role.id).all()
                
                for _obj in _q:
                    db.session.delete(_obj)
                
                _q = RoleProductViewPermission.query.filter_by(role_id = role.id).all()
                
                for _obj in _q:
                    db.session.delete(_obj)
                    
                _q = RolePageViewPermission.query.filter_by(role_id = role.id).all()
                
                for _obj in _q:
                    db.session.delete(_obj)
 
                db.session.delete(r)
            # end for
            db.session.commit()
        # end if
        
        # users
        if new_users_count > 0:
            for u in new_users:
                _ = UserAccount ()
                _.username = u['username'].lower()
                _.account_status = AccountStatusType.ACTIVE
                _.auth_module_name = 'ruther_ldap'
                _.account_create_time = datetime.now()
                db.session.add(_)
            # end for
        # end if
             
        if defunct_users_count > 0:
            for u in UserAccount.query.filter(UserAccount.username.in_(deleted_users)):
                db.session.delete(u)
            # end for
        # end if

        if new_users_count > 0 or defunct_users_count > 0:
            db.session.commit()
        # end if
        
        # new user's roles
        if new_users_count > 0:
            for u in new_users:
                user = UserAccount.query.filter(UserAccount.username == u['username'])[0]
                for role in Role.query.filter(Role.name.in_(u['roles'])):
                    _ = UserRole()
                    _.user_id = user.id
                    _.role_id = role.id
                    db.session.add(_)
                # end for
            # end for
            db.session.commit()
        #end if

        # user role changes        
        if userrole_changes_count:
            for ur in userrole_changes:
                user = UserAccount.query.filter(UserAccount.username == ur['username'].lower())[0]
                for d_ur in UserRole.query.filter(UserRole.user_id == user.id):
                    db.session.delete(d_ur)
                # end for
                
                for role in Role.query.filter(Role.name.in_(ur['new_roles'])):
                    _ = UserRole()
                    _.user_id = user.id
                    _.role_id = role.id
                    db.session.add(_)
                 # end for
            # end for
            
            db.session.commit()
        # end if
        
        return 1
    except Exception, ex:
        log.error("Fatal Exception: %s", ex)
        log.error(traceback.format_exc())
        return -1
        
    
@app.route('/admin', methods=['GET', 'POST'])
@login_required
@log_access
def admin():
    with g.user.role_permission.page_view_permission_context ( 'view_admin', access_forbidden ):
        return render_template('/admin.html', user = g.user)
    
    
def access_forbidden():
    abort (403)
        
    