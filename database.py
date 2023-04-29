from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from config import data as config

db = SQLAlchemy()


class Database:
	@classmethod
	def get_or_add_user(cls, user_name):
		user = db.session.query(User).filter_by(name=user_name).first()
		if user is None:
			user = User(user_name)
			db.session.add(user)

		return user

	@classmethod
	def commit(cls):
		db.session.commit()

	@classmethod
	def get_verified_users(cls):
		return db.session.query(User).filter_by(special_id='verified').order_by(User.name).all()

	@classmethod
	def check_moderator(cls, name):
		mod_special = db.session.query(User).filter_by(name=name).filter_by(is_mod=True).first()
		if mod_special:
			return True
		return False

	@classmethod
	def add_flair(cls, flair):
		db.session.add(flair)

	@classmethod
	def get_flair(cls, flair_id):
		return db.session.query(Flair).filter_by(id=flair_id).first()

	@classmethod
	def get_flair_by_short_name(cls, short_name, temp=False):
		return db.session.query(Flair).filter_by(short_name=short_name).filter_by(is_dirty=temp).first()

	@classmethod
	def get_all_flair(cls, dirty=False):
		if dirty:
			flairs = Database.get_clean_flair()
			flairs.extend(Database.get_dirty_flair())
			return flairs

		else:
			return db.session.query(Flair).filter_by(is_dirty=False).order_by(Flair.short_name).all()

	@classmethod
	def get_dirty_flair(cls):
		return db.session.query(Flair).filter_by(is_dirty=True).order_by(Flair.short_name).all()

	@classmethod
	def get_clean_flair(cls):
		subquery = db.session.query(Flair.short_name).filter_by(is_dirty=True)
		return db.session.query(Flair).filter_by(is_dirty=False).filter(Flair.short_name.notin_(subquery))\
			.order_by(Flair.short_name).all()

	@classmethod
	def get_flair_by_category(cls, include_hidden=False):
		categories = defaultdict(list)
		for flair in Database.get_all_flair():
			if flair.category != "hidden" or include_hidden:
				categories[flair.category].append(flair)

		return categories

	@classmethod
	def merge_dirty(cls):
		for flair in Database.get_dirty_flair():
			old_flair = Database.get_flair_by_short_name(flair.short_name, False)
			if old_flair is not None:
				db.session.delete(old_flair)
				db.session.commit()
			flair.is_dirty = False

	@classmethod
	def clone_flair(cls, orig_flair):
		table = orig_flair.__table__
		non_pk_columns = [k for k in table.columns.keys() if k not in table.primary_key]
		data = {c: getattr(orig_flair, c) for c in non_pk_columns}

		clone_flair = orig_flair.__class__(**data)
		clone_flair.is_dirty = True
		db.session.add(clone_flair)
		return clone_flair


# Models

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))  # Reddit username - max length is 20

	battletag = db.Column(db.String(12))  # Maximum Battletag length is 12
	blizzardid = db.Column(db.String(60))
	psn = db.Column(db.String(16))  # PSN's max length is 16, XBL's is 15 anyway
	xbl = db.Column(db.String(15))

	flair1 = db.Column(db.String(60))
	flair2 = db.Column(db.String(60))
	flairtext = db.Column(db.String(60))
	sr = db.Column(db.Integer)
	rank = db.Column(db.Integer)

	is_mod = db.Column(db.Boolean)
	special_id = db.Column(db.String(60))
	special_text = db.Column(db.String(60))

	def __init__(self, name, battletag='', psn='', xbl='', flair1='', flair2='', flairtext='', sr=0, rank=0, is_mod=False, special_id=None, special_text=None):
		self.name = name
		self.battletag = battletag
		self.psn = psn
		self.xbl = xbl
		self.flair1 = flair1
		self.flair2 = flair2
		self.flairtext = flairtext
		self.sr = sr
		self.rank = rank
		self.is_mod = is_mod
		self.special_id = special_id
		self.special_text = special_text


class Flair(db.Model):
	__table_args__ = (db.UniqueConstraint('short_name', 'is_dirty'),)

	id = db.Column(db.Integer, primary_key=True)

	short_name = db.Column(db.String(64))
	name = db.Column(db.String(64))
	sheet = db.Column(db.String(20))
	category = db.Column(db.String(20))
	col = db.Column(db.String(2))
	row = db.Column(db.String(2))
	is_active = db.Column(db.Boolean)

	is_dirty = db.Column(db.Boolean)

	def __init__(self, short_name, name, sheet, category, is_active=True, col=None, row=None, is_dirty=True):
		self.short_name = short_name
		self.name = name
		self.sheet = sheet
		self.category = category
		self.is_active = is_active

		self.col = col
		self.row = row
		self.is_dirty = is_dirty
