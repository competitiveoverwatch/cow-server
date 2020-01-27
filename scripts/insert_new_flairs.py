import requests
import json
import sqlite3
from PIL import Image, ImageEnhance
from database import Flair, Database

dbConn = sqlite3.connect("cowserver.db")


def clear_flairs():
	c = dbConn.cursor()
	c.execute('''
		DELETE FROM flair
	''')
	dbConn.commit()

	if c.rowcount > 0:
		return True
	else:
		return False


def add_flair(flair):
	c = dbConn.cursor()
	try:
		c.execute('''
			INSERT INTO flair
			(short_name, name, sheet, category, col, row, is_active, is_dirty)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		''', (flair.short_name, flair.name, flair.sheet, flair.category, flair.col, flair.row, flair.is_active, flair.is_dirty))
	except sqlite3.IntegrityError:
		return False

	dbConn.commit()
	return True


def save_image(short_name):
	input_path = r'C:\Users\greg\Downloads\flairs\\' + short_name + ".png"
	output_path = r'C:\Users\greg\Desktop\PyCharm\cow-server\static\data\flair_images\\' + short_name + ".png"

	image = Image.open(input_path)
	image = image.convert('RGBA')
	image.thumbnail((64, 64), Image.ANTIALIAS)
	image.save(output_path, quality=95, optimize=True)


# response = requests.get(url="http://rcompetitiveoverwatch.com/static/flairs.json", headers={'User-Agent': "flair counter"})
# json_data = json.loads(response.text)
#
# flair_names = json_data['flairs']
#
# for flair in new_flairs:
# 	save_image(flair.short_name)
	#add_flair(flair)

	#print(f"{flair.short_name}\t{flair.name}\t{flair.sheet}\t{flair.category}\t{flair.col if flair.col else ''}\t{flair.row if flair.row else ''}")


# c = dbConn.cursor()
# for row in c.execute('''
# 		SELECT short_name, name, sheet, category, col, row
# 		FROM flair
# 		'''):
# 	print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}")

clear_flairs()
with open(r"C:\Users\greg\Downloads\flairs.txt") as flair_file:
	for line in flair_file:
		items = line.split("\t")
		flair = Flair(items[0], items[1], items[2], items[3], col=items[4].zfill(2), row=items[5].strip().zfill(2))
		add_flair(flair)
