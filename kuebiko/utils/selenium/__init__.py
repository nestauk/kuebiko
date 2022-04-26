"""Utilities for web scraping with Chrome+Selenium in a more robust manner."""
from .driver import chrome_driver, DriverContainer
from .exceptions import BrowserCrashError, PossibleSchemeError
from .get_page import get, get_with_retry
from .utils import dismiss_alerts, get_network_data, wait_for_readystate_complete

## This explicitly defines our public API
__all__ = [
    "BrowserCrashError",
    "PossibleSchemeError",
    "get",
    "get_with_retry",
    "DriverContainer",
    "chrome_driver",
    "dismiss_alerts",
    "get_network_data",
    "wait_for_readystate_complete",
]

# TODO: https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.support.abstract_event_listener  # noqa: B950
