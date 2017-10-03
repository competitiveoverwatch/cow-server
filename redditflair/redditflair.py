from flask import Blueprint, make_response, render_template, session, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redditflair.reddit as reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import flairdata

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

redditflair = Blueprint('redditflair', __name__)




# main route
@redditflair.route("/redditflair")
def redditFlair():
	responseParams = dict()
	responseParams['redditLink'] = reddit.redditLink()

	response = make_response(render_template('redditflair.html', **responseParams, flairdata=flairdata))
	return response



# flair verification index
@redditflair.route("/redditflair/rankverification")
def rankVerification():
	responseParams = dict()
	responseParams['redditLink'] = reddit.redditLink()
		
	response = make_response(render_template('rankverification.html', **responseParams))
	
	if session.get('updated'):
		session['step'] = 1
		
	return response

# reddit oauth login
@redditflair.route("/redditflair/redditlogin", methods=['GET'])
def redditLogin():
	code = request.args.get('code', '')
	state = request.args.get('state', '')
	
	if state and state == 'getreddit':
		reddit.redditLogin(code)
	
	return redirect('/redditflair')
	

# blizzard oauth redirect
@redditflair.route("/redditflair/blizzardredirect", methods=['GET'])
def blizzardRedirect():
	region = request.args.get('region', '')
	return redirect(blizzard.blizzardRedirectURL(region))
	
# blizzard oauth login
@redditflair.route("/redditflair/blizzardlogin", methods=['GET'])
def blizzardLogin():
	code = request.args.get('code', '')
	state = request.args.get('state', '')
	
	if state and state == 'getblizzard':
		blizzard.blizzardLogin(code)
			
	return redirect('/redditflair/rankverification')
	

# parse playoverwatch profile and fetch rank
@redditflair.route("/redditflair/fetchrank", methods=['GET'])
@limiter.limit("1 per minute")
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
			session['step'] = 4
			
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
			
		else:
			session['rank'] = "error"
			
	return redirect('/redditflair/rankverification')
	
	
	
@redditflair.route("/redditflair/updateflair", methods=['GET'])
def updateFlair():
	customtext = request.args.get('customflairtext', '')
	customrank = request.args.get('rank', None)
	
	reddit.redditUpdateFlair(customrank, customtext)

	return redirect('/redditflair/rankverification')

@redditflair.errorhandler(429)
def ratelimit_handler(e):
	session['rateexceed'] = True
	return redirect('/redditflair/rankverification')