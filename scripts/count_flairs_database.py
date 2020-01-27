import sqlite3
from collections import defaultdict

dbConn = sqlite3.connect("cowserver_old.db")
c = dbConn.cursor()

flair_counts = defaultdict(int)
for row in c.execute('''
		SELECT flair1, flair2
		FROM user
		'''):
	if row[0]:
		flair_counts[row[0]] += 1
	if row[1]:
		flair_counts[row[1]] += 1

for flair in flair_counts:
	print(f"{flair}\t{flair_counts[flair]}")

