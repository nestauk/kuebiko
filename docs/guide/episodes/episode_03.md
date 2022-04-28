# 3. Critical coding - web-scraping utilities

:warning: **This episode is highly incomplete and does not do a good job of demonstrating critical coding...** :warning:
There are missing tests; the code is still quite messy (e.g. the exposed API could be improved and exceptions are relied on for some control flow); several concepts are glossed over; and the `##` annotations are not coherent.
On reflection, the complexity of interacting with a web-browser (and everything that can go wrong in doing so) and the level of prior knowledge required means that this was probably a poor choice of task to pick for discussing critical coding.

A lot of the modern web relies on Javascript to do just about everything, if we just use `requests` then many web-pages will not render content => **use [Selenium](https://github.com/felipefiali/PySelenium)**

Selenium is _meant_ to be used to test applications (implying prior knowledge of the website structure - e.g. the page is loaded when we can find a `<div>` with a specific class/ID - but we are using it to scrape thousands of websites we have no prior knowledge of which adds significant complexity, e.g.:

-   We don't know if the website is reachable
-   The website might crash the browser
-   We don't know when a webpage can be considered loaded. There could be requests for content that take ages or timeout - these could be requests for crucial content or a tiny script snippet to load an ad.

Because of these sources of complexity and the fact that we want to build a scraping pipeline that is robust to failure (we don't want one unreachable website or a (recoverable) selenium driver crash to cause the whole pipeline to fail) we've elected to create a small utility library to help make the task of using Selenium for web-scraping a little easier.

-   `kuebiko/utils/url.py`
-   `kuebiko/utils/selenium/`
    -   `constants.py` - Defines constants, e.g. default timeouts and chrome network error codes
    -   `exceptions.py` - Defines two new exception types we need to handle errors
    -   `driver.py` - Provides a wrapper for Selenium `WebDriver`s that enables recovery from crashes
    -   `error_handling.py` - Defines error handling functions that map from the errors that Chrome/Selenium give us, to a smaller set of errors closer to the domain of scraping
    -   `utils.py` - General utility functions for user-code use (bad catch-all naming)
    -   `get_page.py` - User functions ...
-   `kuebiko/utils/{tests/,selenium/tests}` - Tests
