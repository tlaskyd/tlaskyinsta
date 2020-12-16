import os
from instaloader import Instaloader

username, password = 'your username', 'your password'
session_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    f'{username}.pickle'
)

loader = Instaloader()

if os.path.isfile(session_file):
    loader.load_session_from_file(session_file)
else:
    loader.login(username, password)
    loader.save_session_to_file(session_file)
