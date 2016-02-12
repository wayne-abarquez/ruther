import os, sys, logging, datetime, time, random, simplejson, argparse

sys.path.append('../')

from app import db
from app.models import *

if __name__ == '__main__':
    r = Role()
    
    r.name = 'Administrator'
    
    # _allowed_b_level = []
    # _allowed_b = []
    # for b in BoundaryLevelDesc.query.all():
        # _allowed_b_level.append(b.id)
    # for b in Boundary.query.all():
        
        # _allowed_b.append( ( b.level_id, b.parent_id, b.id ) )
    
    # r.allowed_boundaries = {'BoundaryLevel' : _allowed_b_level, 'Boundaries' : _allowed_b}
    
    
    # _allowed_pg, _allowed_pg_map, _allowed_p = [], [], []
    # for pg in ProductGroup.query.all():
        # _allowed_pg.append((pg.parent_id, pg.id))
    
    # for pg_map in ProductGroupMap.query.all():
        # _allowed_pg_map.append((pg_map.group_id, pg_map.product_id))
    
    # for p in Product.query.all():
        # _allowed_p.append( (p.id) )
    
    # r.allowed_products = { 'ProductGroup' : _allowed_pg, 'ProductGroupMap' : _allowed_pg_map, 'Product' : _allowed_p }
    
    db.session.add(r)
    db.session.commit()
    
    u = UserAccount()
    u.username = 'localuser'
    u.account_status = AccountStatusType.ACTIVE
    u.password = 'localuser'
    # u.allowed_boundaries = r.allowed_boundaries
    # u.allowed_products = r.allowed_products
    # u.role_id = r.id
    u.auth_module_name = 'ruther_local'
    db.session.add(u)
    db.session.commit()

    ur = UserRole()
    ur.role_id = r.id
    ur.user_id = u.id
    db.session.add(ur)
    db.session.commit()
    
    # u = UserAccount()
    # u.username = 'ldapuser'
    # u.account_status = AccountStatusType.ACTIVE
    # u.password = 'ldapuser'
    # u.allowed_boundaries = r.allowed_boundaries
    # u.allowed_products = r.allowed_products
    # u.role_id = r.id
    # u.auth_module_name = 'ldap'
    # db.session.add(u)
    # db.session.commit()
    