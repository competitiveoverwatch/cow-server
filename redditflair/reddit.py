from flask import session
from config import data as config
from database import db, User, Flair, Database
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
		return praw.Reddit(config['creds']['redditBotUserName'], user_agent='rankification by u/Watchful1')

	@classmethod
	def set_flair(cls, name, display_sr=True):
		user_object = Database.get_or_add_user(name)

		text = ''
		css_class = ''
		if user_object.flair1:
			flair1 = Database.get_flair_by_short_name(user_object.flair1)
			css_class += 's' + flair1['sheet'] + '-c' + flair1['col'] + '-r' + flair1['row']
			text += cls.flair_name(flair1, user_object, display_sr)
		if user_object.flair2:
			flair2 = Database.get_flair_by_short_name(user_object.flair2)
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
			verified_user = Database.get_or_add_user(user_object.name)
			if verified_user.special_id:
				flair_name += u'\u2714 ' + verified_user.special_text
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

	@classmethod
	def upload_emoji(cls, name, path):
		reddit_praw = Reddit.get_global_praw()
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		subreddit.emoji.add(name, path)

	@classmethod
	def upload_stylesheet_image(cls, image_name):
		reddit_praw = Reddit.get_global_praw()
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		subreddit.stylesheet.upload(
			image_name,
			'static/data/' + image_name + '.png')

	@classmethod
	def re_save_stylesheet(cls):
		reddit_praw = Reddit.get_global_praw()
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		css = subreddit.stylesheet().stylesheet
		subreddit.stylesheet.update(css)


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


def reddit_css():
	reddit_praw = Reddit.get_global_praw()
	subreddit = reddit_praw.subreddit(config['config']['subreddit'])
	return subreddit.stylesheet().stylesheet
