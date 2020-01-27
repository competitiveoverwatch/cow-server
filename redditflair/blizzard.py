from flask import session
from config import data as config
from requests_oauthlib import OAuth2Session


def blizzard_url(region, api=False):
	if region == 'cn':
		if api:
			link = 'https://api.battlenet.com.cn/'
		else:
			link = 'https://www.battlenet.com.cn/oauth/'
	else:
		if api:
			link = 'https://{0}.battle.net/'.format(region)
		else:
			link = 'https://{0}.battle.net/oauth/'.format(region)
	return link


def blizzard_redirect_url(region):
	if not region:
		region = 'us'
	redirect_url = \
		blizzard_url(region) + \
		'authorize?client_id=' + \
		config['creds']['blizzardClientId'] + \
		'&state=getblizzard&redirect_uri=' + \
		config['creds']['blizzardRedirectURI'] + \
		'&response_type=code'
	redirect_url = redirect_url.format(region)
	session['region'] = region
	return redirect_url


def blizzard_login(code):
	if code:
		region = session.get('region', 'us')
		oauth = OAuth2Session(
			client_id=config['creds']['blizzardClientId'],
			redirect_uri=config['creds']['blizzardRedirectURI'],
			scope=[])
		token_data = oauth.fetch_token(
			blizzard_url(region) + 'token',
			code=code,
			client_secret=config['creds']['blizzardClientSecret'])
		blizzard_token = token_data['access_token']

		oauth_token = OAuth2Session(
			client_id=config['creds']['blizzardClientId'],
			redirect_uri=config['creds']['blizzardRedirectURI'],
			token={'access_token': blizzard_token, 'token_type': 'bearer'})
		result = oauth_token.get(blizzard_url(region, api=True) + 'oauth/userinfo')
		session['battletag'] = result.json()['battletag']
		session['blizzardid'] = result.json()['id']
		session['step'] = 2

	session['rank'] = None
