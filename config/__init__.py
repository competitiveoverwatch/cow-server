import json

data = dict()

with open("config/config.json") as config_data:
	data['config'] = json.load(config_data)

with open("config/creds.json") as creds_data:
	data['creds'] = json.load(creds_data)
	
flairdata = None
with open("config/flairs.json") as flair_data:
	flairdata = json.load(flair_data)