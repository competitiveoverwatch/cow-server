# [r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch) Overwatch Rank Verification

## Prerequisites
* API keys for Reddit and Blizzard to start the server locally (for the UI and most functions)
* Credentials for a Reddit bot account for production
* Redis server ([see *Redis Quick Start*](https://redis.io/topics/quickstart))
* For HTTPS on your local machine, follow [**Self-Signed Certificates** from *Running Your Flask Application Over HTTPS*](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)

## Running
1. `pip3 install -r requirements.txt`
2. Start the server with `python3 cowserver.py`
3. Visit [`http(s)://0.0.0.0:5000/redditflair`](http://0.0.0.0:5000/redditflair) to view the index page