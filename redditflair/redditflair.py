from flask import Blueprint, make_response, render_template, session, redirect, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redditflair.reddit as reddit
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parse_ow_profile
from config import data as config_data
from database import db, User, Flair, Database
import prawcore

limiter = Limiter(
	key_func=get_remote_address,
	default_limits=['60/minute']
)

redditflair = Blueprint('redditflair', __name__)


@redditflair.before_request
def check_for_maintenance():
	if config_data['config']['maintenanceMode'] == 1 and request.path != '/maintenance' and 'static' not in request.path:
		return redirect('/maintenance')


# root route
@redditflair.route('/maintenance')
def maintenance():
	return make_response(render_template('maintenance.html'))


# root route
@redditflair.route('/')
def root():
	return redirect('/redditflair')


# main route
@redditflair.route('/redditflair')
def reddit_flair():
	response_params = dict()
	response_params['redditLink'] = reddit.reddit_link('flair')

	# if logged in get userObject and special flairs
	user_object = None
	reddit_name = session.get('redditname')
	if reddit_name is None or reddit_name == "":
		session.clear()
	else:
		user_object = Database.get_or_add_user(reddit_name)

	flairs = {}
	for flair in Database.get_all_flair():
		flairs[flair.short_name] = flair

	categories = Database.get_flair_by_category()

	response = make_response(
		render_template(
			'redditflair.html', **response_params, flairs=flairs, categories=categories, user=user_object,
			ranks=config_data['config']['ranks'], category_names=config_data['config']['categories'],
			subreddit=config_data['config']['subreddit'])
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

	try:
		reddit.reddit_login(code)
	except prawcore.exceptions.ResponseException as err:
		if err.response.status_code == 404:
			current_app.logger.info(f"Error logging into reddit with code: {code} : {state} : {err}")
			return redirect('/redditflair')
		else:
			current_app.logger.warning(f"Error logging into reddit with code: {code} : {state} : {err}")
			raise

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
		blizzard.blizzard_login(code, current_app.logger)

	if session.get('battletag', None) == "error try again":
		return redirect('/redditflair/rankverification')

	redditname = session.get('redditname')
	if redditname:
		userObject = User.query.filter_by(name=redditname).first()
		if userObject:
			userObject.battletag = session.get('battletag', None)
			userObject.blizzardid = session.get('blizzardid', None)
			db.session.commit()

	return redirect('/redditflair/rankverification')


# parse playoverwatch profile and fetch rank
@redditflair.route('/redditflair/fetchrank', methods=['GET'])
@limiter.limit('5 per minute')
def fetch_rank():
	redditname = session.get('redditname')
	region = session.get('region', None)
	battletag = session.get('battletag', None)
	blizzard_id = session.get('blizzardid', None)
	#platform = request.args.get('platform')
	#xbl_name = request.args.get('xblname')
	#psn_name = request.args.get('psnname')

	if region and battletag and blizzard_id:# and platform:
		current_app.logger.info(
			f"Parsing blizzard profile u/{redditname} - {battletag} - {blizzard_id}")
		rank, url = parse_ow_profile(battletag)
		current_app.logger.info(
			f"Blizzard profile result u/{redditname} - {rank}")
		if rank:
			session['rank'] = rank

			# rank number
			rank_int = int(rank)
			session['ranknum'] = rank_int

			# update database entry
			redditname = session.get('redditname')
			if redditname:
				userObject = User.query.filter_by(name=redditname).first()
				if userObject:
					userObject.battletag = battletag
					userObject.rank = session['ranknum']
					db.session.commit()

			session['step'] = 1
			return redirect('/redditflair')
		else:
			session['rank'] = 'error'
			session['rank_url'] = url
			return redirect('/redditflair/rankverification')


@redditflair.route('/redditflair/updateflair', methods=['GET'])
def update_flair():
	flair1_name = request.args.get('flair1_id', None)
	flair2_name = request.args.get('flair2_id', None)
	custom_text = request.args.get('customflairtext', '')
	try:
		flair1 = Database.get_flair_by_short_name(flair1_name)
		flair2 = Database.get_flair_by_short_name(flair2_name)
		if (flair1_name and not flair1) or (flair2_name and not flair2):
			raise Exception('Unknown flair ID')
		redditname = session.get('redditname')
		current_app.logger.info(
			f"Flair update u/{redditname}: {flair1_name} : {flair2_name} : {custom_text}")
		user = Database.get_or_add_user(redditname)
		user.flair1 = flair1_name
		user.flair2 = flair2_name
		user.flairtext = custom_text
		Database.commit()

		Reddit.set_flair(redditname)
		session['updated'] = True
	except:
		pass

	return redirect('/redditflair')


@redditflair.errorhandler(429)
def ratelimit_handler(e):
	session['rateexceed'] = True
	return redirect('/redditflair/rankverification')
