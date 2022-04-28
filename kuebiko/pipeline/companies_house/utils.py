"""Companies House data processing."""
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests


COLUMN_MAPPINGS = {
    "CompanyName": "company_name",
    " CompanyNumber": "company_number",
    "URI": "uri",
    "RegAddress.CareOf": "address_careof",
    "RegAddress.POBox": "address_pobox",
    "RegAddress.AddressLine1": "address_line1",
    " RegAddress.AddressLine2": "address_line2",
    "RegAddress.PostCode": "address_postcode",
    "RegAddress.PostTown": "address_town",
    "RegAddress.County": "address_county",
    "RegAddress.Country": "address_country",
    "CompanyCategory": "company_category",
    "CompanyStatus": "company_status",
    "CountryOfOrigin": "country_of_origin",
    "DissolutionDate": "dissolution_date",
    "IncorporationDate": "incorporation_date",
    "SICCode.SicText_1": "sic_1",
    "SICCode.SicText_2": "sic_2",
    "SICCode.SicText_3": "sic_3",
    "SICCode.SicText_4": "sic_4",
}


def download_zip(url: str) -> ZipFile:
    """Download a URL and load into `ZipFile`."""

    ## `download_zip` also exists in the NSPL flow so should probably be a
    ## project-level utility; however we duplicate here for pedagogical simplicity
    response = requests.get(url)
    response.raise_for_status()
    return ZipFile(BytesIO(response.content), "r")


def read_companies_house_chunk(zipfile: ZipFile) -> pd.DataFrame:
    """Read Companies House zipped CSV data-dump from url."""
    n_files = len(zipfile.namelist())
    if n_files != 1:
        raise ValueError(
            f"Expected zipfile {zipfile} to contain 1 file, found {n_files}"
        )

    zip_path = zipfile.namelist()[0]
    return pd.read_csv(zipfile.open(zip_path), usecols=COLUMN_MAPPINGS.keys()).rename(
        columns=COLUMN_MAPPINGS
    )


def process_organisations(ch: pd.DataFrame) -> pd.DataFrame:
    """Split Companies House dataframe into organisation data."""
    return ch[
        [
            "company_number",
            "company_name",
            "company_category",
            "company_status",
            "country_of_origin",
            "dissolution_date",
            "incorporation_date",
            "uri",
        ]
    ].set_index("company_number")


def process_address(ch: pd.DataFrame) -> pd.DataFrame:
    """Split Companies House dataframe into address data."""
    return (
        ch[
            [
                "company_number",
                "address_careof",
                "address_pobox",
                "address_line1",
                "address_line2",
                "address_town",
                "address_county",
                "address_country",
                "address_postcode",
            ]
        ].rename(columns=lambda x: x.replace("address_", ""))
    ).set_index("company_number")


def process_sectors(ch: pd.DataFrame) -> pd.DataFrame:
    """Split Companies House dataframe into sector data."""
    return (
        ch[["company_number", "sic_1", "sic_2", "sic_3", "sic_4"]]
        # Melt SIC ranks
        .melt(
            id_vars=["company_number"],
            value_vars=["sic_1", "sic_2", "sic_3", "sic_4"],
            var_name="rank",
            value_name="SIC5_full",
        )
        .assign(
            # Get rank from column name, e.g. "sic_1"
            rank=lambda x: x["rank"].str.slice(-1).astype(int),
            # Get 4 and 5 digit SIC code from original format "XXXX - Description"
            SIC5_code=lambda x: x["SIC5_full"].str.extract(r"([0-9]*) -"),
            SIC4_code=lambda x: x["SIC5_code"].str.slice(0, 4),
        )
        .dropna(subset=["SIC5_code"])
    ).set_index("company_number")
