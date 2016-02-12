import os, imp, zlib, base64, simplejson
from app import db, app, config
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.dialects import postgresql

class LoginAttemptStatus:
    SUCCESS = 1
    FAILS = 0
    
class LoginAttempt(db.Model):
    
    __tablename__ = 'ruther_audit_login_attempt'
    id = Column(Integer, primary_key = True)
    username = Column (String)
    
    attempt_datetime = Column(DateTime)
    status = Column( Integer )

    ip_address = Column( postgresql.INET )
    



        