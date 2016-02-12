from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
import pprint
from app import app, lm, db 
import config
from app.models import *
from datetime import datetime, date, timedelta
import os, simplejson, time
import re
import HTMLParser
from sqlalchemy import *
from wtforms import TextField, BooleanField, PasswordField
from wtforms.validators import Required
from flask_wtf import Form
# from flask.ext.wtf import Required
from wrappers.permissions import RolePermission, AuthenticatedUser
from wrappers.audit_logs import log_login, log_logout, log_access
log = app.logger
PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)

class LoginForm(Form):
    username = TextField('username', validators = [Required(message="Please enter your username")])
    password = PasswordField('password', validators = [Required(message="Please enter your password")])
    # remember_me = BooleanField('remember_me', default = False)
    
@lm.user_loader
def load_user(id):
    # return UserAccount.query.get(int(id))
    return AuthenticatedUser(id)

@app.route('/login', methods = ['GET', 'POST'])
@log_access
def login():
    log.debug("login page")
    # login can only done by doing  a full round server post not via ajax
    # so if it is ajax, we know that client is trying to get data that is not authorized
    # client will have to redirect to the request.path.
    if request.is_xhr:
        return jsonify({
            'ErrorCode': 'A010101',
            'ErrorMessage': 'No Authorization to access', 
            'Data': { 'redirect_url' : request.path } ,
            'RequestParams' : ''
        })
    
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        q = UserAccount.query.filter_by(username=form.username.data.lower()).all()
        
        if len(q) > 0:
            user = q[0]
            if not can_attempt_login(user):
                flash ("You have exceeded your maximum retries. Please wait for a while before continuing.")
                return redirect(url_for("login"))
            
            
            # login_user(user, remember = form.remember_me.data)
            error, result = user.authenticate(form.password.data)
            if result:
                auth_user = AuthenticatedUser(user.id)
                # _ = LoginAttempt(username = user.username, ip_address = request.remote_addr, attempt_datetime = datetime.now(), status = LoginAttemptStatus.SUCCESS)
                
                # db.session.add(_)
                # db.session.commit()
                insert_login_attempt(user.username, request.remote_addr, datetime.now(), LoginAttemptStatus.SUCCESS)
                if auth_user.role_permission is None or auth_user.role_permission.validate() == False:
                    flash ("Your user account's permissions have not been properly configured. Please contact your administrator.")
                    return redirect(url_for("login"))               

                auth_user.update_last_login_time(True)

                login_user(auth_user)
                log_login(auth_user)
                session.permanent = True
                return redirect(url_for("index"))
            
            else:
                flash ("Login credentials invalid. Please ensure you have entered the correct combination of username/password.")
                # _ = LoginAttempt(username = user.username, ip_address = request.remote_addr, attempt_datetime = datetime.now(), status = LoginAttemptStatus.FAILS)
                # db.session.add(_)
                # db.session.commit()
                insert_login_attempt(user.username, request.remote_addr, datetime.now(), LoginAttemptStatus.FAILS)
                return redirect(url_for("login"))
      
        else:
            flash ("Login credentials invalid. Please ensure you have entered the correct combination of username/password.")
            return redirect(url_for("login"))
    
    return render_template('/login.html', 
        title = 'Sign In',
        form = form)    

# sadly the only way to work with the partitioning.
# using ORM to insert will not work.
def insert_login_attempt ( username, ip_address, attempt_datetime, status ):
    sql = ''' INSERT into ruther_audit_login_attempt ( username, ip_address, attempt_datetime, status ) VALUES ( :username, :ip, :attempt_datetime, :status ) '''    
    db.session.execute(sql, {'username' : username, 'ip' : ip_address, 'attempt_datetime' : attempt_datetime, 'status' : status })
    db.session.commit()
        
def can_attempt_login(user):
    now = datetime.now()
    failed_login_attempt_count = 0 
    for obj in LoginAttempt.query.filter(LoginAttempt.username == user.username, LoginAttempt.attempt_datetime <= now, LoginAttempt.attempt_datetime >= (now - timedelta(seconds = config.login_attempt_timeout) ) ).order_by(LoginAttempt.attempt_datetime.asc()):
        if obj.status == LoginAttemptStatus.FAILS:
            failed_login_attempt_count += 1
        else:
            failed_login_attempt_count = 0
        # end if
    # end for
    print 'fail count %s' % ( failed_login_attempt_count, )
    if user.temporary_login_lockout == TemporaryLockoutStatus.LOCKED and failed_login_attempt_count > 1:
        return False
    elif user.temporary_login_lockout == TemporaryLockoutStatus.LOCKED and failed_login_attempt_count == 0:
        user.temporary_login_lockout = TemporaryLockoutStatus.UNLOCKED
        db.session.commit()
        return True
    elif user.temporary_login_lockout == TemporaryLockoutStatus.UNLOCKED and failed_login_attempt_count >= config.login_attempt_retries:
        user.temporary_login_lockout = TemporaryLockoutStatus.LOCKED
        db.session.commit()
        return False
    
    return True
    
@app.route("/logout")
@login_required
@log_access
def logout():
    log.debug('logging out')
    user = g.user
    log_logout(user)
    logout_user()

    g.user = None
    g.role = None
    session["__invalidate__"] = True
    return redirect(url_for("login"))

@lm.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))
    
@app.before_request
def before_request():
    if current_user.is_authenticated():
        current_user.update_last_access_time(True)
        g.user = current_user
        
    else:
        g.user = current_user
        g.role = None
        g.role_permission = None
    
@app.after_request
def remove_if_invalid(response):
    if "__invalidate__" in session:
        response.delete_cookie(app.session_cookie_name)
    return response