import json
import os
import time
import tinify
import zipfile

from PIL import Image, ImageEnhance
from flask import Blueprint, make_response, render_template, session, redirect, request, current_app

import redditflair.reddit as reddit
from config import data as config_data
from database import Database, Flair
from redditflair.reddit import Reddit

flair_sheets = Blueprint('flair_sheets', __name__)
tinify.key = config_data['creds']['tinifyKey']


def save_image(file, short_name):
	if file and file.filename != '' and file.filename.endswith(".png"):
		path = os.path.join('static/data/flair_images', short_name + '.png')
		file.save(path)

		image = Image.open(path)
		image = image.convert('RGBA')
		image.thumbnail((64, 64), Image.ANTIALIAS)
		image.save(path, quality=95, optimize=True)
		return True

	else:
		return False


def fade_image(image):
	colorConverter = ImageEnhance.Color(image)
	image = colorConverter.enhance(0.2)
	# 50% transparency
	bands = list(image.split())
	if len(bands) == 4:
		# Assuming alpha is the last band
		bands[3] = bands[3].point(lambda x: x * 0.5)
	image = Image.merge(image.mode, bands)
	return image


@flair_sheets.route('/flairsheets')
def flair_sheets_page():
	response_params = dict()
	response_params['redditLink'] = Reddit.auth_link('flairsheets')

	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	# gather flairs
	clean_flairs = Database.get_clean_flair()
	dirty_flairs = Database.get_dirty_flair()

	response = make_response(
		render_template(
			'flairsheets.html', **response_params, clean_flairs=clean_flairs, dirty_flairs=dirty_flairs))
	return response


@flair_sheets.route('/flairsheets/edit/<id>', methods=['GET', 'POST'])
def flair_edit(id):
	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	flair = Database.get_flair(id)

	if flair is None:
		return redirect('/flairsheets')

	response_params = dict()
	response_params['redditLink'] = Reddit.auth_link('flairsheets')

	if request.method == 'POST':
		name = request.form['name']
		faded = request.form['faded']
		category = request.form['category']
		if name:
			if not flair.is_dirty:
				flair = Database.clone_flair(flair)

			changes = []

			# update flair and json
			if flair.name != name:
				changes.append(f"name: {flair.name} - {name}")
				flair.name = name
			else:
				changes.append(f"name: {flair.name}")
			if faded == 'yes' and not flair.is_active:
				changes.append(f"faded: yes - no")
				flair.is_active = False
			elif faded == 'no' and flair.is_active:
				changes.append(f"faded: no - yes")
				flair.is_active = True
			if flair.category != category:
				changes.append(f"category: {flair.category} - {category}")
				flair.category = category

			Database.commit()
			# Upload image if necessary
			if 'file' in request.files:
				changes.append(f"image updated")
				file = request.files['file']
				save_image(file, flair.short_name)

			current_app.logger.warning(f"u/{redditname} updated flair: {', '.join(changes)}")

			return redirect('/flairsheets')

	response = make_response(
		render_template(
			'flairedit.html', **response_params, id=id, flair=flair,
			flairsheets=config_data['config']['flair_sheets'],
			categories=config_data['config']['categories']))
	return response


@flair_sheets.route('/flairsheets/new', methods=['GET', 'POST'])
def flair_new():
	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	current_app.logger.warning(f"u/{redditname} updated flair")
	# process request
	if request.method == 'POST':
		short_name = request.form['short_name']
		name = request.form['name']
		flairsheet = request.form['flairsheet']
		faded = request.form['faded']
		category = request.form['category']
		# check file exist
		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files['file']
		# check fields
		if short_name and name and flairsheet and not Database.get_flair_by_short_name(short_name, False):
			save_image(file, short_name)

			flair = Flair(
				short_name=short_name,
				name=name,
				sheet=flairsheet,
				category=category,
				is_active=faded != 'yes'
			)

			current_app.logger.warning(f"u/{redditname} added flair: {short_name}, {name}, {flairsheet}, {category}, {faded}")

			matrix = make_flair_matrix(flairsheet)
			find_place(matrix, flair)
			Database.add_flair(flair)
			Database.commit()
			return redirect('/flairsheets')
		else:
			return redirect(request.url)

	response_params = dict()
	response_params['redditLink'] = Reddit.auth_link('flairsheets')

	response = make_response(
		render_template(
			'flairnew.html', **response_params, flairsheets=config_data['config']['flair_sheets'],
			categories=config_data['config']['categories']))
	return response


@flair_sheets.route('/flairsheets/makesheets')
def flair_makesheets():
	response_params = dict()
	response_params['redditLink'] = Reddit.auth_link('flairsheets')

	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	reddit_stylesheet = reddit.reddit_css()
	reddit_stylesheet_new = None
	with open('static/flairs.css', 'r') as css_file:
		site_stylesheet = css_file.read()

	dirty_sheets = set()
	for flair in Database.get_dirty_flair():
		dirty_sheets.add(flair.sheet)
		path = 'static/data/flair_images/' + flair.short_name + '.png'
		if not flair.is_active:
			image = Image.open(path)
			image = fade_image(image)
			path = 'static/data/temp_faded.png'
			image.save(path)

		Reddit.upload_emoji(flair.short_name, path)

	# iterate over stylesheets
	for sheet in dirty_sheets:
		matrix = make_flair_matrix(sheet)
		size = make_sheet(matrix, sheet)
		reddit_stylesheet_new = update_stylesheet(
			reddit_stylesheet, sheet, int(size[0] / 2))  # /2 for reddit half resolution
		site_stylesheet = update_stylesheet(site_stylesheet, sheet, size[0], True)
		Reddit.upload_stylesheet_image("flairs-" + sheet)

	# change stylesheets if necessary
	with open('static/flairs.css', 'w') as cssfile:
		cssfile.write(site_stylesheet)

	Reddit.save_stylesheet(reddit_stylesheet_new)

	# make changes permanent on website
	Database.merge_dirty()
	Database.commit()

	# print out the flair json
	flairs_table = {}
	for flair in Database.get_all_flair():
		flairs_table[flair.short_name] = {
			"name": flair.name,
			"col": flair.col,
			"row": flair.row,
			"sheet": flair.sheet,
			"active": flair.is_active,
			"category": flair.category
		}
	with open('static/data/flairs.json', 'w') as flair_data:
		json.dump(flairs_table, flair_data, indent=4)

	current_app.logger.warning(f"u/{redditname} pushed flairsheets")

	return redirect('/flairsheets')


def update_stylesheet(stylesheet, flairsheet, size, timestamp=False):
	i = stylesheet.find('-s' + flairsheet)
	if i < 0:
		return stylesheet
	i1 = stylesheet.find('background-size:', i)
	i2 = stylesheet.find('px', stylesheet.find('px', i1) + 1) + 2
	stylesheet = stylesheet[:i1] + 'background-size: ' + str(size) + 'px ' + str(size) + 'px' + stylesheet[i2:]
	if timestamp:
		i1 = stylesheet.find('flairs-' + flairsheet)
		i2 = stylesheet.find('"', i1)
		stylesheet = stylesheet[:i1] + 'flairs-' + flairsheet + '.png?q=' + str(int(time.time())) + stylesheet[i2:]
	return stylesheet


def make_flair_matrix(sheet):
	# find maximum index
	size = 1
	flairs = Database.get_all_flair(dirty=True)
	for flair in flairs:
		if flair.sheet == sheet and flair.col and flair.row:
			row = int(flair.row)
			col = int(flair.col)
			if row > size:
				size = row
			if col > size:
				size = col
	# create matrix
	matrix = [[None for x in range(size)] for y in range(size)]
	# insert flairs in matrix
	for flair in flairs:
		if flair.sheet == sheet and flair.col and flair.row:
			row = int(flair.row) - 1
			col = int(flair.col) - 1
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


def make_sheet(matrix, sheet):
	path = 'static/data/flairs-' + sheet + '.png'
	# make new spritesheet
	size = (config_data['config']['flair_size'], config_data['config']['flair_size'])
	spritesheet_size = (len(matrix) * size[0], len(matrix) * size[1])
	spritesheet = Image.new('RGBA', spritesheet_size)
	# make spritesheet image
	for row in matrix:
		for flair in row:
			if not flair:
				continue
			# open image
			if not os.path.isfile('static/data/flair_images/' + flair.short_name + '.png'):
				continue
			image = Image.open('static/data/flair_images/' + flair.short_name + '.png')
			image = image.convert('RGBA')
			image.thumbnail(size, Image.ANTIALIAS)
			imageSize = image.size
			# calculate row, column
			row = int(flair.row) - 1
			col = int(flair.col) - 1
			# calculate offset
			offsetX = ((size[0] - imageSize[0]) / 2) + col * size[0]
			offsetY = ((size[1] - imageSize[1]) / 2) + row * size[1]
			offset = (int(offsetX), int(offsetY))
			# faded flair
			if not flair.is_active:
				image = fade_image(image)
			# insert image
			spritesheet.paste(image, offset)
	# output spritesheet
	spritesheet.save(path, quality=95, optimize=True)
	# optimize
	if os.path.getsize(path) > 500000:
		tinify.from_file(path).to_file(path)
	return spritesheet_size
