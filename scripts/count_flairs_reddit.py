import praw
import requests
import json
import re
import sqlite3
from collections import defaultdict

user_agent = "flair counter"


dbConn = sqlite3.connect("cowserver_old.db")


def get_user_flairs(user):
	c = dbConn.cursor()
	result = c.execute('''
		SELECT flair1, flair2
		FROM user
		where name = ?
	''', (user,))

	resultTuple = result.fetchone()

	if not resultTuple:
		return None, None
	else:
		return resultTuple[0] if resultTuple[0] else None, resultTuple[1] if resultTuple[1] else None


response = requests.get(url="http://rcompetitiveoverwatch.com/static/flairs.json", headers={'User-Agent': user_agent})
json_data = json.loads(response.text)

flairs = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
flair_names = json_data['flairs']
for key in flair_names:
	flair_json = json_data['flairs'][key]
	flairs[flair_json['sheet']][flair_json['row']][flair_json['col']] = key

for category in json_data['categories']:
	for flair in category['items']:
		if 'category' in flair_names[flair]:
			print(f"Duplicate category: {category['title']} : {flair_names[flair]['name']} : {flair_names[flair]['category']}")
		flair_names[flair]['category'] = category['title']

r = praw.Reddit("OWMatchThreads", user_agent=user_agent)

count = 0
flair_counts = defaultdict(int)
for flair in r.subreddit("CompetitiveOverwatch").flair(limit=None):
	count += 1
	if count % 1000 == 0:
		print(str(count))

	name = flair['user'].name
	css = flair['flair_css_class']
	if not css:
		continue

	flair1 = None
	sheet = None
	row = None
	col = None
	first = re.search(r'^s(\w+)-c(\d\d)-r(\d\d)', css)
	if first and len(first.groups()) == 3:
		sheet = first.group(1)
		row = first.group(3)
		col = first.group(2)
	else:
		first = re.search(r'^s(\w+)-r(\d\d)-c(\d\d)', css)
		if first and len(first.groups()) == 3:
			sheet = first.group(1)
			row = first.group(2)
			col = first.group(3)

	if sheet and sheet in flairs and row in flairs[sheet] and col in flairs[sheet][row]:
		flair1 = flairs[sheet][row][col]
		flair_counts[flair1] += 1

	flair2 = None
	sheet = None
	row = None
	col = None
	second = re.search(r'2s(\w+)-2c(\d\d)-2r(\d\d)$', css)
	if second and len(second.groups()) == 3:
		sheet = second.group(1)
		row = second.group(3)
		col = second.group(2)
	else:
		second = re.search(r'2s(\w+)-2r(\d\d)-2c(\d\d)$', css)
		if second and len(second.groups()) == 3:
			sheet = second.group(1)
			row = second.group(2)
			col = second.group(3)

	if sheet and sheet in flairs and row in flairs[sheet] and col in flairs[sheet][row]:
		flair2 = flairs[sheet][row][col]
		flair_counts[flair2] += 1

	# database_flair1, database_flair2 = get_user_flairs(name)
	#
	# if flair1 != database_flair1 or flair2 != database_flair2:
	# 	print(f"{flair1}/{database_flair1} - {flair2}/{database_flair2} - u/{name}")

	# if flair1 and flair2:
	# 	print(flair1 + " - " + flair2 + " - " + name)
	# elif flair1:
	# 	print(flair1 + " - " + name)
	# elif flair2:
	# 	print(flair2 + " - " + name)
	# else:
	# 	print(f"None: {css} - {name}")

print(str(count))

for flair in flair_names:
	category = ""
	if 'category' in flair_names[flair]:
		category = flair_names[flair]['category']
	name = flair_names[flair]['name']
	print(f"{flair}\t{name}\t{category}\t{flair_counts[flair]}")
