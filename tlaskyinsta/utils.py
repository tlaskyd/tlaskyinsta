import tqdm
import time
import humanize
from typing import *
from datetime import timedelta


def multi_keys(dct: dict, *keys: str) -> Any:
    result = dct
    for key in keys:
        try:
            result = result[key]
        except KeyError:
            return None
    return result


def json_params(params: dict = None) -> Dict[str, Any]:
    params = params or dict()
    params.update({'__a': 1})
    return params


def gen_to_list(gen: Union[Generator, Iterator], n: int = 0) -> List[Any]:
    return list(gen) if n < 0 else [next(gen) for _ in range(n)]


def minutes(seconds: float) -> float:
    return seconds * 60


def hours(seconds: float) -> float:
    return minutes(seconds) * 60


def wait(seconds: float):
    delta = timedelta(seconds=seconds)
    desc = f'Sleeping for {humanize.precisedelta(delta)}...'
    i, f = divmod(seconds, 1)
    delay = 1 + (f / i)
    for _ in tqdm.tqdm(range(int(i)), desc):
        time.sleep(delay)
