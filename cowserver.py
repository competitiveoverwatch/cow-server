from flask import Flask, url_for
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from redditflair.redditflair import redditflair, limiter
from mod_tools.user_verification import user_verification
from mod_tools.flair_sheets import flair_sheets
from redissession import RedisSessionInterface
from database import db, User, Specials
from werkzeug.utils import secure_filename
import os
import updateScripts

content_security_policy = {
    'style-src': '\'self\''
}

def setupApp():
    app = Flask(__name__)

    # HTTP security headers
    #Talisman(app, content_security_policy=content_security_policy)

    # CSRF library
    SeaSurf(app)

    # Limiter
    limiter.init_app(app)

    # SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cowserver.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Blueprints
    app.register_blueprint(redditflair)
    app.register_blueprint(user_verification)
    app.register_blueprint(flair_sheets)

    # Redis Session Interface
    app.session_interface = RedisSessionInterface()

    return app
    
def setupDatabase():
    if not os.path.isfile('cowserver.db'):
        with app.app_context():
            db.create_all()


app = setupApp()
setupDatabase()

#cache buster
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            if os.path.isfile(file_path):
                values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#updateScripts.databaseToReddit(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # For local HTTPS with cert & key files:
    # app.run(host='0.0.0.0',ssl_context=('cert.pem', 'key.pem'))
