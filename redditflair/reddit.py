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
	def set_flair(cls, name):
		user_object = Database.get_or_add_user(name)

		text = ''
		css_class = ''
		if user_object.flair1:
			flair1 = Database.get_flair_by_short_name(user_object.flair1)
			css_class += 's' + flair1.sheet + '-c' + flair1.col + '-r' + flair1.row
			text += ':' + flair1.short_name + ':'
		if user_object.flair2:
			flair2 = Database.get_flair_by_short_name(user_object.flair2)
			css_class += '-2s' + flair2.sheet + '-2c' + flair2.col + '-2r' + flair2.row
			text += ':' + flair2.short_name + ':'

		# special text
		if user_object.special_text:
			# truncate if necessary
			max_len = 64 - len(text) - 3
			special_text = user_object.special_text[:max_len] if len(
				user_object.special_text) > max_len else user_object.special_text
			text = special_text + u' \u2014 ' + text

		# custom text
		if user_object.flairtext:
			# truncate if necessary
			max_len = 64 - len(text) - 3
			if max_len > 0:
				custom_text = user_object.flairtext[:max_len] if len(
					user_object.flairtext) > max_len else user_object.flairtext
				text = custom_text + u' \u2014 ' + text

		# set flair via praw
		reddit_praw = Reddit.get_global_praw()
		user = reddit_praw.redditor(name)
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		subreddit.flair.set(user, css_class=css_class, text=text)

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
	def save_stylesheet(cls, stylesheet):
		reddit_praw = Reddit.get_global_praw()
		subreddit = reddit_praw.subreddit(config['config']['subreddit'])
		subreddit.stylesheet.update(stylesheet)


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
