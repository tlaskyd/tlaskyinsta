from tlasky_insta import TlaskyInsta
from tlasky_insta.utils import safe_login
from instaloader import Instaloader, Profile

from config import usernames_passwords

loader = Instaloader()
context = loader.context
safe_login(
    loader,
    *usernames_passwords[0],
    './david_tlaskal_session.pickle'
)
insta = TlaskyInsta(loader)

user = Profile.from_username(context, 'david_tlaskal')
stories = list(loader.get_stories([user.userid]))[0]
for item in stories.get_items():
    insta.seen_story(stories, item)
