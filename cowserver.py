from flask import Flask
from rankverification.rankverification import rankverification, limiter
from redissession import RedisSessionInterface

app = Flask(__name__)
limiter.init_app(app)
app.register_blueprint(rankverification)
app.session_interface = RedisSessionInterface()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
