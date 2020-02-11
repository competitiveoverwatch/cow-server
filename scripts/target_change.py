import praw
import sqlite3
import redditflair.reddit as reddit
from database import Flair, User

dbConn = sqlite3.connect("cowserver.db")
SUBREDDIT = "CompetitiveOverwatch"
COMMIT_CHANGES = False


def update_user(user):
	c = dbConn.cursor()
	c.execute('''
		UPDATE user
		(name, flair1, flair2, flairtext, sr, rank, is_mod, special_id, special_text)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	''', (user.name, user.flair1, user.flair2, user.flairtext, user.sr, user.rank, user.is_mod, user.special_id, user.special_text))
	dbConn.commit()


def get_flair(short_name):
	if short_name is None or short_name == '':
		return None
	c = dbConn.cursor()
	result = c.execute('''
		SELECT short_name, name, sheet, category, is_active, col, row, is_dirty
		FROM flair
		WHERE short_name = ?
	''', (short_name,))

	row = result.fetchone()

	if not row:
		return None
	else:
		flair = Flair(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
		return flair


c = dbConn.cursor()
changed_users = []
for row in c.execute('''
		SELECT name, flair1, flair2, flairtext, sr, rank, is_mod, special_id, special_text
		FROM user
		'''):
	user = User(
		name=row[0],
		flair1=row[1],
		flair2=row[2],
		flairtext=row[3],
		sr=row[4],
		rank=row[5],
		is_mod=row[6],
		special_id=row[7],
		special_text=row[8]
	)
	dirty = False
	if user.flair1 == ' square-one':
		print(f"{user.name} : square one fix")
		user.flair1 = 'square-one'
		dirty = True

	if user.flairtext == 'None':
		print(f"{user.name} : None fix")
		user.flairtext = ''
		dirty = True

	if dirty:
		changed_users.append(user)

print(f"{len(changed_users)} changes")
if COMMIT_CHANGES:
	print("Committing")
else:
	print("Not committing")

flair_updates = []
for user in changed_users:
	flair1 = get_flair(user.flair1)
	flair2 = get_flair(user.flair2)
	flair_text, flair_css = reddit.render_flair(user, flair1, flair2)
	flair_updates.append({'user': user.name, 'flair_css_class': flair_css, 'flair_text': flair_text})
	print(f"{user.name} : {flair_text} : {flair_css}")

	if COMMIT_CHANGES:
		update_user(user)

if COMMIT_CHANGES:
	r = praw.Reddit("OWMatchThreads", user_agent="script agent")
	r.subreddit(SUBREDDIT).flair.update(flair_updates)

dbConn.close()
