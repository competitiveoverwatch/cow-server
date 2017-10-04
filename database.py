from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30))
	battletag = db.Column(db.String(30))
	blizzardid = db.Column(db.String(30))
	psn = db.Column(db.String(30))
	xbl = db.Column(db.String(30))
	flair1 = db.Column(db.String(30))
	flair2 = db.Column(db.String(30))
	sr = db.Column(db.Integer)
	rank = db.Column(db.Integer)
	
	def __init__(self, name, battletag='', psn='', xbl='', flair1='', flair2='', sr=0, rank=0):
		self.name = name
		self.battletag = battletag
		self.psn = psn
		self.xbl = xbl
		self.flair1 = flair1
		self.flair2 = flair2
		self.sr = sr
		self.rank = rank