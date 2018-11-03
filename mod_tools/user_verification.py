from flask import Blueprint, make_response, render_template, session, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import get_flairdata
from database import db, User, Specials, Database

user_verification = Blueprint('user_verification', __name__)

# user verification
@user_verification.route('/userverification')
def userVerification():
    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('userverification')
    
    # get verified users
    verified_users = Database.get_verified_users()
    verified_users.sort(key=lambda x: x.name)
    
    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True
            
    response = make_response(render_template('userverification.html', **responseParams, mod = mod, verifiedUsers = verified_users))

    return response
    
@user_verification.route('/userverification/verify')
def userVerificationVerify():
    user = request.args.get('user', '')
    description = request.args.get('description', '')
    
    Database.set_special(user, special_id='verified', text=description)
    Database.set_user(user, flair_1='verified')
    Reddit.set_flair(user)
    
    return redirect('/userverification')
  