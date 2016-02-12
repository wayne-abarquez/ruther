import os, sys, config, logging
from app import config
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify,make_response
from flask.ext.login import login_user, logout_user, current_user, login_required, fresh_login_required, AnonymousUserMixin
from functools import wraps
import permissions

access_logger = logging.getLogger('audit_logs.access_logs')
access_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(config.audit_logs['access_logs'])
file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))    
file_handler.setLevel(logging.DEBUG)

access_logger.addHandler(file_handler)


def log_access (func):
    @wraps (func)
    def inner(*args, **kwargs):
        http_method = request.method
        
        user = g.user
        #print 'User <%s> accessed %s' % ( g.user.username, request.url)
        if g.user.is_authenticated():
            access_logger.info('User %s access url %s via %s method', g.user, request.url, http_method)
        else:
            access_logger.info('Anonymous user access url %s via %s method', request.url, http_method)
        return func(*args, **kwargs)
    return inner

def log_login(user):
    access_logger.info('User <%s> logged in successfully', user.username)
    
def log_logout(user):
    access_logger.info('User <%s> logged out successfully', user.username)