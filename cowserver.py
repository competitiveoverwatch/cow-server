from flask import Flask, url_for
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from redditflair.redditflair import redditflair, limiter
from mod_tools.user_verification import user_verification
from mod_tools.flair_sheets import flair_sheets
from redissession import RedisSessionInterface
from database import db, User, Flair
from werkzeug.utils import secure_filename
import os
import logging
import requests
from config import data as config

content_security_policy = {
	'style-src': '\'self\''
}


class WebhookHandler(logging.Handler):
	def __init__(self, webhook):
		super().__init__()
		self.webhook = webhook

	def emit(self, record):
		try:
			message = self.format(record)

			if message is None or message == "":
				return True

			data = {"content": message[:2000]}
			result = requests.post(self.webhook, data=data)

			if not result.ok:
				return False
			return True
		except Exception:
			return False


def setup_app():
	app = Flask(__name__)

	# HTTP security headers
	# Talisman(app, content_security_policy=content_security_policy)

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


def setup_database():
	if not os.path.isfile('cowserver.db'):
		with app.app_context():
			db.create_all()


app = setup_app()
setup_database()
app.logger.setLevel(logging.INFO)

discord_logging_handler = WebhookHandler(config['creds']['loggingWebhook'])
discord_logging_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
discord_logging_handler.setLevel(logging.WARNING)
app.logger.addHandler(discord_logging_handler)


# cache buster
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


if __name__ == '__main__':
	app.run(host='0.0.0.0')
	# For local HTTPS with cert & key files:
	# app.run(host='0.0.0.0',ssl_context=('cert.pem', 'key.pem'))
