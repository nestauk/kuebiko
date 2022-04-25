"""Extracting SIC code structure lookups from Excel."""
import pandas as pd
import requests
from toolz import interleave

LEVELS = ["section", "division", "group", "class", "subclass"]
EXPECTED_COLUMNS = [
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


def get(url: str) -> bytes:
    """Get SIC 2007 structure from ONS hosted excel file."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def excel_to_df(content: bytes) -> pd.DataFrame:
    """Parse Excel to Dataframe."""
    return (
        pd.read_excel(
            content,
            skiprows=1,
            names=interleave([LEVELS, map(lambda x: f"{x}_name", LEVELS)]),
            dtype=str,
        )
        .dropna(how="all")
        .apply(lambda column: column.str.strip(), axis=1)
    )


def fill(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing information in spreadsheet.

    Go from:

    ```
    [
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
    ```

    To:

    ```
    [
        ["A", "Agri", "01", "Crop", "01.1", "Grow", "01.11", "Grow", "01.11/xx", "Extra"],
        ["A", "Agri", "01", "Crop", "01.1", "Grow", "01.12", "Grow", "01.12/0", "Grow"],
        ["A", "Agri", "01", "Crop", "01.2", "Grow", "01.21", "Grow", "01.21/0", "Grow"],
        ["A", "Agri", "02", "Forest", "02.1", "Silvi", "02.10", "Silvi", "02.10/0", "Silvi"],
        ["B", "Mini", "05", "Mini", "05.1", "Mini", "05.10", "Mini", "05.10/0", "Mini"],
    ]
    ```
    """  # noqa: B950
    return (
        df.pipe(_drop_notes)
        .pipe(_generic_fill, "section")
        .pipe(_generic_fill, "division")
        .pipe(_generic_fill, "group")
        .pipe(_class_subclass_fill)[EXPECTED_COLUMNS]
        .reset_index(drop=True)
    )


def companies_house_extras() -> pd.DataFrame:
    """Add Companies House specific SIC codes."""
    extras = {
        "subclass": ["74990", "98000", "99999"],
        "subclass_name": [
            "Non-trading company",
            "Residents property management",
            "Dormant company",
        ],
    }

    return pd.DataFrame(extras)


def normalise_codes(df):
    """Remove dots and slashes from SIC digits."""
    df.loc[:, LEVELS] = df.loc[:, LEVELS].apply(
        lambda col: col.str.replace("[./]", "", regex=True)
    )
    return df


def _class_subclass_fill(df: pd.DataFrame) -> pd.DataFrame:
    """Fill class and subclass.

    More nuanced because subclasses may not exist, therefore have to be
    resolved at the same time of class and possible inferred from them.
    """
    # Forward fill classes
    df.loc[:, ("class", "class_name")] = df.loc[:, ("class", "class_name")].ffill()

    # Backfill subclass by one
    # (each bfill eventually yields a duplicate row which we can drop with
    # `drop_duplicates` rather than tedious index accounting)
    df.loc[:, ("subclass", "subclass_name")] = df.loc[
        :, ("subclass", "subclass_name")
    ].bfill(limit=1)

    # If no subclass, derive from class by adding a zero, and using class name
    idx = df["subclass"].isna()
    df.loc[idx] = df.loc[idx].assign(
        subclass=lambda x: x["class"] + "/0", subclass_name=lambda x: x.class_name
    )

    return df.drop_duplicates()  # Drops dups we induced with bfill


def _drop_notes(df):
    """Drop rows that only have either code or name - they correspond to notes."""
    return df.loc[df.notna().sum(1) != 1]


def _generic_fill(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Ffill columns relating to `col`, dropping rows that were originally not NaN."""
    cols = [col, f"{col}_name"]
    subdf = df[cols].copy()

    # Indexes of rows that were originally not NaN (just labels to be propagated)
    label_idx = subdf.notna().sum(1).astype(bool)

    return (
        subdf
        # Forward fill
        .ffill()
        # Drop rows we don't need
        .loc[~label_idx]
        # Join back to rest of columns
        .join(df.drop(cols, 1))
    )
