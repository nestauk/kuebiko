from typing import Dict, List, Union

from metaflow import FlowSpec, project, step

## Declare constants in all caps at the top.
URL = (
    "http://www.ons.gov.uk/file?uri=/methodology/classificationsandstandards/"
    "ukstandardindustrialclassificationofeconomicactivities/uksic2007/"
    "sic2007summaryofstructurtcm6.xls"
)

# Type aliases
field_name = str
code_name = str
code = str


@project(name="kuebiko")
class Sic2007Structure(FlowSpec):
    """SIC 2007 taxonomy structure.

    Includes extra subclasses used by companies house:
    - 74990 - Non-trading company
    - 98000 - Residents property management
    - 99999 - Dormant company

    Attributes:
        url: Source excel file
        records: Taxonomy structure as list of records.
        section_lookup: Lookup from code to name
        division_lookup: Lookup from code to name
        group_lookup: Lookup from code to name
        class_lookup: Lookup from code to name
        subclass_lookup: Lookup from code to name
    """

    ## Type-hints for the data artifacts produced are super helpful!
    ## Here we've used type aliases to make these easier to interpret.
    url: str
    records: List[Dict[field_name, Union[code, code_name]]]
    section_lookup: Dict[code, code_name]
    division_lookup: Dict[code, code_name]
    group_lookup: Dict[code, code_name]
    class_lookup: Dict[code, code_name]
    subclass_lookup: Dict[code, code_name]

    @step
    def start(self):
        """Fetch Excel spreadsheet containing taxonomy structure from ONS website."""
        ## **Imports used with a step should always go within a step.**
        ## Because metaflow has the ability to abstract infrastructure then
        ## different steps may run on different machines with different environments.
        from utils import get, excel_to_df

        ## **Capture important values as data artifacts**, such as the URL data
        ## was fetched from. This helps debugging previous runs and can monitor
        ## important changes.<br>
        ## Though be wary of doing this uneccessarily for large values due to
        ## the overhead of persisting artifacts.
        self.url = URL

        ## Naming an artifact with a leading underscore makes the data artifact
        ## available to future steps as usual but hides it from a user inspecting
        ## the results of the run.
        ## This is useful to avoid users loading the raw data rather than the processed
        ## data, but it makes it harder to debug/monitor artifacts so it's a case
        ## of best judgement.
        self._raw_data = excel_to_df(get(self.url))

        self.next(self.transform)

    ## What operations should belong to the same step and when does it make
    ## sense to split a large step into multiple separate steps?<br>
    ## Artifacts are persisted when a step finishes executing. After artifacts
    ## have been persisted successfully, they become available for inspection,
    ## e.g. `metaflow.Run("Sic2007Structure").start.task.data.url`.
    ## Also you will be available to
    ## [resume](https://docs.metaflow.org/metaflow/
    ## debugging#how-to-use-the-resume-command)
    ## execution at an arbitrary step.
    ## Hence keeping steps reasonably small in terms of execution time,
    ## means you won't lose much work if failures happen; however persisting
    ## artifacts (particularly using the S3 datastore) and launching tasks
    ## (particularly using AWS batch) has some overhead so if your steps are
    ## too small, the overhead starts dominating the total execution time.
    ## **On balance it is good to have steps that logically map to the domain/problem
    ## so that it is easy to get a high-level understanding of the flow.** If
    ## you notice a large amount of overhead or your flow is hard to debug then
    ## you can split or merge existing steps accordingly.
    @step
    def transform(self):
        """Transform data.

        Make implicit entries explicit at row-level (fill), normalise SIC
        codes, and add extra codes specific to Companies House.
        """
        from utils import (
            companies_house_extras,
            EXPECTED_COLUMNS,
            fill,
            normalise_codes,
        )

        ## One of the big downsides of passing around dataframes is that it's
        ## easy to lose track of the shape of the data as it passes through
        ## various transformation functions, especially if you didn't even
        ## write the code in the first place!<br>
        ## **Give functions informative names and docstrings and obey the
        ## Single Responsibility Principle** to really help the understandability
        ## of code.<br>
        ## What about these functions, are there names and docstrings
        ## informative enough? What would you change?<br>
        ## In a later episode we will see how unit tests can also increase the
        ## readability and transparency of these transformation functions.
        self._data = (
            self._raw_data.pipe(fill)
            .pipe(normalise_codes)
            .append(companies_house_extras())
        )

        assert self._data.columns.tolist() == EXPECTED_COLUMNS
        self.next(self.end)

    @step
    def end(self):
        """Generate lookups at each level in the SIC hierarchy."""
        from utils import LEVELS

        ## Where possible **avoid saving dataframes as artifacts**,
        ## favouring standard Python data-structures instead.<br>
        ## Python data-structures do not impose the Pandas dependency on the
        ## downstream consumer of the data who may be working in an environment
        ## where Pandas isn't available (e.g. AWS lambda) or may have a
        ## different version of Pandas which when your artifact is loaded
        ## may subtly differ or fail to load.
        ## If dataframes are persisted as regular Python data-structure, the
        ## downstream consumer can still generate a dataframe if they want.
        # Create individual lookup for each level
        for level in LEVELS:
            lookup: Dict[code, code_name] = (
                self._data[[level, f"{level}_name"]]
                .set_index(level)
                .dropna()
                .to_dict()[f"{level}_name"]
            )
            setattr(self, f"{level}_lookup", lookup)

        self.records = self._data.to_dict(orient="records")


if __name__ == "__main__":
    Sic2007Structure()
