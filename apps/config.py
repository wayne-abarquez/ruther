import os
import socket

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# OPENID_PROVIDERS = [
    # { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    # { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    # { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    # { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    # { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

basedir = os.path.abspath(os.path.dirname(__file__))

#if socket.gethostname() == 'jhalley':
#    SQLALCHEMY_DATABASE_URI = 'postgresql://ruther:m0ther@localhost:5432/ruther' #'sqlite:///' + os.path.join(basedir, 'app.db')
#else:
#    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost:5432/ruther' #'sqlite:///' + os.path.join(basedir, 'app.db')
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost:5432/ruther' #'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'postgresql://ruther:m0ther@localhost:5432/ruther'  # 'sqlite:///' + os.path.join(basedir, 'app.db')

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
log_fileout = '/var/www/ruther/logs/ruther_logs'
STORE_TYPE_ID = 1

ldap = { 
'base':'dc=Navagis,dc=local',
'base_pretty' : 'Navagis.local',
'user_ou' : 'People',
'manager_cn' : 'Manager',
'manager_secret' : 'navagis',
'roles_ou': 'Ruther',
'roles_filter' : '(objectClass=groupOfNames)',
'host' : 'ldaps://localhost'
 }

 
#audit_logs = {'access_logs': '/home/jhalley/coding/Navagis/ruther_logs/log' if socket.gethostname() == 'jhalley' else '/home/yp/Workspace/ruther/access_logs'}
audit_logs = {'access_logs': '/var/www/ruther/logs/access_logs'}
session_timeout = 3000000000


login_attempt_timeout = 300
login_attempt_retries = 5
