from typing import Any, Optional, Tuple, TypedDict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from toolz import compose_left
from urllib3.util.url import Url

from kuebiko.utils.selenium import (
    dismiss_alerts,
    DriverContainer,
    get_network_data,
    get_with_retry,
    wait_for_readystate_complete,
)

DEFAULT_TIMEOUT = 10


def chrome_scraper(
    page_timeout: int = DEFAULT_TIMEOUT,
    script_timeout: int = DEFAULT_TIMEOUT,
    download_images: bool = True,
) -> WebDriver:
    """Chrome web driver configured for scraping.

    Args:
        page_timeout: Set the amount of time to wait for a page load to
            complete before throwing an error.
        script_timeout: Set the amount of time that the script should wait
            during an execute_async_script call before throwing an error.
        download_images: If False save bandwidth and do not display/download images.

    Returns:
        Chrome Web Driver
    """
    chrome_options = Options()

    if not download_images:
        chrome_options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )

    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    # Docker /dev/shm too small - avoid crashes in docker:
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(page_timeout)
    driver.set_script_timeout(script_timeout)
    return driver


def get_page(
    driver_container: DriverContainer, url: Url
) -> Tuple[str, Optional[str], Optional[Tuple[Any, Any, Any]]]:
    """Get page source and network data of `url`."""
    ## When a Selenium GETs a page - dismiss any javascript alerts and wait for
    ## the `"complete"` document ready state [1] which is a reasonable
    ## simple heuristic to indicate that a page has finished loading
    ## [1] https://developer.mozilla.org/en-US/docs/Web/API/Document/readyState
    callback = compose_left(dismiss_alerts, wait_for_readystate_complete)
    try:
        driver = get_with_retry(driver_container, url, callback=callback)
    except WebDriverException:  # If an unexpected error arises don't crash everything
        return str(url), None, None

    if driver is None:  # Couldn't get `url` for non-transient reason
        return str(url), None, None
    else:
        return str(url), driver.page_source, get_network_data(driver)


class PageStats(TypedDict):
    """Network data statistics for a webpage."""

    size_kb: float
    paint_time: Optional[float]
    dom_time: Optional[float]


def page_stats(network_data: tuple) -> PageStats:
    """Process `window.performance` network data into summary statistics."""
    navigation, paint, resource = network_data
    return {
        "size_kb": _page_size(resource),
        "paint_time": _paint_time(paint) if paint else None,
        "dom_time": _dom_time(navigation) if navigation else None,
    }


def _page_size(resource) -> float:
    # kB
    return sum((x["transferSize"] for x in resource)) / 1000


def _paint_time(paint) -> float:
    # ms
    return float(paint[0]["startTime"])


def _dom_time(navigation) -> float:
    # ms
    return float(navigation["domComplete"])
