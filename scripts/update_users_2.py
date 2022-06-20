import praw
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from database import Flair, User
from collections import defaultdict


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

removed = {'a-bang','dignity','team-not-found','power-anchors','phase-2','big-time-regal-gaming','far-east-society','up-gaming','athletico','noble','tea-party','global-esports','saints','flag-gaming','light-gaming','ghostmode-gaming','neutral-break-gaming','cyclone-coupling','green-leaves','mega-esports','xavier-young','awakening','betrayed','horus-gaming','noweaver','simplicity','nyyrikki-esports','innocent-revolters'}

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

		print(f"{user_object.name}: {old_text}:{text} : {old_css_class}:{css_class}")

		# set flair via praw
		reddit_user = reddit.redditor(user_object.name)
		subreddit.flair.set(reddit_user, css_class=css_class, text=text)

	flair_object = session.query(Flair).filter_by(short_name=flair).filter_by(is_dirty=False).first()
	session.delete(flair_object)

session.commit()
session.close()
