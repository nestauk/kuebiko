"""Data getters for Companies House data."""
from functools import lru_cache
from typing import Dict, Optional

from metaflow import Flow, Run
from metaflow.exception import MetaflowNotFound


# Type aliases
company_number = str
postcode = str
sic_code = str


@lru_cache()
def get_run():
    """Last successful run executed with `--production`."""
    runs = Flow("CompaniesHouseDump").runs("project_branch:prod")
    try:
        return next(filter(lambda run: run.successful, runs))
    except StopIteration as exc:
        raise MetaflowNotFound("Matching run not found") from exc


def company_postcode_lookup(
    run: Optional[Run] = None,
) -> Dict[company_number, postcode]:
    """Lookup from Companies House number to postcode.

    A value of `nan` signals that the Company number was in the dataset but a
    postcode entry was either not present or a valid postcode could not be
    extracted.

    Args:
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from Companies House number to postcode
    """
    if run is None:
        run = get_run()

    return run.data.addresses["postcode"]


## One could implement many getters in a PR along with the metaflow pipeline -
## e.g. getters returning full dataframes for the organisation, address, and
## sector tables; however, unless you know the exact interface required then it
## is better to keep things minimal to avoid having to communicate breaking
## changes when needs become clearer later on.
## In this case, we've implemented two simple getters we're pretty sure are needed.


def company_sic4_lookup(
    run: Optional[Run] = None,
) -> Dict[company_number, sic_code]:
    """Lookup from Companies House number to 4-digit SIC code.

    Args:
        run: Metaflow Run to get data artifacts from

    Returns:
        Lookup from Companies House number to 4-digit SIC code
    """
    ## Look ma, I turned three lines into one!
    ## This change isn't _too_ complex but it's likely less readable to most
    ## which is always something to bear in mind when collaborating.
    return (run or get_run()).data.sectors["SIC4_code"]
