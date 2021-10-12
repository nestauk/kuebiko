from datetime import datetime, timedelta
from typing import Any, Dict

from metaflow import conda_base
from metaflow import current, FlowSpec, Parameter, project, resources, step

DATA_DUMP_URL_FORMAT = (
    "https://download.companieshouse.gov.uk/"
    "BasicCompanyData-{:04d}-{:02d}-01-part{:d}_{:d}.zip"
)
DAY_1_OF_LAST_MONTH = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)

# Type aliases
field_name = str
company_number = str


## Local (max-workers 4): 5m30s
## S3 (max-workers 4): 21m
## Would likely be somewhere between the two running on AWS batch (which
## requires the S3 datastore) depending on factors such as the number of
## simultaneous workers and how fast the jobs start.


@conda_base(libraries={"pandas": "1.3.3", "toolz": "0.11.1"})
@project(name="kuebiko")
class CompaniesHouseDump(FlowSpec):
    """Companies House monthly data dump.

    More information on the data product can be found here:
    https://download.companieshouse.gov.uk/en_output.html

    It is important to note that Companies House adds custom codes alongside SIC:
    - 74990 - Non-trading company
    - 98000 - Residents property management
    - 99999 - Dormant company

    Attributes:
        urls: URLs of data dump downloads
        metadata: Metadata about data artifacts
        organisations: General information about each organisation
        addresses: Address information for each organisation
        sectors: Sector (SIC code) information each organisation
    """

    metadata: Dict[str, Any]
    organisations: Dict[field_name, Dict[company_number, Any]]
    addresses: Dict[field_name, Dict[company_number, Any]]
    sectors: Dict[field_name, Dict[company_number, Any]]

    test_mode = Parameter(
        "test-mode",
        help="Whether to run in test mode (on a small subset of data)",
        type=bool,
        default=True,
    )

    month = Parameter(
        "month",
        help="month of Companies House data dump",
        type=int,
        default=DAY_1_OF_LAST_MONTH.month,
    )

    year = Parameter(
        "year",
        help="Year of Companies House data dump",
        type=int,
        default=DAY_1_OF_LAST_MONTH.year,
    )

    n_chunks = Parameter(
        "n-chunks",
        help="Number of chunks Companies House data dump is split into",
        type=int,
        default=6,
    )

    @step
    def start(self):
        """Load raw data"""
        import logging

        self.urls = [
            DATA_DUMP_URL_FORMAT.format(self.year, self.month, i, self.n_chunks)
            for i in range(1, self.n_chunks + 1)
        ]

        if self.test_mode and not current.is_production:
            self.urls = self.urls[:1]
            logging.warning("TEST MODE: Constraining to first part of data!")

        self.next(self.get_data, foreach="urls")

    @step
    def get_data(self):
        """Fetch data chunk into Dataframe."""
        from pandas import read_csv

        from utils import COLUMN_MAPPINGS

        self.raw = (
            read_csv(self.input, usecols=COLUMN_MAPPINGS.keys(), compression="zip")
            .rename(columns=COLUMN_MAPPINGS)
            .drop_duplicates()
        )  # TODO refactor
        self.next(self.do_organisation, self.do_address, self.do_sectors)

    @step
    def do_organisation(self):
        """Process organisations"""
        from utils import process_organisations

        self.organisations = process_organisations(self.raw)
        self.next(self.join_branch)

    @step
    def do_address(self):
        """Process addresses"""
        from utils import process_address

        self.addresses = process_address(self.raw)
        self.next(self.join_branch)

    @step
    def do_sectors(self):
        """Process sectors"""
        from utils import process_sectors

        self.sectors = process_sectors(self.raw)
        self.next(self.join_branch)

    @step
    def join_branch(self, inputs):
        self.merge_artifacts(inputs)
        self.next(self.join_foreach)

    @resources(memory=16_000)
    ## No way to separate this out into multiple extra steps to minimise RAM
    ## because a join step must resolve all artifacts. The only solution is to
    ## have a big enough machine.
    @step
    def join_foreach(self, inputs):
        from pandas import concat

        self.organisations = concat(input.organisations for input in inputs)
        self.addresses = concat(input.addresses for input in inputs)
        self.sectors = concat(input.sectors for input in inputs)

        self.merge_artifacts(inputs, exclude=["raw"])

        ## We can save metadata such as dataframe lengths as an artifact, which
        ## can come in useful for debugging/monitoring/experiment tracking
        self.metadata = {
            "lengths": {
                "organisations": self.organisations.shape,
                "addresses": self.addresses.shape,
                "sectors": self.sectors.shape,
                ## Whether DRY is a good idea is subjective here, is the
                ## decreased readability of the following worth it?
                ## ```python
                ## attr: getattr(self, attr).shape
                ## for attr in ["organisations", "addresses", "sectors"]
                ## ```
            }
        }
        print(self.metadata)

        # Convert artifacts from dataframe to dict
        self.organisations = self.organisations.to_dict()
        self.addresses = self.addresses.to_dict()
        self.sectors = self.sectors.to_dict()

        self.next(self.end)

    @step
    def end(self):
        """No-op."""
        pass


if __name__ == "__main__":
    CompaniesHouseDump()
