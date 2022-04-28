import logging
from typing import Any, Callable, Optional

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)
from urllib3.util.url import Url

from kuebiko.utils.url import use_http
from .constants import DEFAULT_RETRIES, DEFAULT_RETRY_WAIT
from .error_handling import handle_webdriver_exception
from .exceptions import BrowserCrashError, PossibleSchemeError
from .utils import log_retry_error_return_none


@retry(
    wait=wait_fixed(DEFAULT_RETRY_WAIT),
    retry=(
        retry_if_exception_type(TimeoutException)
        | retry_if_exception_type(BrowserCrashError)
    ),
    before=lambda state: logging.debug(f"GET {state.args[1]}"),
    before_sleep=lambda state: logging.debug(f"Retry GET {state.args[1]}"),
    retry_error_callback=log_retry_error_return_none,
    stop=stop_after_attempt(DEFAULT_RETRIES),
)
def get_with_retry(
    driver_container: Callable[[], WebDriver],
    url: Url,
    callback: Optional[Callable[[WebDriver], Any]] = None,
) -> Optional[WebDriver]:
    """GET `url` returning raw content response if successful and retrying if not."""
    try:
        return get(driver_container, url, callback)
    except PossibleSchemeError:  # Retry with modified argument
        logging.info(f"Trying {url} with 'http://' scheme")
        url = use_http(url)
        return get(driver_container, url, callback)


def get(
    driver_container: Callable[[], WebDriver],
    url: Url,
    callback: Optional[Callable[[WebDriver], WebDriver]] = None,
) -> Optional[WebDriver]:
    """GET `url` returning raw content response if successful."""
    try:
        driver = driver_container()
        driver.get(str(url))

        if callback:
            callback(driver)

        return driver
    except WebDriverException as exc:
        return handle_webdriver_exception(exc, url)
