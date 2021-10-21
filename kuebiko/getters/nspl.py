"""Data getters providing lookups from postcode to various geographies."""
from functools import lru_cache
from typing import Dict, Literal, Optional

from metaflow import Flow, Run
from metaflow.exception import MetaflowNotFound


# Type aliases
postcode = str
laua_name = str
laua_code = str


@lru_cache()
## This is exactly the same function we wrote for the SIC getter but with a
## different flow name. In order to keep things [DRY](/kuebiko/glossary/#DRY),
## this would ideally be factored out into a utility function!
def get_run():
    """Last successful run executed with `--production`."""
    runs = Flow("NsplLookup").runs("project_branch:prod")
    try:
        return next(filter(lambda run: run.successful, runs))
    except StopIteration as exc:
        raise MetaflowNotFound("Matching run not found") from exc


## The following getters also contain a lot of repetition, a sign that more
## utility functions may be needed. In the case of getters we need to balance
## keeping things DRY with being explicit - a little repetition is better than
## making it harder for someone to see what data is available.
## You'd have to be a bit bonkers to think the following was worth the trade-off...
## ```python
## def dynamically_generate_getter(artifact):
##     def inner(run: Optional[Run] = None):
##         if run is None:
##             run = get_run()
##         return getattr(run.data, artifact)
##     return inner
##
## functions = [
##     "postcode_laua_lookup",
##     "postcode_latlong_lookup",
##     "laua_code_names_lookup",
## ]
## artifacts = ["pcd_laua", "pcd_latlong", "laua_names"]
## for function, artifact in zip(functions, artifacts):
##     f = dynamically_generate_getter(artifact)
##     locals()[function] = f
## ```


def postcode_laua_lookup(run: Optional[Run] = None) -> Dict[postcode, laua_code]:
    """Lookup from postcode to Local Authority.

    Args:
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from postcode to Local Authority code
    """
    if run is None:
        run = get_run()

    return run.data.pcd_laua


def postcode_latlong_lookup(
    run: Optional[Run] = None,
) -> Dict[postcode, Dict[Literal["lat", "long"], float]]:
    """Lookup from postcode to Latitude and Longitude.

    Args:
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from postcode to lat-long
    """
    if run is None:
        run = get_run()

    return run.data.pcd_latlong


def laua_code_names_lookup(run: Optional[Run] = None) -> Dict[laua_code, laua_name]:
    """Lookup from Local Authority code to Local Authority name.

    Args:
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from Local Authority code to name
    """
    if run is None:
        run = get_run()

    return run.data.laua_names
