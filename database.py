from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# Reddit username - max length is 20
	name = db.Column(db.String(20))
	# Maximum Battletag length is 12
	battletag = db.Column(db.String(12))
	blizzardid = db.Column(db.String(60))
	# PSN's max length is 16, XBL's is 15
	psn = db.Column(db.String(16))
	xbl = db.Column(db.String(15))

	flair1 = db.Column(db.String(60))
	flair2 = db.Column(db.String(60))
	flairtext = db.Column(db.String(60))
	sr = db.Column(db.Integer)
	rank = db.Column(db.Integer)
	
	def __init__(self, name, battletag='', psn='', xbl='', flair1='', flair2='', flairtext='', blizzard='', verified='', sr=0, rank=0):
		self.name = name
		self.battletag = battletag
		self.psn = psn
		self.xbl = xbl
		self.flair1 = flair1
		self.flair2 = flair2
		self.flairtext = flairtext
		self.blizzard = blizzard
		self.verified = verified
		self.sr = sr
		self.rank = rank
		
class Specials(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.Integer)
	specialid = db.Column(db.String(60))
	text = db.Column(db.String(60))
	
	def __init__(self, userid, specialid='', text=''):
		self.userid = userid
		self.specialid = specialid
		self.text = text