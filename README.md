# ds-cookiecutter guide (Kuebiko)

> Kuebiko (久延毘古) is the Shinto kami ("god; deity") of Folk wisdom, knowledge and agriculture, and is represented in Japanese mythology as a scarecrow who cannot walk but has comprehensive awareness.

## What is this?

A "full" (see [Corners cut](#corners-cut)) example [`ds-cookiecutter`](http://nestauk.github.io/ds-cookiecutter/) project broken down into episodes, with annotations/narrative for each episode focusing on a different aspect. In addition, there are a set of reference guides consolidating key concepts and pointing to further resources.

### Project problem statement

You have been given a big list (>100,000) of URLs corresponding to the business websites of UK companies.
The stakeholder is interested in better understanding the performance, accessibility, and legal compliance of business websites across different industries (SIC codes).

Some specific questions they have are:

1. It is a [requirement](https://www.gov.uk/running-a-limited-company/signs-stationery-and-promotional-material) that limited companies must display the company's registered number on their website, how many businesses actually list a company number?
2. Does the download size, response time, or reachability of a business' website bear any relation to the number of web development businesses nearby?
3. How do web development businesses themselves do on the extracted features mentioned above?
4. Is there any relationship between aforementioned extracted features and text on a business' website relating to what a business does?

### Episode plan

- [x] 0. Setup
- [x] 1. Metaflow basics - fetching auxiliary data from the web

  Walking through the basics of using metaflow idiomatically by fetching three auxiliary datasets needed for the project.

  Annotated code:

  - Metaflow flows and getter functions for:
    - Companies House lookups to get the SIC code and address for each company number.
    - National Statistics Postcode Lookup (NSPL) which will allow us to identify the Local Authority District (LADs) a company belongs to by matching its postcode.
    - SIC taxonomy lookup between names and codes

  Guides:

  - Metaflow I
    - Metaflow use-cases
    - Structuring/naming a flow
    - Tagging
    - Workflow: local vs remote datastore and metadata
    - Test mode
    - What format to store data artifacts as
    - Minimalism
    - Gotchas
    - When to use the conda decorators

- [ ] 2. Getting data from SQL - fetching NOMIS auxiliary data

  Simple example of how to get data from a DAPS SQL database. In this case, fetching the number of businesses stratified by both SIC code and LAD.

  Annotated code:

  - Metaflow flow fetching NOMIS data

  Other code:

  - Getter function for NOMIS data

- [ ] 3. Critical coding - web-scraping utilities

  To extract information such as Company number, download size, response time etc. from a business website, we first need to render and scrape the raw content.
  Due to the nature of the modern web, simple `GET` requests will not suffice and we need to use a browser automation tool - in this case [Selenium](https://www.selenium.dev/).
  We need to robustly scrape hundreds of thousands of websites, not knowing anything about their structure, behaviour, or likelihood to throw errors or crash the browser. In order to do this we need to develop some web-scraping utilities. This is also the perfect opportunity to define and give some pointers on "Critical coding" and testing.

  Annotated code:

  - Selenium web-scraping utilities
  - Tests for Selenium web-scraping utilities

  Other code:

  - Simple metaflow flow and associated getter for scraping URLs

  Guides:

  - Testing overview
    - Types and testing and when to use each
    - Suggested libraries
    - Links to further resources
  - Critical coding

- [ ] 4. Metaflow on AWS batch - scaling a web-scraper

  The simple scraping flow from episode 3 is too slow for large-scale scraping because it only runs on one machine scraping URLs one at a time.
  This episode scales the scraper using Metaflow on AWS batch to split our seed URLs into chunks and run different chunks on different machines in the cloud. Furthermore, it is also necessary to use a custom docker image to get Selenium working smoothly on AWS batch.

  Annotated code:

  - Scaled-up flow from episode 3
  - Script to build and push docker image to AWS

  Other code:

  - `Dockerfile` for Selenium

  Guides:

  - Metaflow II
    - Metaflow with AWS batch recommended practices
    - `metaflow_custom`
    - Gotchas
  - Docker primer

- [ ] 5. Advanced data getters - extracting and explored scraped data

  The distributed nature of the scaled-up flow developed in episode 4 results in a different artifact structure to its simple counterpart from episode 3. In turn, this means that a more sophisticated getter function is needed to be able to fetch the scraping results without running out of memory.
  This episode focuses on developing a such a getter.

  Annotated code:

  - Updated advanced getter function for scraped data

  Other code:

  - Feature extraction
  - EDA of scraped data

- [ ] 6. Data analysis - answering stakeholders first 3 questions

  With the fundamentals (auxiliary datasets and scraping pipeline) in place we can proceed to answer the first 3 questions in the problem statement.

  Annotated code:

  - Analysis notebooks and scripts for:
    1. How many businesses actually list a company number?
    2. Does the download size, response time, or reachability of a business' website bear any relation to the number of web development businesses nearby?
    3. How do web development businesses themselves do on the extracted features mentioned above?

- [ ] 7. Perfect is the enemy of good - Company description extraction

  In order to answer the final stakeholder question it is necessary to undertake the difficult task of being able to extract a company description from the raw HTML.
  This episode will implement a simple company description extraction algorithm.

  Annotated code:

  - Company description extraction functionality

- [ ] 8. Metaflow on AWS batch with a GPU - transformers

  One way of answering the final stakeholder question is to see whether businesses cluster in semantic space based on any of the extracted features.
  Transformers provide one way to produce a vector representation but ideally require access to powerful GPUs. This episode will show how to use Metaflow on AWS batch with a GPU to make powerful algorithms like transformers easily accessible without taking forever to run.

  Annotated code:

  - Metaflow flow to generate vector representation of company descriptions using transformers

  Other code:

  - Associated getter function

  Guides:

  - Metaflow III
    - Cost-benefit analysis

- [ ] 9. The fine line between analysis and pipeline - answering stakeholders final question
- [ ] 10. Refactoring

Further episodes may be added as further use-cases arise, further guidelines are developed or new technologies adopted (e.g. AWS step-functions).

### How to read/use

For each released episode the [episode overview](docs/episode_overview.md) gives: the link to the episode's narrative guide (these can be found in `episodes/`); a summary of what is tackled in the episode (both features but also associated guides); a description of the important new/modified files; and any important notes such as whether future episodes will improve upon specific aspects and whether an episode stands alone or builds upon a previous episode.

For each episode there will be a markdown file at `docs/episodes/episode_XX.md` which is the starting point for the episode. It will walk through the episode referring to files. Files with a `*` at the end are themselves annotated and you should read through these files and their annotations as the text refers to them.

Within the source code normal python comments, e.g. `# hello there`, belong in a real (not an example) data science project; however comments with two hashes like `## hello there` are for the narrative purposes of this guide.

### Corners cut

This is a MVP of a data science project following the `ds-cookiecutter` workflow but some corners have been cut:

- The problem statement is a bit contrived.

  It was chosen in order to demonstrate a variety of day-to-day aspects of data science development whilst keeping the overall level of content as small as possible to aid accessibility.

- We present and discuss complete, but not necessarily final, features -
  e.g. models work end-to-end but may only be simple.

  A detailed iterative workflow such as exploring in notebooks and then refactoring into modules, is not covered because:

  1. This would further bloat the already ambitious scope of this repository
  2. Everyone works differently and projects are nuanced therefore it does not pay to be opinonated here

  _There are plans to record a video demoing and discussing one possible workflow_

- Development/commit order is chosen for episodic release not necessarily the order which a real project would have

### Miscellaneous notes

- To avoid covering too much at once, early episodes are missing important things such as tests and data quality and data validation. These are covered a few episodes in and are retrospectively added at that point; **however** in a real project tests should always be written at the same time as the code they test (or even before if you are a proponent of test driven development)!
- When an episode gets opened for review then the code is only in a state/quality that any other PR might be at when a review is requested. I.e. there will be mistakes/shortcomings so it's up to DAP as a community to help improve things.
- The [`ds-cookiecutter` template](https://github.com/nestauk/ds-cookiecutter/pull/92) this is based on has not yet been merged (awaiting further reviews)
- Episode 4 will introduce our own extensions to Metaflow, [`metaflow_custom`](https://github.com/nestauk/metaflow_custom/). Due to a [change in `metaflow` as of `2.4.0`](https://github.com/Netflix/metaflow/pull/691), the package and repo is pending [renaming](https://github.com/nestauk/metaflow_custom/pull/13) to `metaflow_extensions`.

## Setup

- Meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:
  - Install: `git-crypt`, `direnv`, and `conda`
  - Have a Nesta AWS account configured with `awscli`
- Run `make install` to configure the development environment:
  - Setup the conda environment
  - Configure pre-commit
  - Configure metaflow to use AWS

---

<small><p>Project based on <a target="_blank" href="https://github.com/nestauk/ds-cookiecutter">Nesta's data science project template</a>
(<a href="http://nestauk.github.io/ds-cookiecutter">Read the docs here</a>).
</small>
