from datetime import datetime, timedelta
from typing import Any, Dict

from metaflow import (
    card,
    conda_base,
    current,
    FlowSpec,
    Parameter,
    project,
    resources,
    step,
)

DATA_DUMP_URL_FORMAT = (
    "https://download.companieshouse.gov.uk/"
    "BasicCompanyData-{:04d}-{:02d}-01-part{:d}_{:d}.zip"
)
DAY_1_OF_LAST_MONTH = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)

# Type aliases
field_name = str
company_number = str


@conda_base(
    libraries={
        "pandas": "1.1.5",
        "pandas-profiling": "3.1.0",
        "requests-cache": "0.4.13",
    }
)
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
        help="Month of Companies House data dump",
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
        """Parse parameters into URL's containing data chunks."""
        ## It is important to **always have a docstring for `start` and `end`**
        ## because their name cannot convey any information about what
        ## the step does when looking at the DAG structure (without the code),
        ## e.g. when using the `show` or `output-dot` commands.
        import logging

        self.urls = [
            DATA_DUMP_URL_FORMAT.format(self.year, self.month, i, self.n_chunks)
            for i in range(1, self.n_chunks + 1)
        ]

        if self.test_mode and not current.is_production:
            self.urls = self.urls[:1]
            logging.warning("TEST MODE: Constraining to first part of data!")

        ## This step forks for each URL
        self.next(self.get_data_chunk, foreach="urls")

    @step
    def get_data_chunk(self):
        ## Due to the atomic nature of the following few steps in this flow,
        ## docstrings would just repeat either/both of the step name or the
        ## docstring of the single functions they tend to call.
        from tempfile import gettempdir

        import requests_cache

        from utils import download_zip, read_companies_house_chunk

        if not current.is_production:
            print("USING REQUESTS CACHE")
            requests_cache.install_cache(f"{gettempdir()}/ch_zip_cache")

        ## Use of `requests_cache` means we need to download the zipfile rather
        ## than giving a URL directly with `pandas.read_csv(..., compression="zip")`
        with download_zip(self.input) as zipfile:
            self.raw = read_companies_house_chunk(zipfile).drop_duplicates()

        ## Each fork (corresponding to one URL chunk), forks a further three times
        self.next(self.process_organisation, self.process_address, self.process_sectors)

    @step
    def process_organisation(self):
        from utils import process_organisations

        self.organisations = process_organisations(self.raw)
        self.next(self.join_branch)

    @step
    def process_address(self):
        from utils import process_address

        self.addresses = process_address(self.raw)
        self.next(self.join_branch)

    @step
    def process_sectors(self):
        from utils import process_sectors

        self.sectors = process_sectors(self.raw)
        self.next(self.join_branch)

    ## Forks must be joined in reverse order
    @step
    def join_branch(self, inputs):
        """Merge artifacts for a single data chunk."""
        self.merge_artifacts(inputs)
        self.next(self.join_foreach)

    ## This step involves loading several large data artifacts; however there
    ## is no way to separate this out into multiple extra steps to minimise RAM
    ## because a join step must resolve all artifacts. The only solution is to
    ## have a big enough machine.
    @card(type="html", options={"attribute": "html_sectors"}, id="Sectors")
    @card(type="html", options={"attribute": "html_organisations"}, id="Organisations")
    @card(type="html", options={"attribute": "html_addresses"}, id="Addresses")
    @resources(memory=32_000)
    @step
    def join_foreach(self, inputs):
        """Merge artifacts of different data chunks together."""
        from pandas import concat
        from pandas_profiling import ProfileReport

        self.organisations = concat(input.organisations for input in inputs)
        self.addresses = concat(input.addresses for input in inputs)
        self.sectors = concat(input.sectors for input in inputs)

        self.merge_artifacts(inputs, exclude=["raw"])

        profile_options = {
            "progress_bar": False,
            "html": {"minify_html": True, "navbar_show": False},
            "correlations": None,
            "interactions": None,
        }
        self.html_sectors = ProfileReport(self.sectors, **profile_options).to_html()
        self.html_organisations = ProfileReport(
            self.organisations, **profile_options
        ).to_html()
        self.html_addresses = ProfileReport(self.addresses, **profile_options).to_html()

        ## It may be more logical to put this conversion from one data type to
        ## another in the `end` step; however because the data artifacts are
        ## large this would involve even more overhead when persisting
        ## artifacts, so we keep it here.
        # Convert artifacts from dataframe to dict
        self.organisations = self.organisations.to_dict()
        self.addresses = self.addresses.to_dict()
        self.sectors = self.sectors.to_dict()

        self.next(self.end)

    ## Join steps have to be distinct, so we can't do the joining logic in `end`
    @step
    def end(self):
        """No-op."""
        pass


if __name__ == "__main__":
    CompaniesHouseDump()
