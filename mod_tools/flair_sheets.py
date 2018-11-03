from flask import Blueprint, make_response, render_template, session, redirect, request, url_for, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redditflair.reddit as reddit
from redditflair.reddit import Reddit
import redditflair.blizzard as blizzard
from redditflair.parse import parseOWProfile
from config import set_flairdata, get_flairdata
from config import data as config
from database import db, User, Specials, Database
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
import os, collections, json, sys, tinify, zipfile, copy

flair_sheets = Blueprint('flair_sheets', __name__)
ALLOWED_EXTENSIONS = set(['png'])
tinify.key = config['creds']['tinifyKey']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@flair_sheets.route('/flairsheets')
def flairSheets():
    flairdata = get_flairdata(True)

    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairsheets')

    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True

    # gather flairs
    flairs = collections.OrderedDict(sorted(flairdata['flairs'].items()))

    response = make_response(render_template('flairsheets.html', **responseParams, mod = mod, flairs = flairs))
    return response

@flair_sheets.route('/flairsheets/edit/<id>', methods=['GET', 'POST'])
def flairEdit(id):
    flairdata = get_flairdata(True)

    if id not in flairdata['flairs']:
        return redirect('/flairsheets')
    flair = flairdata['flairs'][id]

    if request.method == 'POST':
        name = request.form['name']
        faded = request.form['faded']
        categories = request.form.getlist('categories')
        if name:
            # update flair and json
            flair['name'] = name
            if faded == 'yes':
                flair['active'] = False
            else:
                flair['active'] = True
            flairdata['flairs'][id] = flair
            # update categories
            for i in range(len(flairdata['categories'])):
                c = flairdata['categories'][i]
                if c['title'] in categories:
                    if id not in c['items']:
                        c['items'].append(id)
                else:
                    if id in c['items']:
                        c['items'].remove(id)
                c['items'].sort()
            set_flairdata(flairdata, True)
            # Upload image if necessary
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = id + '.png'
                    file.save(os.path.join('static/flair_images', filename))
    
    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairsheets')

    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True

    response = make_response(render_template('flairedit.html', **responseParams, mod = mod, id = id, flair = flair, flairsheets = config['config']['flair_sheets'], categories = flairdata['categories']))
    return response

@flair_sheets.route('/flairsheets/new', methods=['GET', 'POST'])
def flairNew():
    flairdata = get_flairdata(True)

    # process request
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        flairsheet = request.form['flairsheet']
        faded = request.form['faded']
        categories = request.form.getlist('categories')
        # check file exist
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # check fields
        if (id) and (name) and (flairsheet) and (id not in flairdata['flairs']) and (file.filename != ''):
            #check file
            if file and allowed_file(file.filename):
                #upload
                filename = id + '.png'
                file.save(os.path.join('static/flair_images', filename)) 

                #add to flair json and update flairdata
                flair = dict()
                flair['name'] = name
                flair['sheet'] = flairsheet
                if faded == 'yes':
                    flair['active'] = False
                else:
                    flair['active'] = True
                matrix = makeFlairMatrix(flairsheet)
                flair = findPlace(matrix, flair, id)
                flairdata['flairs'][id] = flair
                # update categories
                for i in range(len(flairdata['categories'])):
                    c = flairdata['categories'][i]
                    if c['title'] in categories:
                        if id not in c['items']:
                            c['items'].append(id)
                    else:
                        if id in c['items']:
                            c['items'].remove(id)
                    c['items'].sort()
                set_flairdata(flairdata, True)
                return redirect('/flairsheets/edit/'+id)
        else:
            return redirect(request.url)
        
    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairsheets')

    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True

    response = make_response(render_template('flairnew.html', **responseParams, mod = mod, flairsheets = config['config']['flair_sheets'], categories = flairdata['categories']))
    return response


@flair_sheets.route('/flairsheets/makesheets')
def flairMakesheets():
    flairdata = get_flairdata(True)

    responseParams = dict()
    responseParams['redditLink'] = Reddit.auth_link('flairsheets')

    # moderator check
    redditname = session.get('redditname')
    mod = False
    if redditname:
        if not Database.check_moderator(redditname):
            return redirect('/redditflair')
        mod = True

    change = False
    reddit_stylesheet = reddit.redditCSS()
    with open('static/flairs.css', 'r') as cssfile:
        site_stylesheet = cssfile.read()
    #iterate over stylesheets
    for sheet in config['config']['flair_sheets']:
        matrix = makeFlairMatrix(sheet)
        size = makeSheet(matrix, sheet)
        reddit_stylesheet_new = updateStylesheet(reddit_stylesheet, sheet, int(size[0]/2)) # /2 for reddit half resolution
        site_stylesheet = updateStylesheet(site_stylesheet, sheet, size[0])
    # change stylesheets if necessary
    with open('static/flairs.css', 'w') as cssfile:
            cssfile.write(site_stylesheet)
    if reddit_stylesheet_new == reddit_stylesheet:
        reddit_stylesheet_new = None

    # make changes permanent on website
    set_flairdata(flairdata)
    set_flairdata(flairdata, True)

    # create flairsheets zip
    with zipfile.ZipFile('static/flairsheets.zip', 'w') as flairsheetzip:
        for sheet in config['config']['flair_sheets']:
            flairsheetzip.write('static/flairs-' + sheet + '.png')

    response = make_response(render_template('makesheets.html', **responseParams, mod = mod, flairsheets = config['config']['flair_sheets'], reddit_stylesheet = reddit_stylesheet_new))
    return response

def updateStylesheet(stylesheet, flairsheet, size):
    i = stylesheet.find('-s' + flairsheet)
    if i < 0:
        return stylesheet
    i1 = stylesheet.find('background-size:', i)
    i2 = stylesheet.find('px', stylesheet.find('px', i1) + 1) + 2 
    return stylesheet[:i1] + 'background-size: ' + str(size) + 'px ' + str(size) + 'px' + stylesheet[i2:]

def makeFlairMatrix(sheet):
    flairdata = get_flairdata(True)
    # find maximum index
    size = 1
    flairlist = flairdata['flairs']
    for id, flair in flairlist.items():
        if flair['sheet'] == sheet:
            row = int(flair['row'])
            col = int(flair['col'])
            if row > size:
                size = row
            if col > size:
                size = col
    # create matrix
    matrix = [[None for x in range(size)] for y in range(size)] 
    # insert flairs in matrix
    for id, flair in flairlist.items():
        if flair['sheet'] == sheet:
            row = int(flair['row']) - 1
            col = int(flair['col']) - 1
            matrix[row][col] = id
    return matrix
            
def findPlace(matrix, flair, id):
    found_place = False
    for row in range(len(matrix)):
        for col in range(len(matrix)):
            if matrix[row][col] == None:
                flair['col'] = '%02d' % (col + 1)
                flair['row'] = '%02d' % (row + 1)
                matrix[row][col] = id
                found_place = True
                break
        if found_place:
            break
    # increase size if no space
    if not found_place:
        for row in matrix:
            row.extend([None])
        matrix.extend([[None] * (len(matrix) + 1)])
        flair['col'] = '%02d' % len(matrix)
        flair['row'] = '01'
        matrix[0][len(matrix)-1] = id
    return flair

def makeSheet(matrix, sheet):
    flairdata = get_flairdata(True)
    path = 'static/flairs-' + sheet + '.png'
    # make new spritesheet
    size = (config['config']['flair_size'],config['config']['flair_size'])
    spritesheet_size = (len(matrix)*size[0],len(matrix)*size[1])
    spritesheet = Image.new('RGBA', spritesheet_size)
    # make spritesheet image
    for row in matrix:
        for id in row: 
            if not id:
                continue
            flair = flairdata['flairs'][id]
            # open image
            if not os.path.isfile('static/flair_images/' + id + '.png'):
                continue
            image = Image.open('static/flair_images/' + id + '.png')
            image = image.convert('RGBA')
            image.thumbnail(size, Image.ANTIALIAS)
            imageSize = image.size
            # calculate row, column
            row = int(flair['row']) - 1
            col = int(flair['col']) - 1
            # calculate offset
            offsetX = ((size[0] - imageSize[0]) / 2)  +  col * size[0]
            offsetY = ((size[1] - imageSize[1]) / 2)  +  row * size[1]
            offset = (int(offsetX), int(offsetY)) 
            # faded flair
            if not flair['active']:
                # desaturate
                colorConverter = ImageEnhance.Color(image)
                image = colorConverter.enhance(0.2)
                # 50% transparency
                bands = list(image.split())
                if len(bands) == 4:
                    # Assuming alpha is the last band
                    bands[3] = bands[3].point(lambda x: x*0.5)
                image = Image.merge(image.mode, bands)
            # insert image
            spritesheet.paste(image, offset)
    # output spritesheet
    spritesheet.save(path, quality=95, optimize=True)
    # optimize
    if os.path.getsize(path) > 500000:
        tinify.from_file(path).to_file(path)
    return spritesheet_size
