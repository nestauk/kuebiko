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

Below is a list of provisional episodes. See [issues labeled `episode`](https://github.com/nestauk/kuebiko/issues?q=is%3Aopen+label%3Aepisode+sort%3Acreated-asc) for more information and more timely updates.

- [x] 0. Setup
- [ ] 1. Metaflow basics - fetching auxiliary data from the web
- [ ] 2. Getting data from SQL - fetching NOMIS auxiliary data
- [ ] 3. Critical coding - web-scraping utilities
- [ ] 4. Metaflow on AWS batch - scaling a web-scraper
- [ ] 5. Advanced data getters - extracting and explored scraped data
- [ ] 6. Data analysis - answering stakeholders first 3 questions
- [ ] 7. Perfect is the enemy of good - Company description extraction
- [ ] 8. Metaflow on AWS batch with a GPU - transformers
- [ ] 9. The fine line between analysis and pipeline - answering stakeholders final question
- [ ] 10. Refactoring

Further episodes may be added as further use-cases arise, further guidelines are developed or new technologies adopted (e.g. AWS step-functions).

### How to read/use

For each released episode the [episode overview](docs/episode_overview.md) gives: the link to the episode's narrative guide (these can be found in `episodes/`); a summary of what is tackled in the episode (both features but also associated guides); a description of the important new/modified files; and any important notes such as whether future episodes will improve upon specific aspects and whether an episode stands alone or builds upon a previous episode.

For each episode there will be a markdown file at `docs/episodes/episode_XX.md` which is the starting point for the episode. It will walk through the episode referring to files. Files with a `*` at the end are themselves annotated and you should read through these files and their annotations as the text refers to them.

Within the source code normal python comments, e.g. `# hello there`, belong in a real (not an example) data science project; however comments with two hashes like `## hello there` are for the narrative purposes of this guide.

To assist with readabilty I have [forked](https://github.com/bishax/pycco) and tweaked the `pycco` literate documentation generator to render these narrative comments.
To generate these documents: [setup the repo](#setup), run `make pycco`, and open `docs/pycco/index.html` in your browser. These will shortly be published to github pages.

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
