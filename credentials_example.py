import os

username, password = 'your username', 'your password'
session_filepath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    f'{username}.json'
)
