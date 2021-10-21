"""Script version of Companies House flow used for simple benchmarking purposes."""
import logging

from pandas import concat

from flow import DATA_DUMP_URL_FORMAT, DAY_1_OF_LAST_MONTH  # noqa: I
from utils import (
    process_address,
    process_organisations,
    process_sectors,
    read_from_url,
)

## There's a lot less boilerplate when we write our flow as a plain Python
## script. **But** you lose a lot:
##
## - There's no documentation
## - It's not parameterisable
## - It can't run in parallel
## - There's no way to share results
## - It's harder to debug and resume from a checkpoint
## - It doesn't automatically produce a diagram of our pipeline
if __name__ == "__main__":
    month = DAY_1_OF_LAST_MONTH.month
    year = DAY_1_OF_LAST_MONTH.year
    n_chunks = 6

    urls = [
        DATA_DUMP_URL_FORMAT.format(year, month, i, n_chunks)
        for i in range(1, n_chunks + 1)
    ]

    organisations = {}
    addresses = {}
    sectors = {}
    for url in urls:
        logging.info(f"Processing chunk: {url}")
        raw = read_from_url(url)
        organisations[url] = process_organisations(raw)
        addresses[url] = process_address(raw)
        sectors[url] = process_sectors(raw)

    logging.info("Concatenating chunks")
    organisations = concat(organisations.values()).to_dict()
    addresses = concat(addresses.values()).to_dict()
    sectors = concat(sectors.values()).to_dict()
