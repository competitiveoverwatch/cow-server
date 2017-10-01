# [r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch) Overwatch Rank Verification

## Running
1. `pip3 install -r requirements.txt`
2. [Make sure Redis server is running](https://redis.io/topics/quickstart)
3. Add credentials to `config/creds.json` based on the template in `creds.json.template`
4. Start the server with `python3 cowserver.py`
5. Visit [`http(s)://0.0.0.0:5000/redditflair`](http://0.0.0.0:5000/redditflair) to view the index page

## Notes
* To run the Python Flask server over HTTPS on your local machine, follow [**Self-Signed Certificates** from this guide:](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) [*Running Your Flask Application Over HTTPS*](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)