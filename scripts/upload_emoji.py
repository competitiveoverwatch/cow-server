import praw

reddit = praw.Reddit("OWMatchThreads", user_agent="test agent")
subreddit = reddit.subreddit("CompetitiveOverwatch")
subreddit.emoji.add(name="akron", image_path='static/data/flair_images/akron.png')
