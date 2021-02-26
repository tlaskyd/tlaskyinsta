from instaloader import Instaloader
from tlasky_insta import TlaskyInsta
from tlasky_insta.utils import safe_login

from config import usernames_passwords

if __name__ == '__main__':
    print('This file is used as base for test_* and script_*. It\'s not intended to be run on it\'s own.')
    exit()

loader = Instaloader()
safe_login(
    loader,
    *usernames_passwords[0],
    './david_tlaskal_session.pickle'
)
context = loader.context
insta = TlaskyInsta(loader)
