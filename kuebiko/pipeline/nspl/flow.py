from typing import Dict

from metaflow import (
    conda_base,
    current,
    FlowSpec,
    Parameter,
    project,
    step,
)


GEOPORTAL_URL_PREFIX = "https://geoportal.statistics.gov.uk/datasets"


## Using separate conda environment because selenium is a ...
@conda_base(
    libraries={
        "pandas": "1.1.0",
        "selenium": "3.141.0",
        "requests-cache": "0.4.13",
    }
)
@project(name="kuebiko")
## A flows docstring is a great place to document (or refer to)
## shortcomings in the data.
class NSPL(FlowSpec):
    """Lookups from postcode to Local Authority Districts and lat-long.

    Uses National Statistics Postcode Lookup (NSPL).
    Excludes postcodes that do not have an assigned output area (OA),
    and therefore no Local Authority District coding.
    Postcodes in the Channel Islands and Isle of Man both have lat-longs of
    `(99.999999, 0.000000)` and have pseudo Local Authorit district codes of
    "L99999999" and "M99999999" respectively, this does not match up with
    other datasets and therefore have been excluded.

    Attributes:
        geoportal_url: Full URL of dataset in gov.uk geoportal
        download_url: Download URL of dataset
        laua_names: Lookup from laua code to name
        laua_year: Year LAUA names and codes correspond to
        pcd_laua: Lookup from postcode to LAUA
        pcd_latlong: Lookup from postcode to latitude and longitude
    """

    geoportal_dataset = Parameter(
        "geoportal-dataset",
        help=f"Name of dataset in URL at {GEOPORTAL_URL_PREFIX}",
        required=True,
        type=str,
        default="national-statistics-postcode-lookup-august-2021",
    )

    test_mode = Parameter(
        "test-mode",
        help="Whether to run in test mode",
        type=bool,
        default=True,
    )

    geoportal_url: str
    download_url: str
    laua_names: Dict[str, str]
    laua_year: int
    pcd_laua: Dict[str, str]
    pcd_latlong: Dict[str, Dict[str, float]]

    @step
    def start(self):
        """Get dynamically rendered download link."""
        from utils import (
            chrome_driver,
            find_download_url,
        )

        self.geoportal_url = f"{GEOPORTAL_URL_PREFIX}/{self.geoportal_dataset}"
        with chrome_driver() as driver:
            self.download_url = find_download_url(driver, self.geoportal_url)

        self.next(self.get_data)

    @step
    def get_data(self):
        """Download zipped NSPL collection, extracting main lookup & LAUA names."""
        import logging

        import requests_cache

        from utils import (
            download_zip,
            extract_laua_year,
            filter_nspl_data,
            read_nspl_data,
            read_laua_names,
        )

        if self.test_mode and not current.is_production:
            nrows = 1_000
            logging.warning(f"TEST MODE: Constraining to first {nrows} rows!")
        else:
            nrows = None

        ## Downloading a large zip each time we iterate is inefficient.
        ## With other expensive tasks we can split them into different
        ## metaflow steps and `resume` part-way through our flow; however
        ## if we download a zip in one step and process it in another then
        ## this requires that the two steps run on the same machine. One of
        ## the big benefits of metaflow is how easy it is to run a pipeline in
        ## a distributed manner.
        ## If you knew the flow would only ever be run locally with all steps
        ## happening on the same machine then it would _probably_ be ok to do
        ## the above. But we can have the best of both worlds by using
        ## `requests_cache` to cache requests for us.
        ## We can also make sure that if the `--production` flag is used then
        ## the file is re-downloaded rather than risking an invalid cache/local copy.
        if not current.is_production:
            requests_cache.install_cache("nspl_zip_cache")
        with download_zip(self.download_url) as zipfile:
            # Load main postcode lookup
            self.nspl_data = read_nspl_data(zipfile, nrows).pipe(filter_nspl_data)

            # LAUA lookup from codes to names
            laua_names_tmp = read_laua_names(zipfile)
            self.laua_year = extract_laua_year(laua_names_tmp)
            self.laua_names = laua_names_tmp.to_dict()
            ## Could have extracted year in `read_laua_names` but we separate
            ## our concerns...

        self.next(self.data_quality)

    @step
    def data_quality(self):
        """Data quality checks."""
        from utils import LOOSE_UK_BOUNDS

        ## It is always important to check data-quality, both during EDA but
        ## also during each workflow run.
        ## We will see some potential better approaches to data quality checks
        ## in a later episode.

        # Null checks
        has_nulls = self.nspl_data.isna().sum().sum() > 0
        if has_nulls:
            raise AssertionError("Nulls detected")

        # Postcode validity
        # Choose very simple postcode verification as NSPL is a fairly
        ## authoritative source that may update faster than a precise regex
        POSTCODE_REGEX = r"^([A-Z]{1,2}[A-Z\d]{0,2}? ?\d[A-Z]{2})$"
        valid_pcds = self.nspl_data.index.str.match(POSTCODE_REGEX)
        if not valid_pcds.all():
            raise AssertionError(
                "Invalid postcodes detected: "
                f"{self.nspl_data.loc[~valid_pcds].index.values}"
            )

        # Check we have names for all laua codes
        nspl_laua_cds = set(self.nspl_data.laua.dropna())
        laua_names_cds = set(self.laua_names.keys())
        laua_diff = nspl_laua_cds - laua_names_cds
        if len(laua_diff) > 0:
            raise AssertionError(f"LAUA do not match: {laua_diff}")

        # Check lat-longs are in the UK
        assert self.nspl_data.lat.between(*LOOSE_UK_BOUNDS["lat"]).all()
        assert self.nspl_data.long.between(*LOOSE_UK_BOUNDS["long"]).all()

        self.next(self.end)

    @step
    def end(self):
        ## Individual lookups reduce the amount of data each getter needs to
        ## download for the price of slightly more serialisation overhead and
        ## storage when the flow is originally run
        self.pcd_laua = self.nspl_data["laua"].to_dict()
        self.pcd_latlong = self.nspl_data[["lat", "long"]].to_dict(orient="index")
        del self.nspl_data  # Don't expose the pandas dataframe as a final artifact


if __name__ == "__main__":
    NSPL()
