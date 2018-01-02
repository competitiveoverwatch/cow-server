from flask import Flask
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from redditflair.redditflair import redditflair, limiter
from mod_tools.user_verification import user_verification
from redissession import RedisSessionInterface
from database import db, User, Specials
import os.path
import updateScripts

content_security_policy = {
    'script-src': '\'unsafe-inline\'',
    'style-src': '\'self\''
}

def setupApp():
    app = Flask(__name__)

    # HTTP security headers
    Talisman(app, content_security_policy=content_security_policy)

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

    # Redis Session Interface
    app.session_interface = RedisSessionInterface()

    return app
    
def setupDatabase():
    if not os.path.isfile('cowserver.db'):
        with app.app_context():
            db.create_all()


app = setupApp()
setupDatabase()

#updateScripts.databaseToReddit(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # For local HTTPS with cert & key files:
    # app.run(host='0.0.0.0',ssl_context=('cert.pem', 'key.pem'))
