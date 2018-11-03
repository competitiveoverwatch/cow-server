from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Database():
    @classmethod
    def set_user(cls, name, battletag=None, psn=None, xbl=None, flair_1=None, flair_2=None, flair_text=None, sr=None, rank=None):
        # fetch from database
        user_object = User.query.filter_by(name=name).first()
        # create user if nonexistent
        if not user_object:
            user_object = User(name)
            db.session.add(user_object)
        
        # update info for given values
        if battletag is not None:
            user_object.battletag = battletag
        if psn is not None:
            user_object.psn = psn
        if xbl is not None:
            user_object.xbl = xbl
        if flair_1 is not None:
            user_object.flair1 = flair_1
        if flair_2 is not None:
            user_object.flair2 = flair_2
        if flair_text is not None:
            user_object.flairtext = flair_text
        if sr is not None:
            user_object.sr = sr
        if rank is not None:
            user_object.rank = rank
        
        db.session.commit()

    @classmethod
    def set_special(cls, name, special_id, text=None):
        # fetch from database
        special_object = Specials.query.filter_by(name=name).filter_by(specialid=special_id).first()
        # create special if nonexistent
        if not special_object:
            special_object = Specials(name)
            db.session.add(special_object)
        
        # update info for given values
        special_object.specialid = special_id
        if text is not None:
            special_object.text = text
       
        db.session.commit()
        
    @classmethod
    def get_user(cls, name):
        user_object = User.query.filter_by(name=name).first()
        specials = Specials.query.filter_by(name=name).all()
        return user_object, specials
    
    @classmethod
    def get_verified_users(cls):
        return Specials.query.filter_by(specialid='verified').all()
        
    @classmethod
    def get_verified_user(cls, name):
        verified_special = Specials.query.filter_by(name=name).filter_by(specialid='verified').first()
        if verified_special:
            return verified_special
        return None
        
    @classmethod
    def get_moderators(cls):
        return Specials.query.filter_by(specialid='moderator').all()
        
    @classmethod
    def check_moderator(cls, name):
        mod_special = Specials.query.filter_by(name=name).filter_by(specialid='moderator').first()
        if mod_special:
            return True
        return False

        
# Models
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20)) # Reddit username - max length is 20
    battletag = db.Column(db.String(12)) # Maximum Battletag length is 12
    blizzardid = db.Column(db.String(60))
    psn = db.Column(db.String(16)) # PSN's max length is 16, XBL's is 15 anyway
    xbl = db.Column(db.String(15))

    flair1 = db.Column(db.String(60))
    flair2 = db.Column(db.String(60))
    flairtext = db.Column(db.String(60))
    sr = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    
    def __init__(self, name, battletag='', psn='', xbl='', flair1='', flair2='', flairtext='', sr=0, rank=0):
        self.name = name
        self.battletag = battletag
        self.psn = psn
        self.xbl = xbl
        self.flair1 = flair1
        self.flair2 = flair2
        self.flairtext = flairtext
        self.sr = sr
        self.rank = rank

        
        
class Specials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialid = db.Column(db.String(60))
    text = db.Column(db.String(60))
    
    def __init__(self, name, specialid='', text=''):
        self.name = name
        self.specialid = specialid
        self.text = text