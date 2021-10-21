# ds-cookiecutter guide (Kuebiko)

> Kuebiko (久延毘古) is the Shinto kami ("god; deity") of Folk wisdom, knowledge and agriculture, and is represented in Japanese mythology as a scarecrow who cannot walk but has comprehensive awareness.

A "full" (see [Corners cut](#corners-cut)) example [`ds-cookiecutter`](http://nestauk.github.io/ds-cookiecutter/) project broken down into episodes, with annotations/narrative for each episode focusing on a different aspect. In addition, there are a set of reference guides consolidating key concepts and pointing to further resources.

!!! warning "Not from around these parts? A disclaimer..."

    This is an **internal (but open) project** to develop and refine best practices for _a subset_ of Nesta's work delivering data science projects.

    It is not a guide to production data science and the **recommended practices in this guide may be wholly unsuitable for you/your company** because you may be delivering completely different types of projects under completely different constraints.

    Furthermore, these docs are deployed when a new episode is ready for review therefore **content is likely to change significantly**! To get an indication of what content is stable, check out which [episodes have closed issues](https://github.com/nestauk/kuebiko/issues?q=is%3Aclosed+label%3Aepisode+sort%3Acreated-asc+).

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

-   [x] 0. Setup
-   [x] 1. Metaflow basics - fetching auxiliary data from the web
-   [ ] 2. Getting data from SQL - fetching NOMIS auxiliary data
-   [ ] 3. Critical coding - web-scraping utilities
-   [ ] 4. Metaflow on AWS batch - scaling a web-scraper
-   [ ] 5. Advanced data getters - extracting and explored scraped data
-   [ ] 6. Data analysis - answering stakeholders first 3 questions
-   [ ] 7. Perfect is the enemy of good - Company description extraction
-   [ ] 8. Metaflow on AWS batch with a GPU - transformers
-   [ ] 9. The fine line between analysis and pipeline - answering stakeholders final question
-   [ ] 10. Refactoring

Further episodes may be added as further use-cases arise, further guidelines are developed or new technologies adopted (e.g. AWS step-functions).

### How to read/use

For each released episode the [episode overview](episodes/index.md) gives: a summary of what is tackled in the episode (both features but also associated guides); a description of the important new/modified files; and any important notes such as whether future episodes will improve upon specific aspects and whether an episode stands alone or builds upon a previous episode.

For each episode there is a page at [episodes/episode_XX](episodes/) which is the starting point for the episode. It will walk through the episode referring to files. Files with a `*` at the end are themselves annotated and you should read through these files and their annotations as the text refers to them.

Normal python comments, e.g. `# hello there`, belong in a real (not an example) data science project; however comments with two hashes like `## hello there` are for the narrative purposes of this guide. In the online documentation, narrative comments are rendered as markdown on the left hand side of the page and ordinary comments are kept within the rendered source.

:notebook: **Note:** If reading the raw source files or using the github UI then some links may not work as this repo is targeting the online docs first. Where links don't work, the link text should be informative enough to send you to the right place!

### Corners cut

This is a MVP of a data science project following the `ds-cookiecutter` workflow but some corners have been cut:

-   The problem statement is a bit contrived.

    It was chosen in order to demonstrate a variety of day-to-day aspects of data science development whilst keeping the overall level of content as small as possible to aid accessibility.

-   We present and discuss complete, but not necessarily final, features -
    e.g. models work end-to-end but may only be simple.

    A detailed iterative workflow such as exploring in notebooks and then refactoring into modules, is not covered because:

    1. This would further bloat the already ambitious scope of this repository
    2. Everyone works differently and projects are nuanced therefore it does not pay to be opinonated here

    _There are plans to record a video demoing and discussing one possible workflow_

-   Development/commit order is chosen for episodic release not necessarily the order which a real project would have

### Miscellaneous notes

-   To avoid covering too much at once, early episodes are missing important things such as tests and data quality and data validation. These are covered a few episodes in and are retrospectively added at that point; **however** in a real project tests should always be written at the same time as the code they test (or even before if you are a proponent of test driven development)!
-   When an episode gets opened for review then the code is only in a state/quality that any other PR might be at when a review is requested. I.e. there will be mistakes/shortcomings so it's up to DAP as a community to help improve things.
    There are a few deliberate "mistakes" throughout, try and spot them
    and raise it in review.
-   The [`ds-cookiecutter` template](https://github.com/nestauk/ds-cookiecutter/pull/92) this is based on has not yet been merged (awaiting further reviews)
