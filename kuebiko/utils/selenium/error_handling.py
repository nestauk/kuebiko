import logging

from selenium.common.exceptions import (
    InvalidSessionIdException,
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from urllib3.exceptions import MaxRetryError
from urllib3.util.url import Url

from .constants import CHROME_NETWORK_ERRORS
from .exceptions import BrowserCrashError, PossibleSchemeError
from .utils import dismiss_alerts


def is_driver_corrupt(driver: WebDriver) -> bool:
    """Returns True if WebDriver is corrupt (can't be used to perform new actions)."""
    try:
        driver.execute_script("")
    except MaxRetryError:
        # Arises when driver has quit?
        return True
    except UnexpectedAlertPresentException:
        try:
            dismiss_alerts(driver)
        except BrowserCrashError:
            return True
        return False
    except WebDriverException as exc:
        if _is_browser_crash(exc):
            return True
        raise exc  # Unexpected

    return False


def _is_browser_crash(exc: WebDriverException) -> bool:
    """Returns True if `exc` should be narrowed to a `BrowserCrashError`."""
    msg = exc.msg or ""
    return ("session deleted because of page crash" in msg) or isinstance(
        exc, InvalidSessionIdException
    )


def _is_chrome_network_error(msg: str) -> bool:
    return any([msg_ in (msg or "") for msg_ in CHROME_NETWORK_ERRORS.keys()])


def _is_scheme_error(exc: WebDriverException, url: Url) -> bool:
    ## Combine small functions to create more complex one
    return True if _is_chrome_network_error(exc.msg) and url.scheme != "http" else False  # type: ignore # noqa


def _is_timeout_error(exc: Exception) -> bool:
    ## May seem pointless to wrap this in such a simple function but our
    ## understanding of a timeout error could change. Encapsulating our domain's
    ## definition of a timeout error here means we would only need to make
    ## a change here.
    return isinstance(exc, TimeoutException)


def handle_webdriver_exception(exc: WebDriverException, url: Url) -> None:
    """Narrow `WebDriverException` for `url`, to specific exception or return `None`.

    Args:
        exc: A WebDriverException raised when trying to reach `url`
        url: URL that raised `exc`

    Raises:
        BrowserCrashError: `exc` narrowed
        PossibleSchemeError: `exc` narrowed
        TimeoutException: `exc` narrowed
        WebDriverException: `exc` wasn't narrowed to exception we know how to handle.

    Returns:
        None if `url` not reachable (non-transient error), e.g. the URL doesn't exist.
    """
    if _is_browser_crash(exc):
        raise BrowserCrashError(exc.msg)
    elif _is_scheme_error(exc, url):
        raise PossibleSchemeError(exc.msg)
    elif _is_timeout_error(exc):
        raise TimeoutException(exc.msg)
    elif _is_chrome_network_error(exc.msg):
        # Non-transient failure
        # E.g. "ERR_NAME_NOT_RESOLVED (-105)"
        return None
    else:
        logging.error(f"Unknown error pathway @ {url}: {exc.msg}")
        raise WebDriverException(*exc.args)
    return None
