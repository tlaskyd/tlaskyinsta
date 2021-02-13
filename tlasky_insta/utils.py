import os
import time
from tqdm import tqdm
from datetime import timedelta
from humanize import precisedelta
from instaloader import Instaloader, Post
from typing import Dict, Any, Iterable, List


def multikeys(dct: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    result = dct
    try:
        for key in keys:
            result = result[key]
    except KeyError:
        result = default
    return result


def iterlist(iter: Iterable, n: int = 0) -> List[Any]:
    return list(iter) if not n else [
        next(iter)
        for _ in range(n)
    ]


def wait(t: float):
    i, f = divmod(t, 1)
    delay = 1 + f / i
    description = f'Waiting for {precisedelta(timedelta(seconds=t))}'
    for _ in tqdm(range(int(i)), description):
        time.sleep(delay)


def safe_login(loader: Instaloader, username: str, password: str, session_path: str = './session.pickle'):
    if os.path.exists(session_path):
        loader.load_session_from_file(username, session_path)
    else:
        loader.login(username, password)
    loader.save_session_to_file(session_path)


def post_url(post: Post) -> str:
    return f'https://instagram.com/p/{post.shortcode}'
