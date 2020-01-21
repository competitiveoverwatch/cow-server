import praw
import requests
import json
import re
from collections import defaultdict

user_agent = "flair counter"

# response = requests.get(url="http://rcompetitiveoverwatch.com/static/flairs.json", headers={'User-Agent': user_agent})
# json_data = json.loads(response.text)
#
# flairs = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
# for key in json_data['flairs']:
# 	flair_json = json_data['flairs'][key]
# 	flairs[flair_json['sheet']][flair_json['row']][flair_json['col']] = flair_json['name']

r = praw.Reddit("OWMatchThreads", user_agent=user_agent)

count = 0
for flair in r.subreddit("CompetitiveOverwatch").flair(limit=None):
	count += 1
	if count % 1000 == 0:
		print(str(count))
	# css = flair['flair_css_class']
	# first = re.search(r'^s(\w+)-c(\d\d)-r(\d\d)', css)
	# if first and len(first.groups()) == 3:
	# 	#print(f"{first.group(1)} - {first.group(2)} - {first.group(3)}")
	# 	print(flairs[first.group(1)][first.group(2)][first.group(3)] + " - " + flair['user'].name)
	# else:
	# 	first = re.search(r'^s(\w+)-r(\d\d)-c(\d\d)', css)
	# 	if first and len(first.groups()) == 3:
	# 		#print(f"{first.group(1)} - {first.group(3)} - {first.group(2)}")
	# 		print(flairs[first.group(1)][first.group(3)][first.group(2)] + " - " + flair['user'].name)
	# 	else:
	# 		print(f"None: {css} - {flair['user'].name}")

print(str(count))
