from flask import session
from config import data as config
from config import get_flairdata
from database import db, User, Specials, Database
import praw

SPRITESHEETS = {
	'teams': 'steams',
	'ranks': 'sranks',
	'flags': 'sflags',
	'special': 'sspecial'
}


class Reddit:
	@classmethod
	def get_global_praw(cls):
		return praw.Reddit(
			client_id=config['creds']['redditBotClientId'],
			client_secret=config['creds']['redditBotClientSecret'],
			redirect_uri=config['creds']['redditBotRedirectURI'],
			user_agent='rankification by u/Watchful1',
			username=config['creds']['redditBotUserName'],
			password=config['creds']['redditBotPassword'])


	@classmethod
	def set_flair(cls, name, display_sr=True):
		flairdata = get_flairdata()

		user_object, specials = Database.get_user(name)

		text = ''
		css_class = ''
		if user_object.flair1:
			flair1 = flairdata['flairs'][user_object.flair1]
			css_class += 's' + flair1['sheet'] + '-c' + flair1['col'] + '-r' + flair1['row']
			text += cls.flair_name(flair1, user_object, display_sr)
		if user_object.flair2:
			flair2 = flairdata['flairs'][user_object.flair2]
			css_class += '-2s' + flair2['sheet'] + '-2c' + flair2['col'] + '-2r' + flair2['row']
			text += ' | ' + cls.flair_name(flair2, user_object, display_sr)

		# custom text
		if user_object.flairtext:
			# truncate if necessary
			max_len = 64 - len(text) - 3
			custom_text = user_object.flairtext[:max_len] if len(
				user_object.flairtext) > max_len else user_object.flairtext
			text = custom_text + u' \u2014 ' + text

		# set flair via praw
		reddit_praw = Reddit.get_global_praw()
		user = reddit_praw.redditor(name)
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		subreddit.flair.set(user, css_class=css_class, text=text)

	@classmethod
	def flair_name(cls, flair, user_object, display_sr=True):
		flair_name = ''
		if flair['name'] == 'Verified':
			verified_user = Database.get_verified_user(user_object.name)
			if verified_user:
				flair_name += u'\u2714 ' + verified_user.text
		else:
			flair_name += flair['name']
			if display_sr and flair['sheet'] == 'ranks':
				flair_name += ' (' + str(user_object.sr) + ')'
		return flair_name

	@classmethod
	def auth_link(cls, state):
		return \
			'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + \
			config['creds']['redditClientId'] + \
			'&redirect_uri=' + \
			config['creds']['redditRedirectURI'] + \
			'&state=' + \
			state + \
			'&scope=identity'


def reddit_link(state):
	return \
		'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + \
		config['creds']['redditClientId'] + \
		'&redirect_uri=' + \
		config['creds']['redditRedirectURI'] + \
		'&state=' + \
		state + \
		'&scope=identity'


def reddit_login(code):
	if code:
		# create praw session with given code
		reddit_praw = praw.Reddit(
			client_id=config['creds']['redditClientId'],
			client_secret=config['creds']['redditClientSecret'],
			redirect_uri=config['creds']['redditRedirectURI'],
			user_agent='rankification by u/Watchful1')
		reddit_praw.auth.authorize(code)

		# set session username if possible
		try:
			session['redditname'] = reddit_praw.user.me().name
		except:
			pass

		# reset rank for new login
		session['rank'] = None


def flair_name(flair_ID, user, sr):
	flairdata = get_flairdata()

	flair = flairdata['flairs'][flair_ID]
	flair_final = ''

	# verified
	if flair_ID == 'verified':
		special = Specials.query.filter_by(name=user).filter_by(specialid='verified').first()
		flair_final += u'\u2714 ' + special.text
	else:
		flair_final += flair['name']
		if sr and flair['sheet'] == 'ranks':
			flair_final += ' (' + str(sr) + ')'

	return flair_final


def reddit_update_flair(flair1_id, flair2_id, custom_flair_text, sr, redditname=None):
	flairdata = get_flairdata()

	if redditname is None:
		redditname = session.get('redditname', None)
	if redditname:
		# ensure correct flair configuration
		if flair1_id == flair2_id:
			flair2_id = None
		if not flair1_id and flair2_id:
			flair1_id = flair2_id
			flair2_id = None

		# get redditor
		reddit_praw = Reddit.get_global_praw()
		user = reddit_praw.redditor(redditname)
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])

		if flair1_id:
			# prepare css class
			flair1 = flairdata['flairs'][flair1_id]
			css_class = SPRITESHEETS[flair1['sheet']] + '-c' + flair1['col'] + '-r' + flair1['row']
			flair2 = None
			if flair2_id:
				flair2 = flairdata['flairs'][flair2_id]
				css_class += '-2' + SPRITESHEETS[flair2['sheet']] + '-2c' + flair2['col'] + '-2r' + flair2['row']

			# flair names
			text = flair_name(flair1_id, redditname, sr)
			if flair2:
				text += ' | ' + flair_name(flair2_id, redditname, sr)

			# custom text
			if custom_flair_text:
				# truncate if necessary
				maxLen = 64 - len(text) - 3
				custom_flair_text = custom_flair_text[:maxLen] if len(custom_flair_text) > maxLen else custom_flair_text
				text = custom_flair_text + u' \u2014 ' + text
		else:
			css_class = ''
			text = ''

		# update flair
		subreddit.flair.set(user, css_class=css_class, text=text)
		session['updated'] = True
	else:
		raise ValueError()

	return flair1_id, flair2_id


def reddit_css():
	reddit_praw = Reddit.get_global_praw()
	subreddit = reddit_praw.subreddit(config['config']['subreddit'])
	return subreddit.stylesheet().stylesheet
