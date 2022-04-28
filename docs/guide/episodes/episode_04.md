# 4. Metaflow on AWS batch

:warning: **This episode is partially complete** :warning:

Takes the scraping utilities developed in [Episode 3](episode_03.md) and wraps them in a Metaflow flow that starts many concurrent Batch jobs running our scraper allowing it to scale to hundreds of thousands of websites.

It also introduces the [`metaflow_extensions`](https://github.com/nestauk/metaflow_extensions) library which provides a `@pip` decorator which allows easy installation of pip dependencies. This is useful because it allows us to use the scraping utilities (in `kuebiko/utils/*`) on AWS Batch and/or within a Conda environment.

-   `kuebiko/pipeline/scraper/flow.py` defines the flow
-   `kuebiko/pipeline/scraper/utils.py` contains related utility functions:
    -   `chrome_scraper` - Define a Selenium Chrome `WebDriver` instance specific to scraping and performance benchmarking websites - this gets injected into the scraper utilities
    -   `get_page` - Simple wrapper around the scraper utilities to:
        -   Perform callback actions we want to occur when the scraper GETs a page
        -   Extract and return network and page source data
    -   `page_stats` - Processes network data into appropriate summary statistics

We can run the flow with the command...

```bash
python kuebiko/pipeline/scraper/flow.py\
 --datastore s3\
 --metadata service\
 --environment=conda\
 --package-suffixes .py,.md,.txt\
 run\
 --url-list inputs/data/websites.csv\
 --with "batch:image=pyselenium"
```

where:

-   `--with: "batch:image=pyselenium"` will run our flow steps on batch with the `pyselenium` image, which is a Docker image that will work with Python, Selenium, and Chrome and is hosted in Nesta's AWS ECR account
    -   alternatively to building, deploying, and maintaining a Docker image you could check out [`metaflow_extensions`' `preinstall` environment](https://github.com/nestauk/metaflow_extensions#i-want-to-install-something-on-a-batch-machine-that-isnt-available-via-pip-or-conda-but-i-dont-want-to-build-and-maintain-my-own-docker-image)
    -   the purpose of this episode is not to teach anything to do with Docker but the Dockerfile and a simple script to deploy to ECR can be found at `kuebiko/pipeline/scraper/{Dockerfile,build_deploy_docker.sh}`
-   `--package-suffixes ...` determines what file extensions get packaged up into batch jobs
    -   `.py` for our code
    -   `.md` because `setup.py` requires `README.md`
    -   `.txt` to include any `requirements*.txt` files

If we were doing a production run for all 100K sites we would do something like...

```bash
python kuebiko/pipeline/scraper/flow.py\
 --datastore s3\
 --metadata service\
 --environment=conda\
 --package-suffixes .py,.md,.txt\
 --production\
 run\
 --url-list inputs/data/websites.csv\
 --with "batch:image=pyselenium"\
 --max-workers 34\
 --max-num-splits 150
```

where:

-   `--max-workers 34` means we can have `34` metaflow tasks running at once - for this flow it means we'll have up to `34` AWS batch jobs concurrently scraping websites
-   `--max-num-splits 150` increases the number of "splits" a `foreach` step can contain. The default is `100` (to protect against accidentally creating a large number of jobs) but we end up with `101` so we increase this.

:flame: Check out the [results]() in the Metaflow UI :abacus:
