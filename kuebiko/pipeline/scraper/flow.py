import json

from metaflow import (
    conda_base,
    current,
    FlowSpec,
    IncludeFile,
    Parameter,
    pip,
    project,
    retry,
    S3,
    step,
)
from urllib3.util.url import parse_url


@conda_base(python="3.8")
@project(name="kuebiko")
class UkBusinessHomepageScrape(FlowSpec):
    """Scrape URL's in `url_list` with Selenium."""

    ## This is a heavy duty flow we want to run on many machines on Batch, so
    ## we need a way to distribute our data.
    ## If we used the getter `kuebiko.getters.inputs.url.get_urls` then the
    ## underlying file would be missing (it only exists locally on our
    ## hard-drive, not in the cloud).
    ## We could run `make inputs-push`, and then in the `start` step download
    ## the data from our bucket, but `IncludeFile` is just a lot more convenient.
    url_list = IncludeFile(
        "url-list", required=True, help="Newline delimited set of URL's to scrape."
    )

    test = Parameter("test", default=True, type=bool)
    test_size = Parameter("test-size", default=100, type=int)

    @pip(path="requirements.txt", safe=False)
    @step
    def start(self) -> None:
        """Chunk `url_list` into chunks."""
        import toolz.curried as t
        from kuebiko.utils.url import default_to_http

        chunk_size = self.test_size // 4 if self.test else 1_000

        ## Assign this composition to a variable so the pipeline below is more readable
        line_to_url = t.compose_left(str.strip, parse_url, default_to_http)
        ## Expressing the transformation as a sequence of steps inside pipes
        ## means we can read in linear order rather than:<br>
        ## Reading inside out...
        ## ```python
        ## self.url_chunks = list(
        ##     t.partition(
        ##         chunk_size,
        ##         t.take(
        ##             None if not self.test else self.test_size,
        ##             (line_to_url(url) for url in self.url_list.split("\n")),
        ##         ),
        ##     )
        ## )
        ## ```
        ## Or having to give redundant names or over-write variables every
        ## individual step...
        ## ```python
        ## urls = [line_to_url(url) for url in self.url_list.split("\n")]
        ## urls = t.take(None if not self.test else self.test_size)
        ## self.url_chunks = list(t.partition(chunk_size, urls))
        ## ```
        self.url_chunks = t.pipe(
            self.url_list.split("\n"),
            t.map(line_to_url),
            t.take(None if not self.test else self.test_size),  # None means take all
            t.partition_all(chunk_size),
            list,
        )

        self.next(self.fork, foreach="url_chunks")

    @pip(path="requirements.txt")
    @retry(times=2, minutes_between_retries=1)
    @step
    def fork(self) -> None:
        """Scrape input."""
        ## TODO: why are the imports here
        from kuebiko.utils.selenium import DriverContainer
        from kuebiko.pipeline.scraper.utils import chrome_scraper, get_page

        task_id = current.task_id
        urls = self.input
        with DriverContainer(chrome_scraper) as driver_container:
            data = [get_page(driver_container, url) for url in urls]

            ## We could assign `data` to `self.data` and get metaflow to
            ## automatically create an artifact that we can load;
            ## however when we go to join the artifacts from each fork
            ## in the next (join) step we run into issues:
            ## 1) If we try and combine all the data into one artifact we
            ##    will run out of memory
            ## 2) If we process the chunks one-by-one clearing memory as
            ##    each is done, then we need to stream to S3 which requires
            ##    an extra dependency (`smart-open`).
            ##    If we choose JSON (a sensible default format) then the
            ##    getter ends up with one big file that it can't stream and
            ##    likely ends up running out of memory (and you have to hack
            ##   '[' and ']' at the beginning and end of writing).
            ##    If we choose ...
            ##
            ## Instead we ...
            with S3(run=self) as s3:
                self.key = f"pages-task{task_id}.json"
                ## Very inefficient way of storing the data - if we only wanted
                ## to analyse the network data we'd have to download and load
                ## into RAM all the page-sources too...
                s3.put(self.key, json.dumps(data))

        self.next(self.join)

    @step
    def join(self, inputs) -> None:
        """Store keys corresponding to data from forked tasks."""
        ## Storing keys means we have to write less logic in the getters
        ## rather than duplicating logic.
        self.keys = list(input.key for input in inputs)
        self.next(self.end)

    @step
    def end(self) -> None:
        """No-op."""
        pass


if __name__ == "__main__":
    UkBusinessHomepageScrape()
