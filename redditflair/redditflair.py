from flask import Blueprint, make_response, render_template, session, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redditflair.reddit as reddit
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parse_ow_profile
import config
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
def reddit_flair():
	flairdata = config.get_flairdata()

	response_params = dict()
	response_params['redditLink'] = reddit.reddit_link('flair')

	# if logged in get userObject and special flairs
	user_object = None
	specials = None
	reddit_name = session.get('redditname')
	if reddit_name is None or reddit_name == "":
		session.clear()
	else:
		user_object, specials = Database.get_user(reddit_name)

	response = make_response(
		render_template('redditflair.html', **response_params, flairdata=flairdata, user=user_object, specials=specials)
	)

	if session.get('updated'):
		session['updated'] = False

	return response


# flair verification index
@redditflair.route('/redditflair/rankverification')
def rank_verification():
	response = make_response(render_template('rankverification.html'))
	return response


# reddit oauth login
@redditflair.route('/redditflair/redditlogin', methods=['GET'])
def reddit_login():
	code = request.args.get('code', '')
	state = request.args.get('state', '')

	reddit.reddit_login(code)

	# if session redditname is set make database entry if necessary
	reddit_name = session.get('redditname')
	if reddit_name:
		user_object = User.query.filter_by(name=reddit_name).first()
		if not user_object:
			# create new entry
			new_user = User(reddit_name)
			db.session.add(new_user)
			db.session.commit()

	ret = redirect('/redditflair')
	if state == 'userverification':
		ret = redirect('/userverification')
	return ret


# blizzard oauth redirect
@redditflair.route('/redditflair/blizzardredirect', methods=['GET'])
def blizzard_redirect():
	region = request.args.get('region', '')
	return redirect(blizzard.blizzard_redirect_url(region))


# blizzard oauth login
@redditflair.route('/redditflair/blizzardlogin', methods=['GET'])
def blizzard_login():
	code = request.args.get('code', '')
	state = request.args.get('state', '')

	if state and state == 'getblizzard':
		blizzard.blizzard_login(code)

	return redirect('/redditflair/rankverification')


# parse playoverwatch profile and fetch rank
@redditflair.route('/redditflair/fetchrank', methods=['GET'])
@limiter.limit('1 per minute')
def fetch_rank():
	region = session.get('region', None)
	battletag = session.get('battletag', None)
	blizzard_id = session.get('blizzardid', None)
	platform = request.args.get('platform')
	xbl_name = request.args.get('xblname')
	psn_name = request.args.get('psnname')

	if region and battletag and blizzard_id and platform:
		rank = parse_ow_profile(battletag, blizzard_id, xbl_name, psn_name, platform)
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
			rank_int = int(rank)
			if rank_int < 1500:
				session['ranknum'] = 1
			elif rank_int < 2000:
				session['ranknum'] = 2
			elif rank_int < 2500:
				session['ranknum'] = 3
			elif rank_int < 3000:
				session['ranknum'] = 4
			elif rank_int < 3500:
				session['ranknum'] = 5
			elif rank_int < 4000:
				session['ranknum'] = 6
			else:
				session['ranknum'] = 7

			# update database entry
			redditname = session.get('redditname')
			if redditname:
				userObject = User.query.filter_by(name=redditname).first()
				if userObject:
					userObject.battletag = battletag
					userObject.blizzardid = blizzard_id
					userObject.xbl = xbl_name
					userObject.psn = psn_name
					userObject.sr = rank_int
					userObject.rank = session['ranknum']
					db.session.commit()

			session['step'] = 1
		else:
			session['rank'] = 'error'

	return redirect('/redditflair')


@redditflair.route('/redditflair/updateflair', methods=['GET'])
def update_flair():
	flairdata = config.get_flairdata()

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
