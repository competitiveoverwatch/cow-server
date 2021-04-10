import praw, prawcore

reddit = praw.Reddit("OWMatchThreads", user_agent="test agent")
subreddit = reddit.subreddit("CompetitiveOverwatch")
name = "akron"
try:
    subreddit.emoji.add(name=name, image_path='static/data/flair_images/akron.png')
except prawcore.exceptions.BadRequest:
    print(f"BadRequest uploading emoji {name}, continuing")

