from instances import *
from instaloader import Profile

user = Profile.from_username(context, 'david_tlaskal')
stories = list(loader.get_stories([user.userid]))[0]
for item in stories.get_items():
    insta.seen_story(stories, item)
