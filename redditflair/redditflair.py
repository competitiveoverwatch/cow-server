from flask import Blueprint, make_response, render_template, session, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redditflair.reddit as reddit
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import set_flairdata, get_flairdata
from database import db, User, Specials, Database

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['60/minute']
)

redditflair = Blueprint('redditflair', __name__)

# root route
@redditflair.route('/')
def root():
    return redirect('/redditflair')

# main route
@redditflair.route('/redditflair')
def redditFlair():
    flairdata = get_flairdata()

    responseParams = dict()
    responseParams['redditLink'] = reddit.redditLink('flair')
    
    # if logged in get userObject and special flairs
    userObject = None
    specials = None
    redditname = session.get('redditname')
    if redditname is None or redditname == "":
        session.clear()
    else:
        userObject, specials = Database.get_user(redditname)
 
    response = make_response(render_template('redditflair.html', **responseParams, flairdata=flairdata, user=userObject, specials=specials))
    
    if session.get('updated'):
        session['updated'] = False
    
    return response

# flair verification index
@redditflair.route('/redditflair/rankverification')
def rankVerification():
    response = make_response(render_template('rankverification.html'))
    return response

# reddit oauth login
@redditflair.route('/redditflair/redditlogin', methods=['GET'])
def redditLogin():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    
    reddit.redditLogin(code)
        
    # if session redditname is set make database entry if necessary
    redditname = session.get('redditname')
    if redditname:
        userObject = User.query.filter_by(name=redditname).first()
        if not userObject:
            # create new entry
            newUser = User(redditname)
            db.session.add(newUser)
            db.session.commit()
    
    ret = redirect('/redditflair')
    if state == 'userverification':
        ret = redirect('/userverification')
    return ret
    

    
# blizzard oauth redirect
@redditflair.route('/redditflair/blizzardredirect', methods=['GET'])
def blizzardRedirect():
    region = request.args.get('region', '')
    return redirect(blizzard.blizzardRedirectURL(region))
    
# blizzard oauth login
@redditflair.route('/redditflair/blizzardlogin', methods=['GET'])
def blizzardLogin():
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    
    if state and state == 'getblizzard':
        blizzard.blizzardLogin(code)
            
    return redirect('/redditflair/rankverification')
    
    

# parse playoverwatch profile and fetch rank
@redditflair.route('/redditflair/fetchrank', methods=['GET'])
@limiter.limit('1 per minute')
def fetchRank():
    region = session.get('region', None)
    battletag = session.get('battletag', None)
    blizzardid = session.get('blizzardid', None)
    platform = request.args.get('platform')
    xblname = request.args.get('xblname')
    psnname = request.args.get('psnname')
        
    if region and battletag and blizzardid and platform:
        rank = parseOWProfile(battletag, blizzardid, xblname, psnname, platform)
        if rank:
            session['rank'] = rank
            
            # platform
            session['platform'] = platform  
            if platform == 'pc':
                session['platform'] = 'PC'
            elif platform == 'xbl':
                session['platform'] = 'PS4'
            elif platform == 'psn':
                session['platform'] = 'Xbox'
                
            # rank number
            rankint = int(rank)
            if rankint < 1500:
                session['ranknum'] = 1
            elif rankint < 2000:
                session['ranknum'] = 2
            elif rankint < 2500:
                session['ranknum'] = 3
            elif rankint < 3000:
                session['ranknum'] = 4
            elif rankint < 3500:
                session['ranknum'] = 5
            elif rankint < 4000:
                session['ranknum'] = 6
            else:
                session['ranknum'] = 7
                
            # update database entry
            redditname = session.get('redditname')
            if redditname:
                userObject = User.query.filter_by(name=redditname).first()
                if userObject:
                    userObject.battletag = battletag
                    userObject.blizzardid = blizzardid
                    userObject.xbl = xblname
                    userObject.psn = psnname
                    userObject.sr = rankint
                    userObject.rank = session['ranknum']
                    db.session.commit()
                    
            session['step'] = 1
        else:
            session['rank'] = 'error'
            
    return redirect('/redditflair')
    
    
    
@redditflair.route('/redditflair/updateflair', methods=['GET'])
def updateFlair():
    flairdata = get_flairdata()
    
    flair_1 = request.args.get('flair1_id', None)
    flair_2 = request.args.get('flair2_id', None)
    custom_text = request.args.get('customflairtext', '')
    display_sr = request.args.get('displaysr', None)
    try:
        # check flair consistency
        if flair_1 == flair_2: 
            flair_2 = None
        if (flair_1 and flair_1 not in flairdata['flairs']) or (flair_2 and flair_2 not in flairdata['flairs']):
            raise Exception('Unknown flair ID')
        redditname = session.get('redditname')
        Database.set_user(redditname, flair_1=flair_1, flair_2=flair_2, flair_text=custom_text)
        Reddit.set_flair(redditname, display_sr)    
        session['updated'] = True 
    except:
        pass
        
    return redirect('/redditflair')

@redditflair.errorhandler(429)
def ratelimit_handler(e):
    session['rateexceed'] = True
    return redirect('/redditflair/rankverification')
