from typing import Union, List

session_path = './session.pickle'
username, password = 'your username', 'your password'
debug = False

interests: List[Union[str, int]] = list()
interests.extend('nature czechnature czechgirl slovaknature slovakgirl'.split())
interests.extend([
    244516490,  # CZ
    261698127,  # SK
    108100019211318,  # DE
])
