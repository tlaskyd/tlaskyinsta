import os
from instaloader import Instaloader, Post
from typing import Dict, Any, Iterator, List


def multikeys(dct: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    result = dct
    try:
        for key in keys:
            result = result[key]
    except KeyError:
        result = default
    return result


def iterlist(iterable: Iterator, n: int = 0) -> List[Any]:
    return list(iterable) if not n else [
        next(iterable)
        for _ in range(n)
    ]


def safe_login(loader: Instaloader, username: str, password: str, session_path: str = './session.pickle'):
    if os.path.exists(session_path):
        loader.load_session_from_file(username, session_path)
    else:
        loader.login(username, password)
    loader.save_session_to_file(session_path)


def post_url(post: Post) -> str:
    return f'https://instagram.com/p/{post.shortcode}'
