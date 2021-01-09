import time
from tqdm import tqdm
from datetime import timedelta
from humanize import precisedelta
from typing import Dict, Any, Iterable, List


def multikeys(dct: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    result = dct
    try:
        for key in keys:
            result = result[key]
    except KeyError:
        result = default
    return result


def iterlist(iter: [Iterable], n: int = 0) -> List[Any]:
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
