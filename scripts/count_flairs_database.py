import sqlite3
from collections import defaultdict

dbConn = sqlite3.connect("cowserver.db")
c = dbConn.cursor()

flair_counts = {}
flair_categories = {}
for row in c.execute('''
		SELECT short_name, category
		FROM flair
		'''):
	flair_counts[row[0].strip()] = 0
	flair_categories[row[0].strip()] = row[1]

for row in c.execute('''
		SELECT flair1, flair2
		FROM user
		'''):
	if row[0]:
		flair_counts[row[0].strip()] += 1
	if row[1]:
		flair_counts[row[1].strip()] += 1

for flair in flair_counts:
	print(f"{flair}\t{flair_categories[flair]}\t{flair_counts[flair]}")

