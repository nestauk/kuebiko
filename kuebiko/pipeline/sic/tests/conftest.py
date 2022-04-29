import pytest
from numpy import nan
from pandas import DataFrame


@pytest.fixture
def expected_columns():
    return [
        "section",
        "section_name",
        "division",
        "division_name",
        "group",
        "group_name",
        "class",
        "class_name",
        "subclass",
        "subclass_name",
    ]


@pytest.fixture
def raw_df(expected_columns):
    NOTE = "Notes in the middle of data are amateur hour stuff"
    rows = [
        ["A", "Agri", nan, nan, nan, nan, nan, nan, nan, nan],
        [nan, nan, "01", "Crop", nan, nan, nan, nan, nan, nan],
        [nan, nan, nan, nan, "01.1", "Grow", nan, nan, nan, nan],
        [nan, nan, nan, nan, nan, nan, "01.11", "Grow", nan, nan],
        [nan, nan, nan, nan, nan, nan, nan, nan, "01.11/xx", "Extra"],
        [nan, nan, nan, nan, nan, nan, "01.12", "Grow", nan, nan],
        [nan, nan, nan, nan, "01.2", "Grow", nan, nan, nan, nan],
        [nan, nan, nan, nan, nan, nan, "01.21", "Grow", nan, nan],
        [nan, nan, "02", "Forest", nan, nan, nan, nan, nan, nan],
        [nan, nan, nan, nan, "02.1", "Silvi", nan, nan, nan, nan],
        [nan, nan, nan, nan, nan, nan, "02.10", "Silvi", nan, nan],
        ["B", "Mini", nan, nan, nan, nan, nan, nan, nan, nan],
        [nan, nan, "05", "Mini", nan, nan, nan, nan, nan, nan],
        [nan, nan, nan, NOTE, nan, nan, nan, nan, nan, nan],
        [nan, nan, nan, nan, "05.1", "Mini", nan, nan, nan, nan],
        [nan, nan, nan, nan, nan, nan, "05.10", "Mini", nan, nan],
    ]
    return DataFrame(rows, columns=expected_columns)


@pytest.fixture
def clean_df(expected_columns):
    # fmt: off
    rows = [
        ["A", "Agri", "01", "Crop", "01.1", "Grow", "01.11", "Grow", "01.11/xx", "Extra"],  # noqa: B950
        ["A", "Agri", "01", "Crop", "01.1", "Grow", "01.12", "Grow", "01.12/0", "Grow"],
        ["A", "Agri", "01", "Crop", "01.2", "Grow", "01.21", "Grow", "01.21/0", "Grow"],
        ["A", "Agri", "02", "Forest", "02.1", "Silvi", "02.10", "Silvi", "02.10/0", "Silvi"],  # noqa: B950
        ["B", "Mini", "05", "Mini", "05.1", "Mini", "05.10", "Mini", "05.10/0", "Mini"],
    ]
    # fmt: on
    return DataFrame(rows, columns=expected_columns)
