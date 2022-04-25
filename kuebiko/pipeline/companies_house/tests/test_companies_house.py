from numpy import nan
from pandas import DataFrame
import pytest

from kuebiko.pipeline.companies_house.utils import (
    process_address,
    process_organisations,
    process_sectors,
)


@pytest.fixture
def raw_df():
    return DataFrame(
        {
            "company_name": ["Foo", "bar"],
            "company_number": ["SC12", "13"],
            "uri": ["http://foo", "http://bar"],
            "address_careof": [nan, "Baz"],
            "address_pobox": [nan, "*DEFAULT*"],
            "address_line1": ["58 VE", nan],
            "address_line2": [nan, nan],
            "address_postcode": [nan, "SE15 7UF"],
            "address_town": ["London", nan],
            "address_county": ["Londonshire", nan],
            "address_country": ["United Kingdom", "Engerrrland"],
            "company_category": ["Private Limited Company", "Limited Partnership"],
            "company_status": ["Active", "Liquidation"],
            "country_of_origin": ["United Kingdom", "Engerrrland"],
            "dissolution_date": [nan, nan],
            "incorporation_date": ["01/08/1981", "14/05/2021"],
            "sic_1": ["68209 - something", "99999 - all nines"],
            "sic_2": ["77777 - mostly nan", nan],
            "sic_3": [nan, nan],
            "sic_4": [nan, nan],
        }
    )


def test_process_organisations(raw_df):
    out = process_organisations(raw_df)
    assert out.shape == (2, 7)
    assert out.index.name == "company_number"


def test_process_address(raw_df):
    out = process_address(raw_df)
    assert out.shape == (2, 8)
    assert not any("address" in name for name in out.columns.values)
    assert out.index.name == "company_number"


def test_process_sectors(raw_df):
    out = process_sectors(raw_df)
    assert out.shape == (3, 4)
    assert out.index.name == "company_number"


def test_process_sectors_extraction(raw_df):
    out = process_sectors(raw_df)
    print(out)
    assert set(out.SIC5_code.values) == {"68209", "77777", "99999"}
    assert set(out.SIC4_code.values) == {"6820", "7777", "9999"}
    assert set(out["rank"].values) == {1, 2, 1}


## Testing `read_companies_house_chunk` could be considered overkill, given:
## our project is not a production system; the level of mocking required to
## test it; and that we have a flow-level test that should fail if anything
## were wrong with `read_companies_house_chunk`.
