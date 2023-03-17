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
		"bronzetier-5": 1,
		"bronzetier-4": 2,
		"bronzetier-3": 3,
		"bronzetier-2": 4,
		"bronzetier-1": 5,
		"silvertier-5": 6,
		"silvertier-4": 7,
		"silvertier-3": 8,
		"silvertier-2": 9,
		"silvertier-1": 10,
		"goldtier-5": 11,
		"goldtier-4": 12,
		"goldtier-3": 13,
		"goldtier-2": 14,
		"goldtier-1": 15,
		"platinumtier-5": 17,
		"platinumtier-4": 18,
		"platinumtier-3": 19,
		"platinumtier-2": 20,
		"platinumtier-1": 21,
		"diamondtier-5": 22,
		"diamondtier-4": 23,
		"diamondtier-3": 24,
		"diamondtier-2": 25,
		"diamondtier-1": 26,
		"mastertier-5": 27,
		"mastertier-4": 28,
		"mastertier-3": 29,
		"mastertier-2": 30,
		"mastertier-1": 31,
		"grandmastertier-5": 32,
		"grandmastertier-4": 33,
		"grandmastertier-3": 34,
		"grandmastertier-2": 35,
		"grandmastertier-1": 36,
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
				break
		if not found:
			print(f"Couldn't find rank for image {image_url}")

	print(str(current_rank))

