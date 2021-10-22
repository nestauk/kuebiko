"""Data getters for SIC taxonomy."""
from functools import lru_cache
from typing import Dict, Optional

from metaflow import Flow, Run
from metaflow.exception import MetaflowNotFound

from kuebiko.pipeline.sic.utils import LEVELS

# Type aliases
code_name = str
code = str


## Examining past runs involves making network requests and database queries,
## caching means that we only need to pay this cost once.
@lru_cache()
def get_run():
    """Last successful run executed with `--production`."""
    ## `project_branch:prod` is the tag corresponding to running a flow with
    ## the `--production` flag. Without `--production` the equivalent tag
    ## relates to your username, e.g. `project_branch:user.alex`.
    runs = Flow("Sic2007Structure").runs("project_branch:prod")
    try:
        return next(filter(lambda run: run.successful, runs))
    except StopIteration as exc:
        raise MetaflowNotFound("Matching run not found") from exc


## Returning the latest successful run,
## e.g. `Flow("Sic2007Structure").latest_successful_run`,
## is incredibly flexible because it allows the user to select whatever
## [namespace](https://docs.metaflow.org/metaflow/tagging#namespaces)
## they want. This means they could either use these getters for development
## (using their own namespace) or production. On the other hand, a user
## could forget to choose the production namespace and use the wrong data.
## For this reason, we recommend:
##
## - Using [`@project`](https://docs.metaflow.org/
## going-to-production-with-metaflow/
## coordinating-larger-metaflow-projects#the-project-decorator)
##   on a Flow
## - Have `kuebiko/__init__.py` choose the project's namespace -
##  `metaflow.namespace("project:kuebiko")` in this case
## - Write getters that fetch 'production' artifacts but are extensible
##
## The following getter is one such example. It's default behaviour is to
## fetch the latest successful production run but a user can pass in their
## own `Run` object if the need arises (during development, testing, or debugging).
def level_lookup(level: int, run: Optional[Run] = None) -> Dict[code, code_name]:
    """Get SIC names for `level` index.

    Args:
        level: Number of SIC digits/letters to fetch lookup for
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from SIC code to name

    Raises:
        ValueError: if 1 <= level <= 5
    """
    if run is None:
        run = get_run()

    if level not in range(1, len(LEVELS) + 1):
        raise ValueError(f"Level: {level} not valid.")

    return getattr(run.data, f"{LEVELS[level - 1]}_lookup")
