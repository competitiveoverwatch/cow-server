from database import db, User, Specials
import praw, json, operator, re
from config import data as config
from config import flairdata

FLAIR_REPLACEMENTS = {
	'fan 123': '123', 
	'fan 1246': '1246', 
	'fan ahq-esports-club': 'ahq-e-sports-club', 
	'fan anox': 'anox', 
	'fan arc-6': 'arc-6', 
	'fan ardeont': 'ardeont', 
	'fan bazooka-puppiez': 'bazooka-puppiez', 
	'fan blank': 'blank-esports', 
	'fan brasil-gaming-house': 'brasil-gaming-house', 
	'fan c9': 'cloud9', 
	'fan c9-kongdoo': 'cloud9-kongdoo', 
	'fan clg': 'counter-logic-gaming', 
	'fan cloud-9': 'cloud9', 
	'fan col': 'complexity-gaming', 
	'fan complexity': 'complexity-gaming', 
	'fan conbox-spirit': 'conbox', 
	'fan counter-logic-gaming': 'counter-logic-gaming', 
	'fan dallas-fuel': 'dallas-fuel', 
	'fan dig': 'dignitas', 
	'fan dignitas': 'dignitas', 
	'fan envision': 'envision', 
	'fan envy': 'envyus', 
	'fan envyus': 'envyus', 
	'fan eunited': 'eunited', 
	'fan evil-geniuses': 'evil-geniuses', 
	'fan faze': 'faze', 
	'fan flash-lux': 'flash-lux', 
	'fan flash-wolves': 'flash-wolves', 
	'fan fnatic': 'fnatic', 
	'fan fnrgfe': 'fnrgfe', 
	'fan freecs': 'afreeca-freecs', 
	'fan freecs-blue': 'afreeca-freecs', 
	'fan freecs-red': 'afreeca-freecs', 
	'fan ftd-club': 'ftd-club', 
	'fan gamersorigin': 'gamersorigin', 
	'fan gc-busan': 'gc-busan', 
	'fan gigantti': 'team-gigantti', 
	'fan immortals': 'immortals', 
	'fan kongdoo-panthera': 'kongdoo-panthera', 
	'fan kongdoo-uncia': 'kongdoo-uncia', 
	'fan kungarna': 'kungarna', 
	'fan laser-kittenz': 'laser-kittenz', 
	'fan ldlc': 'ldlc', 
	'fan lg-evil': 'luminosity-gaming-evil', 
	'fan lg-loyal': 'luminosity-gaming', 
	'fan lgd-gaming': 'lgd-gaming', 
	'fan libalent-supreme': 'libalent-supreme', 
	'fan liquid': 'team-liquid', 
	'fan lucky-future': 'lucky-future', 
	'fan luminosity': 'luminosity-gaming', 
	'fan lunatic hai': 'lunatic-hai', 
	'fan lunatic-hai': 'lunatic-hai', 
	'fan luxury-watch-blue': 'luxury-watch-blue', 
	'fan luxury-watch-red': 'luxury-watch-red', 
	'fan mega-thunder': 'mega-thunder', 
	'fan meta-athena': 'meta-athena', 
	'fan method': 'method', 
	'fan miraculous-youngsters': 'miraculous-youngsters', 
	'fan misfits': 'misfits', 
	'fan movistar-riders': 'movistar-riders', 
	'fan mvp-space': 'mvp-space', 
	'fan nc-foxes': 'rx-foxes', 
	'fan nga': 'nga', 
	'fan ninjas-in-pyjamas': 'ninjas-in-pyjamas', 
	'fan nip': 'ninjas-in-pyjamas', 
	'fan nrg': 'nrg', 
	'fan oh-my-god': 'oh-my-god', 
	'fan renegades': 'renegades', 
	'fan rest-in-pyjamas': 'rest-in-pyjamas', 
	'fan reunited': 'reunited', 
	'fan rise': 'rise-nation', 
	'fan rogue': 'rogue', 
	'fan rox-orcas': 'rox-orcas', 
	'fan runaway': 'runaway', 
	'fan scylla': 'scylla-esports', 
	'fan selfless': 'selfless-gaming', 
	'fan shanghai-dragons': 'shanghai-dragons', 
	'fan singularity-ninjas': 'team-singularity',  
	'fan storm': 'tempo-storm',
	'fan tempo-storm': 'tempo-storm', 
	'fan vici-gaming': 'vici-gaming', 
	'fan vivis-adventure': 'vivis-adventure', 
	'fan x6-gaming': 'x6-gaming', 
	'fan yikes': 'arc-6', 
	'fan you-guys-get-paid': 'you-guys-get-paid', 
	'flag ar': 'flag-ar', 
	'flag at': 'flag-at', 
	'flag au': 'flag-au', 
	'flag be': 'flag-be', 
	'flag br': 'flag-br', 
	'flag ca': 'flag-ca', 
	'flag cn': 'flag-cn', 
	'flag de': 'flag-de', 
	'flag dk': 'flag-dk', 
	'flag es': 'flag-es', 
	'flag fi': 'flag-fi', 
	'flag fr': 'flag-fr', 
	'flag gb': 'flag-gb', 
	'flag hk': 'flag-hk', 
	'flag il': 'flag-il', 
	'flag it': 'flag-it', 
	'flag jp': 'flag-jp', 
	'flag kr': 'flag-kr', 
	'flag nl': 'flag-nl', 
	'flag no': 'flag-no', 
	'flag nz': 'flag-nz', 
	'flag pl': 'flag-pl', 
	'flag pt': 'flag-pt', 
	'flag ro': 'flag-ro', 
	'flag ru': 'flag-ru', 
	'flag se': 'flag-se', 
	'flag sg': 'flag-sg', 
	'flag th': 'flag-th', 
	'flag tr': 'flag-tr', 
	'flag tw': 'flag-tw', 
	'flag us': 'flag-us', 
	'flag vn': 'flag-vn', 
	'rank bronze': 'bronze', 
	'rank diamond': 'diamond', 
	'rank gold': 'gold', 
	'rank grandmaster': 'grandmaster', 
	'rank master': 'master', 
	'rank platinum': 'platinum', 
	'rank silver': 'silver'
}

def redditToDatabase(app):
	with app.app_context():
		redditPraw = praw.Reddit(client_id=config['creds']['redditBotClientId'], client_secret=config['creds']['redditBotClientSecret'], redirect_uri=config['creds']['redditBotRedirectURI'], user_agent='rankification by u/jawoll', username = config['creds']['redditBotUserName'], password = config['creds']['redditBotPassword'])
		subreddit = redditPraw.subreddit('Competitiveoverwatch')
		
		for flair in subreddit.flair(limit=None):
			username = flair['user'].name
			# normal flairs
			if flair['flair_css_class'] in FLAIR_REPLACEMENTS: 
				# create new entry
				newUser = User(username)
				newUser.flair1 = FLAIR_REPLACEMENTS[flair['flair_css_class']]
				if flair['flair_text']:
					newUser.flairtext = re.sub('[^\s\w]+', '', flair['flair_text'])
				db.session.add(newUser)
				db.session.commit()
				print('added user: ' + username + '   with flair: ' + newUser.flair1)
				
			# secial flairs
			if flair['flair_css_class'] == 'verified' or flair['flair_css_class'] == 'blizzard':
				# create new user entry
				newUser = User(username)
				newUser.flair1 = flair['flair_css_class']
				db.session.add(newUser)
				db.session.commit()
				# create new specials entry
				newSpecial = Specials(username)
				newSpecial.specialid = flair['flair_css_class']
				newSpecial.text = flair['flair_text'].replace('✓ ','')
				db.session.add(newSpecial)
				db.session.commit()
				print('added verified user: ' + username + '   with flair: ' + newUser.flair1)
				
def databaseToReddit(app):
	with app.app_context():
		redditPraw = praw.Reddit(client_id=config['creds']['redditBotClientId'], client_secret=config['creds']['redditBotClientSecret'], redirect_uri=config['creds']['redditBotRedirectURI'], user_agent='rankification by u/jawoll', username = config['creds']['redditBotUserName'], password = config['creds']['redditBotPassword'])
		subreddit = redditPraw.subreddit('CO_Test')
		for id, flair in flairdata['flairs'].items():
			flair_users = User.query.filter_by(flair1=id)
			css_class = 's' + flair['sheet'] + '-r' + flair['row'] + '-c' + flair['col']
			userlist = []
			for user in flair_users:
				temp = dict()
				temp['user'] = user.name
				temp['flair_css_class'] = css_class
				if flair['sheet'] == 'special':
					special = Specials.query.filter_by(name=user.name).first()
					temp['flair_text'] = special.text
				else:
					flairtext = ''
					if user.flairtext:
						flairtext += user.flairtext + u' \u2014 '
					flairtext += flair['name']
					temp['flair_text'] = flairtext
				userlist.append(temp)
			print('Updating ' + str(len(userlist)) + ' users with flair: ' + flair['name'])
			subreddit.flair.update(userlist)
			print('updated users: ' + str(userlist))
			
def specialsToReddit(app):
	pass