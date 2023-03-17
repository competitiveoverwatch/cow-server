from bs4 import BeautifulSoup
import urllib.request, re


ranks = {
	"bronzetier": 1,
	"silvertier": 2,
	"goldtier": 3,
	"platinumtier": 4,
	"diamondtier": 5,
	"mastertier": 6,
	"grandmastertier": 7,
}


def parse_ow_profile(battletag):
	battletag = urllib.parse.quote(battletag.replace('#', '-'))
	pc_url = 'https://overwatch.blizzard.com/en-us/career/' + battletag

	current_rank = 0
	html = urllib.request.urlopen(pc_url)
	soup = BeautifulSoup(html, 'html.parser')
	nodes = soup.find_all(class_="Profile-playerSummary--rank")
	for node in nodes:
		image_url = node["src"].lower()
		found = False
		for tier, rank in ranks.items():
			if tier in image_url:
				if rank > current_rank:
					current_rank = rank
				found = True
				break
		if not found:
			pass
			#log.warning(f"Couldn't find rank for image {image_url}")

	if current_rank == 0:
		current_rank = None
	return current_rank, pc_url
