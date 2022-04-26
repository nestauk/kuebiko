import json
from functools import lru_cache
from typing import Iterable, Iterator, List, Optional, Tuple

from metaflow import Flow, Run, S3
from metaflow.exception import MetaflowNotFound

from . import cache


@lru_cache()
def get_run():
    """Last successful run executed with `--production`."""
    ## `project_branch:prod` is the tag corresponding to running a flow with
    ## the `--production` flag. Without `--production` the equivalent tag
    ## relates to your username, e.g. `project_branch:user.alex`.
    runs = Flow("UkBusinessHomepageScrape").runs("project_branch:prod")
    try:
        return next(filter(lambda run: run.successful, runs))
    except StopIteration as exc:
        raise MetaflowNotFound("Matching run not found") from exc


def _get_page_data(run: Optional[Run] = None) -> Iterator[list]:
    run = run or get_run()
    keys = run.data.keys

    ## Store in cache (defined in `__init__.py`) for a day
    @cache.memoize(tag=f"{run.pathspec}/keys", expire=86_400)
    def cache_current_chunk(key):
        print("KEY:", key)
        return json.loads(s3.get(key).text)

    ## Stream chunks as requested
    for key in keys:
        with S3(run=run) as s3:
            yield from cache_current_chunk(key=key)


def get_page_source(run: Optional[Run] = None) -> Iterable[Tuple[str, str]]:
    """Get (URL, page source) pairs."""
    run = run or get_run()
    return map(lambda x: (x[0], x[1]), _get_page_data(run))


def get_page_network_data(run: Optional[Run] = None) -> List[Tuple[str, List[dict]]]:
    """Get (URL, network data) pairs."""
    run = run or get_run()
    return list(map(lambda x: (x[0], x[2]), _get_page_data(run)))
