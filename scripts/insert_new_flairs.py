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


def get_all_flairs():
	c = dbConn.cursor()
	flairs = []
	for row in c.execute('''
			SELECT short_name, sheet, col, row
			FROM flair
			'''):
		flairs.append({'short_name': row[0], 'sheet': row[1], 'col': row[2], 'row': row[3]})
	return flairs


def make_flair_matrix(sheet):
	# find maximum index
	size = 1
	flairs = get_all_flairs()
	for flair in flairs:
		if flair["sheet"] == sheet and flair["col"] and flair["row"]:
			row = int(flair["row"])
			col = int(flair["col"])
			if row > size:
				size = row
			if col > size:
				size = col
	# create matrix
	matrix = [[None for x in range(size)] for y in range(size)]
	# insert flairs in matrix
	for flair in flairs:
		if flair["sheet"] == sheet and flair["col"] and flair["row"]:
			row = int(flair["row"]) - 1
			col = int(flair["col"]) - 1
			matrix[row][col] = flair
	return matrix


def find_place(matrix, flair):
	found_place = False
	for row in range(len(matrix)):
		for col in range(len(matrix)):
			if matrix[row][col] is None:
				flair.col = '%02d' % (col + 1)
				flair.row = '%02d' % (row + 1)
				matrix[row][col] = flair
				found_place = True
				break
		if found_place:
			break
	# increase size if no space
	if not found_place:
		for row in matrix:
			row.extend([None])
		matrix.extend([[None] * (len(matrix) + 1)])
		flair.col = '%02d' % len(matrix)
		flair.row = '01'
		matrix[0][len(matrix) - 1] = flair
	return flair


def save_image(filename, short_name):
	input_path = r'C:\Users\greg\Downloads\ranks\\' + filename + ".png"
	output_path = r'C:\Users\greg\Desktop\PyCharm\cow-server\static\data\flair_images\\' + short_name + ".png"
	print(input_path)
	print(output_path)

	image = Image.open(input_path)
	image = image.convert('RGBA')

	background_color = (255, 255, 255, 0)
	width, height = image.size
	if width > height:
		squared = Image.new(image.mode, (width, width),
							background_color)
		squared.paste(image, (0, (width - height) // 2))
	elif width < height:
		squared = Image.new(image.mode, (height, height),
							background_color)
		squared.paste(image, ((height - width) // 2, 0))
	else:
		squared = image

	squared.thumbnail((64, 64), Image.ANTIALIAS)
	squared.save(output_path, quality=95, optimize=True)

	return True


with open(r"C:\Users\greg\Downloads\flairs.txt") as flair_file:
	for line in flair_file:
		items = line.split("\t")
		file_name = items[4].strip()
		print(file_name)
		save_image(file_name, items[0])
		flair = Flair(items[0], items[1], items[2], items[3])

		matrix = make_flair_matrix("ranks")
		find_place(matrix, flair)
		add_flair(flair)
