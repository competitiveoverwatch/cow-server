from flask import session
from config import data as config
from config import flairdata
import praw

SPRITESHEETS = {
	'teams': 'st',
	'ranks': 'sr',
	'flags': 'sf',
	'special': 'sx'
}

def redditLink():
	return 'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + config['creds']['redditClientId'] + '&redirect_uri=' + config['creds']['redditRedirectURI'] + '&state=getreddit&scope=identity'
	
	
def redditLogin(code):
	if code:
		# create praw session with given code
		redditPraw = praw.Reddit(client_id=config['creds']['redditClientId'], client_secret=config['creds']['redditClientSecret'], redirect_uri=config['creds']['redditRedirectURI'], user_agent='rankification by u/jawoll')
		redditPraw.auth.authorize(code)
		
		# set session username if possible
		try:
			session['redditname'] = redditPraw.user.me().name
		except:
			pass
		
		# reset rank for new login
		session['rank'] = None
		
		
def redditUpdateFlair(flair1ID, flair2ID, customflairtext):
	redditname = session.get('redditname', None)
	if redditname:
		# ensure correct flair configuration
		if flair1ID == flair2ID:
			flair2ID = None
		if not flair1ID and flair2ID: 
			flair1ID = flair2ID
			flair2ID = None
		
		
		# get redditor
		redditPraw = praw.Reddit(client_id=config['creds']['redditBotClientId'], client_secret=config['creds']['redditBotClientSecret'], redirect_uri=config['creds']['redditBotRedirectURI'], user_agent='rankification by u/jawoll', username = config['creds']['redditBotUserName'], password = config['creds']['redditBotPassword'])
		user = praw.models.Redditor(redditPraw, name=redditname)
		subreddit = redditPraw.subreddit(config['config']['subreddit'])
		
		if flair1ID:
			# prepare css class
			flair1 = flairdata['flairs'][flair1ID]
			cssclass = SPRITESHEETS[flair1['sheet']] + '-c' + flair1['col'] + '-r' + flair1['row']
			flair2 = None
			if flair2ID:
				flair2 = flairdata['flairs'][flair2ID]
				cssclass += '-2' + SPRITESHEETS[flair2['sheet']] + '-2c' + flair2['col'] + '-2r' + flair2['row']
			
			print(cssclass)
			
			# prepare custom text
			text = ''
			if customflairtext:
				text += customflairtext + u' \u2014 '
			text += flair1['name']
			if flair2:
				text += ' | ' + flair2['name']
				
			print(text)
		else:
			cssclass = ''
			text = ''
			
		# update flair
		subreddit.flair.set(user, css_class = cssclass, text = text)
		print("ok")
		session['updated'] = True
	else:
		raise ValueError()
		
	return flair1ID, flair2ID	