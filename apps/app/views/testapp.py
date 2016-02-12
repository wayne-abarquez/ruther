

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
# from flask.ext.login import login_user, logout_user, current_user, login_required
# from flask.ext.babel import gettext
from app import app #, db, lm, oid, babel
# from forms import LoginForm, EditForm, PostForm, SearchForm
# from models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime
# from emails import follower_notification
# from guess_language import guessLanguage
# from translate import microsoft_translate
# from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, LANGUAGES

@app.route('/testapp/index', methods=['GET', 'POST'])
def testapp():
	return render_template('/testapp/index.html')
	
@app.route('/test', methods=['GET','POST'])
def test():
	return 12345
	
@app.route('/testapp/Locations', methods=['GET','POST'])
def Locations():

	return jsonify({"locations" : [
		{ "name" : "Test",
		  "phys_address " : "Nowhere",
		  "longitude" : 0,
		  "latitude" : 0,
		  "description" : "first entry" },
	]})