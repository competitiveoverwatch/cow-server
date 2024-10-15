import praw, prawcore
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from database import Flair, User
from collections import defaultdict
import time


def render_flair(user, flair1, flair2):
	text = ''
	css_class = ''
	if not flair1 and not flair2:
		return text, css_class

	if flair1:
		css_class += 's' + flair1.sheet + '-c' + flair1.col + '-r' + flair1.row
		text += ':' + flair1.short_name + ':'
	if flair2:
		css_class += '-2s' + flair2.sheet + '-2c' + flair2.col + '-2r' + flair2.row
		text += ':' + flair2.short_name + ':'

	# special text
	if user.special_text:
		# truncate if necessary
		max_len = 64 - len(text) - 3
		special_text = user.special_text[:max_len] if len(user.special_text) > max_len else user.special_text
		text = special_text + u' \u2014 ' + text

	# custom text
	if user.flairtext:
		# truncate if necessary
		max_len = 64 - len(text) - 3
		if max_len > 0:
			custom_text = user.flairtext[:max_len] if len(user.flairtext) > max_len else user.flairtext
			text = custom_text + u' \u2014 ' + text

	if not user.special_text and not user.flairtext:
		text = " " + text

	return text, css_class

reddit = praw.Reddit("OWMatchThreads", user_agent="flair updating")
subreddit = reddit.subreddit("CompetitiveOverwatch")

removed = {'michigan','minnesota','uc-los-angeles','cal-state-long-beach','miami-ohio','mizzou','stephens-institute','midland','akron','bellevue','colorado','florida','fresno-state','kent-state','north-texas','northwood','ontario-tech','scad','uc-riverside','second-wind','team-cc','order','cis-hope','kungarna','rise-nation','patitos','orgless-hungry','kongdoo-uncia','montreal-rebellion','method','triumph','team-cat','talon-esports','last-nights-leftovers','vivis-adventure','skyfoxes','odyssey','revival','hsl-esports','lucky-future','war-pigs','square-one','eternal-academy','samsung-ms','darkmode-na','world-game-star','altiora','maryville-esports','old-and-bored','first-fabulous-fighter','intro-wave','team-bm','obey-alliance','spackle-academy','new-kings','angelica-esport','roll-momo','team-name','4giver','dire-wolves','teamfp','rhodes','ow-contenders-logo','ow-open-division-logo','ow-world-cup-logo','ground-zero','0rd3r','remedy','team-chaser','ignite-one','the-one-winner','bilibili-gaming','zones','bull-frog-in-well','time-resume','courage','cnow','shus-money-crew','raspberry-racers','triple-esports','ataraxia','pitbull-storm','dreamers','mdy','starlight-gaming','team-diamond','pathera','nt','duck','odh','xero','min-shark','fm','jngk','wisp','trick-room','Saints','redbirds','o3-splash','afterlife','rift','amplify','good-boys','kraken-esports-club','brainlets','ngu-k','invincible','tamakoro','ouyue-esport','far-east-society','flag-mx','flag-ph','flag-pr','flag-ar','flag-cl','flag-co','flag-ae','flag-ch','flag-be','flag-cr','flag-ec','flag-gt','flag-in','flag-id','flag-my','flag-pe','flag-sa','flag-tr','owlp-s1-weekly','owlp-s1-bronze','comm-cup','blizzard','owlp-s1-silver','owlp-s1-gold'}

engine = create_engine('sqlite:///cowserver.db')
session = Session(engine)

for flair in removed:
	for user_object in session.query(User).filter(or_(User.flair1 == flair, User.flair2 == flair)).all():
		old_text, old_css_class = render_flair(
			user_object,
			session.query(Flair).filter_by(short_name=user_object.flair1).filter_by(is_dirty=False).first(),
			session.query(Flair).filter_by(short_name=user_object.flair2).filter_by(is_dirty=False).first()
		)

		if user_object.flair1 in removed:
			user_object.flair1 = None
		if user_object.flair2 in removed:
			user_object.flair2 = None

		text, css_class = render_flair(
			user_object,
			session.query(Flair).filter_by(short_name=user_object.flair1).filter_by(is_dirty=False).first(),
			session.query(Flair).filter_by(short_name=user_object.flair2).filter_by(is_dirty=False).first()
		)

		print(f"u/{user_object.name}: {old_text}|{text} --- {old_css_class}|{css_class}")

		# set flair via praw
		for i in range(10):
			try:
				try:
					reddit_user = reddit.redditor(user_object.name)
					reddit_flair = next(subreddit.flair(redditor=reddit_user))

					if reddit_flair is None:
						print(f"    flair not set")
					else:
						# if reddit_flair["flair_css_class"] != old_css_class:
						# 	print(f"    reddit css doesn't match: {reddit_flair['flair_css_class']} != {old_css_class}")
						# if reddit_flair["flair_text"] != old_text:
						# 	print(f"    reddit text doesn't match: {reddit_flair['flair_text']} != {old_text}")
						subreddit.flair.set(reddit_user, css_class=css_class, text=text)
				except prawcore.exceptions.Forbidden:
					pass
				break
			except Exception as err:
				print(f"WARNING: {err} sleeping {i * 10} seconds")
				time.sleep(i * 10)

	flair_object = session.query(Flair).filter_by(short_name=flair).filter_by(is_dirty=False).first()
	session.delete(flair_object)

session.commit()
session.close()
