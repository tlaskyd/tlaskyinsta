from pprint import pprint
from instaloader import Instaloader
from tlasky_insta import TlaskyInsta
from tlasky_insta.utils import safe_login

from config import usernames_passwords

loader = Instaloader()
safe_login(
    loader,
    *usernames_passwords[0],
    './david_tlaskal_session.pickle'
)
insta = TlaskyInsta(loader)

response = insta.session.get(
    'https://i.instagram.com/api/v1/direct_v2/get_presence/'
)
pprint(response.text)
