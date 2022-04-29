import pytest
from pandas.testing import assert_frame_equal
from requests.exceptions import HTTPError

from kuebiko.pipeline.sic.flow import URL
from kuebiko.pipeline.sic.utils import fill, get, LEVELS, normalise_codes


## By running our test-suite we know that the data is still there
def test_data_URL_still_live():
    response = get(URL)
    assert isinstance(response, bytes)


## We want to test that failures aren't silent
def test_get_fails_on_bad_URL():
    with pytest.raises(HTTPError):
        get(URL + "/garbage")


## If we were building a production system we would more rigorously test `get`
## and would test `excel_to_df` but these get sufficient testing by running
## the flow (`test_sic_flow.py`)
## Remains to test the core transformation logic of utils in the remaining functions...


def test_fill(raw_df, clean_df):
    out = fill(raw_df)
    print(out)
    print(clean_df)
    assert out.isna().sum().sum() == 0
    assert_frame_equal(out, clean_df)


def test_normalise_codes(clean_df):
    assert (
        normalise_codes(clean_df.loc[:, LEVELS])
        # Check for dots/slashes in `LEVELS`
        .apply(lambda col: (~col.str.contains(r"\.|/", regex=True)).all()).all()
    )
