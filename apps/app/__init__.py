from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
# from flask.ext.openid import OpenID
from config import basedir
import config
import os, logging, sys


# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from models.base import Base


app = Flask(__name__)
app.config.from_object('config')
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)

lm = LoginManager(app)
lm.login_view = 'login'
# lm.setup_app(app)
# oid = OpenID(app, os.path.join(basedir, 'tmp'))
# lm.login_view = 'login'

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))
stdout_handler.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(stdout_handler)
if config.log_fileout:
    file_handler = logging.FileHandler(config.log_fileout)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(filename)s %(funcName)s: %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os

    app.wsgi_app = SharedDataMiddleware(app.wsgi_app,
                                        {
                                            '/resources': os.path.join(os.path.dirname(__file__), 'static',
                                                                       'resources'),
                                            '/tutorial': os.path.join(os.path.dirname(__file__), 'static', 'html'),
                                            '/js': os.path.join(os.path.dirname(__file__), 'templates', 'js'),
                                            '/css': os.path.join(os.path.dirname(__file__), 'templates', 'css')
                                            # '/templates/js' : os.path.join(os.path.dirname(__file__), 'templates','js')
                                        })
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)

from app.views import *
from models import *
from auth_modules import AuthModuleFactory

AuthModuleFactory.init(os.path.join(config.basedir, 'app', 'auth_modules'))

app.permanent_session_lifetime = timedelta(seconds=config.session_timeout)
app.secret_key = os.urandom(24)
# from models import *


# engine = create_engine(config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
# db_session = scoped_session(sessionmaker(autocommit=False,
# autoflush=False,
# bind=engine))

# Base.query = db_session.query_property()

# def init_db():
# # import all modules here that might define models so that
# # they will be registered properly on the metadata.  Otherwise
# # you will have to import them first before calling init_db()
# Base.metadata.create_all(bind=engine)

print "running from init.. Done loading app"
