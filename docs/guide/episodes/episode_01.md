# 1. Metaflow basics - fetching auxillary data from the web

:warning: This is not a Metaflow tutorial! It is assumed that you have already looked through the [official Metaflow tutorials](https://docs.metaflow.org/getting-started/tutorials) and familiarised yourself with the [Metaflow docs](https://docs.metaflow.org/).

## Standard Industrial Taxonomy (SIC)

The first dataset that is fetched and processed is an Excel spreadsheet containing the codes and names of each of the 5 levels of the Standard Industrial Classification (SIC) taxonomy.
Later in the project when we come to analyse whether industry has an effect on the performance of a business' website this will be done using the SIC taxonomy - it's important that we are able to convert the (zero-padded) numeric codes into their description names when interpreting and reporting results.

The flow code can found in [`kuebiko/pipeline/sic/flow.py`\*](../pycco/kuebiko/pipeline/sic/flow.html) and its utility functions (which are not a focus of this episode) in [`kuebiko/pipeline/sic/utils.py`](../pycco/kuebiko/pipeline/sic/utils.html).

Lets recap a few Metaflow commands:

-   `python kuebiko/pipeline/sic/flow.py show` will give us the docstrings and basic structure of the flow.

-   `python kuebiko/pipeline/sic/flow.py run` will run the flow.

-   `python kuebiko/pipeline/sic/flow.py dump <run id>/end` will dump a summary of the artifacts for a given run ID.

!!! info "Metaflow defaults"

    `.envrc` specifies:

    - `METAFLOW_DEFAULT_DATASTORE=local`
    - `METAFLOW_PROFILE=ds-cookiecutter`

    [`direnv`](https://direnv.net/) automatically loads these environment variables (after you run `direnv allow` - a security mechanism to avoid changes to `.envrc` automatically executing unsafe code).

    The end effect is that Metaflow will use the configuration in `~/.metaflowconfig/config_ds-cookiecutter.json` that `ds-cookiecutter` sets up, and then override the default datastore to be local (data artifacts are persisted on your local machine in a `.metaflow/` folder not to S3).

-   `python kuebiko/pipeline/sic/flow.py --datastore=s3 run` will run the flow storing artifacts in S3 (rather than locally).

-   `python kuebiko/pipeline/sic/flow.py --datastore=s3 --production run` will run the flow storing artifacts in S3 (rather than locally) under a production namespace.

[`kuebiko/getters/sic.py`\*](../pycco/kuebiko/getters/sic.html) implements a getter function to load the lookups from our flow.
Writing a getter may seem to be an uneccessary level of indirection; however it is important to have this level of indirection because `getters`:

-   Allows us to create derived views of data where Metaflow artifacts may not map 1:1 to getter functions
-   Provides a place to go to discover what data is available for _analysis_ along in a logical folder/file structure with clear doc-strings per function
    -   **It is very important that getters relate to the problem domain**, <br>`get_csv_table(filename: str) -> DataFrame` is not a valid getter, it's a utility function at best!
-   Enables the possibility of extra data validation before returning to the user

## National Statistics Postcode Lookup (NSPL)

The second dataset that is fetched and processed is the National Statistics Postcode Lookup (NSPL), a lookup from UK postcodes to various statistical geographies.

In this project we wish to extract the Local Authority District (variably referred to as LAD or LAUA), latitude, and longitude of each postcode.
The Local Authority Districts will enable spatial aggregation of businesses to a level at which official statistics relating to the number of businesses in each SIC code in a given area.
The latitude and longitude will enable other activities such as plotting.

The flow code can found in [`kuebiko/pipeline/nspl/flow.py`\*](../pycco/kuebiko/pipeline/nspl/flow.html), its utility functions (which are not a focus of this episode) in [`kuebiko/pipeline/nspl/utils.py`](../pycco/kuebiko/pipeline/nspl/utils.html), and its getters in [`kuebiko/getters/nspl.py`\*](../pycco/kuebiko/getters/nspl.html)

!!! info inline end

    If a flow uses one of Metaflow's Conda decorators, or `--with conda` at runtime then it must run with `--environment=conda`.

Running `python kuebiko/pipeline/nspl/flow.py --environment=conda run` will run the flow.

## Companies House

The third dataset that is fetched and processed is the Companies House (UK company registrar) monthly data dump.

Each registered UK company has a company number. By finding company numbers on websites we can match companies to Companies House obtaining information such as the SIC code they classify their activities as and their registered trading addresses.

The flow code can found in [`kuebiko/pipeline/companies_house/flow.py`\*](../pycco/kuebiko/pipeline/companies_house/flow.html), its utility functions (which are not a focus of this episode) in [`kuebiko/pipeline/companies_house/utils.py`](../pycco/kuebiko/pipeline/companies_house/utils.html), and its getters in [`kuebiko/getters/companies_house.py`\*](../pycco/kuebiko/getters/companies_house.html)
.

Running `python kuebiko/pipeline/companies_house/flow.py run` will run the flow.

## A short investigation into artifact overheads

In [`kuebiko/pipeline/sic/flow.py`\*](../pycco/kuebiko/pipeline/sic/flow.html) we talked about the size of metaflow steps and the fact that persisting artifacts with the S3 datastore has some overhead, but how much?

The Companies House dataset is quite large (several GB of RAM as a Pandas dataframe), so lets use this to explore the slowdown we might see close to the worst case (also comparing to plain Python [`kuebiko/pipeline/companies_house/script.py`\*](../pycco/kuebiko/pipeline/companies_house/script.html) whilst we're here):

-   `time python kuebiko/pipeline/companies_house/flow.py run --max-workers 1`

    ~10 minutes

-   `time python kuebiko/pipeline/companies_house/script.py`

    ~10 minutes

-   `time python kuebiko/pipeline/companies_house/flow.py --datastore=s3 run --max-workers 1`

    ~26 minutes

-   `time python kuebiko/pipeline/companies_house/flow.py run --max-workers 4`

    ~4 minutes

-   `time python kuebiko/pipeline/companies_house/flow.py --datastore=s3 run --max-workers 4`

    ~19 minutes

Firstly, we see that Metaflow is the same speed as the plain Python script when
running on one core. We might expect Metaflow to be a little slower because it
has to serialise and deserialise artifacts between steps. Metaflow is twice as
fast when we allow up to 4 steps to execute at once - free parallelism as long
as we have the RAM to spare!

Next, comparing the local datastore to the S3 datastore, we see a rather large slowdown of 2.5x (5x with more parallelism)!<br>
Do not despair:

-   This was picked as a particularly bad case
-   In reality, you only need to pay this cost once when your feature is complete and you run with `--production --datastore=s3`. During testing/development you can use `--datastore=local` (or if you specify `METAFLOW_DEFAULT_DATASTORE=local` in `.envrc` then you don't need to explicitly choose this)
-   If the flow was run on batch, which requires the S3 datastore, (covered in a later episode) then the download and upload speeds would be faster and the slowdown not so severe
-   If all else fails you can always use the local datastore and use [`metaflow.S3`](https://docs.metaflow.org/metaflow/data#data-in-s3-metaflow.s3) to save and share the necessary data at the end of the flow

    -   :notebook: Note: You should use the `self` context, i.e. `with S3(run=self) as s3: ...` so that data is versioned under the current run ID and doesn't risk overwriting someone else's version of the data.
