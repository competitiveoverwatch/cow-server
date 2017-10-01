# [r/CompetitiveOverwatch](https://reddit.com/r/competitiveoverwatch) Overwatch Rank Verification

## Running
1. `pip3 install -r requirements.txt`
2. [Make sure Redis server is running](https://redis.io/topics/quickstart)
3. Add credentials to `config/creds.json` based on the template in `creds.json.template`
4. Start the server with `python3 cowserver.py`
5. Visit [`http://0.0.0.0:5000/redditflair`](http://0.0.0.0:5000/redditflair) to view the index page