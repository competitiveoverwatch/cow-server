from bs4 import BeautifulSoup
import urllib.request, re


if __name__ == "__main__":
	#battletag = "super#12850"
	battletag = "ModWilliam#1264"
	battletag = urllib.parse.quote(battletag.replace('#', '-'))
	pc_url = 'https://overwatch.blizzard.com/en-us/career/' + battletag

	current_rank = 0

	html = urllib.request.urlopen(pc_url)
	soup = BeautifulSoup(html, 'html.parser')

	ranks = {
	"bronzetier": 1,
	"silvertier": 2,
	"goldtier": 3,
	"platinumtier": 4,
	"diamondtier": 5,
	"mastertier": 6,
	"grandmastertier": 7,
	}

	# get rank
	nodes = soup.find_all(class_="Profile-playerSummary--rank")
	for node in nodes:
		image_url = node["src"].lower()
		found = False
		for tier, rank in ranks.items():
			if tier in image_url:
				if rank > current_rank:
					current_rank = rank
				found = True
		if not found:
			print(f"Couldn't find rank for image {image_url}")

	print(str(current_rank))

