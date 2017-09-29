from flask import session
from config import data as config
import praw


def redditLink():
	return 'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + config['creds']['redditClientId'] + '&redirect_uri=' + config['creds']['redditRedirectURI'] + '&state=getreddit&scope=identity'
	
	
def redditLogin(code):
	if code:
		# create praw session with given code
		redditPraw = praw.Reddit(client_id=config['creds']['redditClientId'], client_secret=config['creds']['redditClientSecret'], redirect_uri=config['creds']['redditRedirectURI'], user_agent='rankification by u/jawoll')
		redditRefreshToken = redditPraw.auth.authorize(code)
		
		# set session username if possible
		try:
			session['redditname'] = redditPraw.user.me().name
			session['step'] = 2
		except:
			pass
		
		# reset rank for new login
		session['rank'] = None
		
		
def redditUpdateFlair(customrank, customtext):
	battletag = session.get('battletag', '')
	redditname = session.get('redditname', '')
	rank = session.get('rank', 0)
	ranknum = session.get('ranknum', 1)

	if battletag and redditname and ranknum and rank and rank != "error":
		# get redditor
		redditPraw = praw.Reddit(client_id=config['creds']['redditBotClientId'], client_secret=config['creds']['redditBotClientSecret'], redirect_uri=config['creds']['redditBotRedirectURI'], user_agent='rankification by u/jawoll', username = config['creds']['redditBotUserName'], password = config['creds']['redditBotPassword'])
		user = praw.models.Redditor(redditPraw, name=redditname)
		subreddit = redditPraw.subreddit('Competitiveoverwatch')
		
		# prepare css class
		cssclass = ''
		if customrank and int(customrank) > 0 and int(customrank) < 8:
			ranknum = int(customrank)	
		cssclass = config['config']['ranks'][ranknum-1]
		
		# prepare custom text
		text = ''
		if customtext:
			text += customtext
			
		# update flair
		subreddit.flair.set(user, css_class = cssclass, text = text)

		session.clear()
		session['updated'] = True