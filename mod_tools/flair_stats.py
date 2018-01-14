from flask import Blueprint, make_response, render_template, session, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import flairdata
from database import db, User, Specials, Database

flair_stats = Blueprint('flair_stats', __name__)

COW_TEAMS = ['boston-uprising', 'dallas-fuel', 'florida-mayhem', 'houston-outlaws', 'london-spitfire', 'los-angeles-gladiators', 'los-angeles-valiant', 'new-york-excelsior', 'philadelphia-fusion', 'san-francisco-shock', 'seoul-dynasty', 'shanghai-dragons']

# user verification
@flair_stats.route('/flairstats')
def flairStats():
    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairstats')
    
    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True
    else:
        return redirect('/redditflair')
    
    ret = '<table><tr><th>Team</th><th>Total</th><th>Primary</th><th>Secondary</th></tr>'
    for team in COW_TEAMS:
        primary = len(User.query.filter_by(flair1=team).all())
        secondary = len(User.query.filter_by(flair2=team).all())
        total = primary + secondary
        
        ret += '<tr><td>' + flairdata['flairs'][team]['name'] + '</td><td>' + str(total) + '</td><td>' + str(primary) + '</td><td>' + str(secondary) + '</td></tr>'
    ret += '</table>'
    
    
    
    #response = make_response(render_template('userverification.html', **responseParams, mod = mod, verifiedUsers = verified_users))

    return ret
    
