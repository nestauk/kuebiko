import logging
from typing import Any, Callable, Optional, Tuple

from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from tenacity import (
    retry,
    retry_if_exception_type,
    RetryCallState,
    stop_after_attempt,
)

from .constants import DEFAULT_TIMEOUT
from .exceptions import BrowserCrashError


def raise_exception_on_call(exc: Exception) -> Callable:
    """Return function that when called will raise `exc`."""

    def delayed(state: RetryCallState) -> None:
        raise exc

    return delayed


@retry(
    stop=stop_after_attempt(10),
    retry=retry_if_exception_type(UnexpectedAlertPresentException),
    retry_error_callback=raise_exception_on_call(BrowserCrashError("alert bomb")),
)
def dismiss_alerts(driver: Optional[WebDriver]) -> Optional[WebDriver]:
    """Unexpected alerts prevent us extracting data, protect against it."""
    if not driver:  # pragma: nocover
        return None

    try:
        driver.execute_script("")  # current_url
    except UnexpectedAlertPresentException:
        # Triggered Exception dismisses ONE alert for us
        # Try again (more alerts triggers retry behaviour)
        driver.execute_script("")  # current_url

    return driver


def log_retry_error_return_none(retry_state: RetryCallState) -> None:
    """Log Tenacity retry error and return `None`."""
    url = retry_state.args[1]
    try:  # This should raise an error
        retry_state.outcome and retry_state.outcome.result()
    except Exception as exc:
        exc_type = type(exc).__qualname__
        logging.warning(f"Retry of 'get_with_retry' for '{url}' failed with {exc_type}")

    return None


def get_network_data(driver: WebDriver) -> Tuple[Any, Any, Any]:  # TODO
    """Get `window.performance` network data from `driver`."""
    navigation, paint, resource = driver.execute_script(
        """
        const performance = (
            window.performance ||
            window.mozPerformance ||
            window.msPerformance ||
            window.webkitPerformance ||
            {});
        const paint = performance.getEntriesByType("paint") || {}
        const resource = performance.getEntriesByType("resource") || {}
        const navigation = performance.getEntriesByType("navigation") || {}
        return [navigation, paint, resource];
        """
    )

    return navigation[0], paint, resource


def wait_for_readystate_complete(
    driver: Optional[WebDriver], timeout: int = DEFAULT_TIMEOUT
) -> Optional[WebDriver]:
    """Wait `timeout` seconds for `driver` document ready state to be "complete"."""
    if not driver:
        return None

    # Wait up to `timeout` seconds for document readystate to be "complete"
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
    return driver
