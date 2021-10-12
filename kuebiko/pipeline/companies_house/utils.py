"""Companies House data processing."""
import pandas as pd


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


def process_organisations(ch: pd.DataFrame) -> pd.DataFrame:
    """"""
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


def process_address(ch: pd.DataFrame):  # , nspl: pd.DataFrame) -> pd.DataFrame:
    """ """
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
        # .merge(nspl, on="postcode")
    ).set_index("company_number")


def process_sectors(ch: pd.DataFrame) -> pd.DataFrame:
    """ """
    return (
        ch[["company_number", "sic_1", "sic_2", "sic_3", "sic_4"]]
        .melt(
            id_vars=["company_number"],
            value_vars=["sic_1", "sic_2", "sic_3", "sic_4"],
            var_name="rank",
            value_name="SIC5_full",
        )
        .assign(
            rank=lambda x: x["rank"].str.slice(-1).astype(int),
            SIC5_code=lambda x: x["SIC5_full"].str.extract(r"([0-9]*) -"),
            SIC4_code=lambda x: x["SIC5_code"].str.slice(0, 4),
        )
        .dropna(subset=["SIC5_code"])
    ).set_index("company_number")
