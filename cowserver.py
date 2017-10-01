from flask import Flask
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from rankverification.rankverification import rankverification, limiter
from redissession import RedisSessionInterface

content_security_policy = {
	'script-src': '\'unsafe-inline\'',
	'style-src': '\'self\''
}

app = Flask(__name__)

# HTTP security headers
Talisman(app, content_security_policy=content_security_policy)

# CSRF library
SeaSurf(app)

limiter.init_app(app)
app.register_blueprint(rankverification)
app.session_interface = RedisSessionInterface()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
