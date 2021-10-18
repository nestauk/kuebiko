# Episode overview

Overview of released episodes content, see [issues labeled `episode`](https://github.com/nestauk/kuebiko/issues?q=is%3Aopen+label%3Aepisode+sort%3Acreated-asc) for planned episodes.

## 1. Metaflow basics - fetching auxillary data from the web

This episode walks through the basics of using Metaflow idiomatically - i.e.
in a way that suits DAP and its use-cases - by fetching three auxilliary datasets needed:

-   Companies House lookups to get the SIC code and address for each company number.
-   National Statistics Postcode Lookup (NSPL) which will allow us to identify the Local Authority District (LADs) a company belongs to by matching its postcode.
-   SIC taxonomy lookup between names and codes

In addition, the first set of content (later episodes add more advanced content) is added to a Metaflow guide.

### Important notes

There are missing pieces to this episode that a data-science PR should have.
The most obvious of these is the absence of tests which are the subject of episode 3.
Tests for the three pipelines of this episode will be added in the testing episode in order to keep the content of this episode focused around writing basic Metaflow flows and getters.

Besides the [episode guide](episode_01.md) there is neither documentation of how to run the flows or version-controlled configuration for flow parameters. This will be addressed in episode 4.

### Key files

-   [Episode 1 guide](episode_01.md)
-   [`kuebiko/pipeline/sic/flow.py`](../pycco/kuebiko/pipeline/sic/flow.html)
-   [`kuebiko/getters/sic.py`](../pycco/kuebiko/getters/sic.html)
-   [`kuebiko/pipeline/nspl/flow.py`](../pycco/kuebiko/pipeline/nspl/flow.html)
-   [`kuebiko/getters/nspl.py`](../pycco/kuebiko/getters/nspl.html)
-   [`kuebiko/pipeline/companies_house/flow.py`](../pycco/kuebiko/pipeline/companies_house/flow.html)
-   [`kuebiko/getters/companies_house.py`](../pycco/kuebiko/getters/companies_house.html)
-   [Metaflow guide](../../guides/metaflow.md)
