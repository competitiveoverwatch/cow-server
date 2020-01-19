import json

data = dict()

with open("config/config.json") as config_data:
	data['config'] = json.load(config_data)

with open("config/creds.json") as creds_data:
	data['creds'] = json.load(creds_data)


def get_flairdata(temp=False):
	flairdata = None
	if temp:
		with open("data/flairs_tmp.json") as flair_data:
			flairdata = json.load(flair_data)
	else:
		with open("data/flairs.json") as flair_data:
			flairdata = json.load(flair_data)
	return flairdata


def set_flairdata(flairdata, temp=False):
	if temp:
		with open('data/flairs_tmp.json', 'w') as flair_data:
			json.dump(flairdata, flair_data, indent=4)
	else:
		with open('data/flairs.json', 'w') as flair_data:
			json.dump(flairdata, flair_data, indent=4)
