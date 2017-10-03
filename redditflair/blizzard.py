from flask import session
from config import data as config
from requests_oauthlib import OAuth2Session

def blizzardurl(region, api=False):
	if region == 'cn':
		if api:
			link = 'https://api.battlenet.com.cn/'
		else:
			link = 'https://www.battlenet.com.cn/oauth/'
	else:
		if api:
			link = 'https://{0}.api.battle.net/'.format(region)
		else:
			link = 'https://{0}.battle.net/oauth/'.format(region)
	return link

def blizzardRedirectURL(region):
	if not region:
		region = 'us'
	redirecturl = blizzardurl(region) + 'authorize?client_id=' + config['creds']['blizzardClientId'] + '&state=getblizzard&redirect_uri=' + config['creds']['blizzardRedirectURI'] + '&response_type=code'
	redirecturl = redirecturl.format(region)
	session['region'] = region
	return redirecturl
	
def blizzardLogin(code):
	if code:
		region = session.get('region', 'us')
		oauth = OAuth2Session(client_id=config['creds']['blizzardClientId'], redirect_uri=config['creds']['blizzardRedirectURI'], scope = [])
		token_data = oauth.fetch_token(blizzardurl(region) + 'token', code = code, client_secret = config['creds']['blizzardClientSecret'])
		blizzardToken = token_data['access_token']

		try:
			oauthtoken = OAuth2Session(client_id=config['creds']['blizzardClientId'], redirect_uri=config['creds']['blizzardRedirectURI'], token={'access_token': blizzardToken, 'token_type': 'bearer'})
			result = oauthtoken.get(blizzardurl(region, api=True) + 'account/user')
			session['battletag'] = result.json()['battletag']
			session['blizzardid'] = result.json()['id']
			session['step'] = 3
		except:
			pass
	
	session['rank'] = None