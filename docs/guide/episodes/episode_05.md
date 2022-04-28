# 5. Advanced data getters

:warning: **This episode is partially complete** :warning:

Episode 4 scales a web scraper to hundreds of thousands of websites but the scraped data is not available as a Metaflow data artifact (i.e. ...) because it is too large for memory.

This relatively short episode shows how we can write a data getter to pull all this data together relatively efficiently - without running out of RAM and caching data to disk (so that each call to the getter only has to make a trip to disk rather than downloading a lot of data over the network from S3).

`kuebiko/getters/websites.py` defines two getters:

-   `get_page_source` - Returns an iterable (not all loaded into RAM - unless you call something like `list(my_iterable)`) of tuples containing the scraped URL and it's page source (HTML).
-   `get_page_network_data` - Returns a list of tuples containing the scraped URL and it's network data.

Both of these getters rely on the `_get_page_data` function which:

-   Fetches the `keys` data artifact from the `UkBusinessHomepageScrape` run which corresponds to the S3 objects the scraped data chunks are stored at
-   Returns the data from those `keys` one at a time using `yield from` which means that:
    -   only one key of data is fetched and loaded into RAM at once
    -   each "row" in the data of a key is yielded one-by-one - the `from` bit of `yield from`
-   Uses the `diskcache` library to cache chunks of data to disk
