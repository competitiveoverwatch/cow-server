from flask import session
from config import data as config
from config import flairdata
from database import db, User, Specials, Database
import praw

SPRITESHEETS = {
    'teams': 'steams',
    'ranks': 'sranks',
    'flags': 'sflags',
    'special': 'sspecial'
}

class Reddit():
    @classmethod
    def set_flair(cls, name, display_sr=True):
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
            maxLen = 64 - len(text) - 3
            custom_text = user_object.flairtext[:maxLen] if len(user_object.flairtext) > maxLen else user_object.flairtext
            text = custom_text + u' \u2014 ' + text
        else:
            css_class = ''
            text = ''
        
        # set flair via praw
        reddit_praw = praw.Reddit(client_id=config['creds']['redditBotClientId'], client_secret=config['creds']['redditBotClientSecret'], redirect_uri=config['creds']['redditBotRedirectURI'], user_agent='rankification by u/jawoll', username = config['creds']['redditBotUserName'], password = config['creds']['redditBotPassword'])
        user = praw.models.Redditor(reddit_praw, name=name)
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
        return 'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + config['creds']['redditClientId'] + '&redirect_uri=' + config['creds']['redditRedirectURI'] + '&state=' + state + '&scope=identity'
    
    
    
def redditLink(state):
    return 'https://www.reddit.com/api/v1/authorize?duration=temporary&response_type=code&client_id=' + config['creds']['redditClientId'] + '&redirect_uri=' + config['creds']['redditRedirectURI'] + '&state=' + state + '&scope=identity'
    
    
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
        
def flairName(flairID, user, sr):
    flair = flairdata['flairs'][flairID]
    flairname = ''
    
    # verified
    if flairID == 'verified':
        special = Specials.query.filter_by(name=user).filter_by(specialid='verified').first()
        flairname += u'\u2714 ' + special.text
    else:
        flairname += flair['name']
        if sr and flair['sheet'] == 'ranks':
            flairname += ' (' + str(sr) + ')'
    
    return flairname
        
def redditUpdateFlair(flair1ID, flair2ID, customflairtext, sr, redditname = None):
    if redditname == None:
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
            
            # flair names
            text = flairName(flair1ID, redditname, sr)
            if flair2:
                text += ' | ' + flairName(flair2ID, redditname, sr)
                
            # custom text
            if customflairtext:
                # truncate if necessary
                maxLen = 64 - len(text) - 3
                customflairtext = customflairtext[:maxLen] if len(customflairtext) > maxLen else customflairtext
                text = customflairtext + u' \u2014 ' + text
        else:
            cssclass = ''
            text = ''
            
        # update flair
        subreddit.flair.set(user, css_class = cssclass, text = text)
        session['updated'] = True
    else: 
        raise ValueError()
        
    return flair1ID, flair2ID   