import logging
from subprocess import TimeoutExpired
from typing import Any, Callable

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from .error_handling import is_driver_corrupt


def chrome_driver() -> WebDriver:
    """Headless Chrome web driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def _quit(driver: WebDriver) -> None:
    try:
        driver.quit()
    except WebDriverException as exc:  # Aggressive fallback
        process = driver.service.process  # NOTE: chrome specific
        logging.error(
            f"Failed to close old driver: '{exc}'. Killing pid {process.pid}."
        )
        process.kill()
        try:
            process.wait(5)
        except TimeoutExpired:  # pragma: nocover
            logging.warning(f"Failed to wait for {process.pid} to terminate.")


class DriverContainer(object):
    """Callable wrapper for Selenium driver that returns a new driver after crash."""

    def __init__(
        self, driver_factory: Callable[..., WebDriver] = chrome_driver
    ) -> None:
        """Initialise selenium driver."""
        self._driver_factory = driver_factory
        self._driver = self._driver_factory()

    def __enter__(self) -> "DriverContainer":
        """No-op."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Quit `WebDriver`."""
        _quit(self._driver)

    def __call__(self) -> WebDriver:
        """Returns selenium driver on blank page with valid session."""
        if is_driver_corrupt(self._driver):
            self.restart_driver()
        self._driver.get("data:;,")
        return self._driver

    def restart_driver(self) -> None:
        """Restarts selenium driver."""
        logging.debug("Restarting driver...")
        try:
            self._driver.close()  # Fast
        except WebDriverException:
            _quit(self._driver)  # Slow fallback
        try:
            self._driver = self._driver_factory()
        except Exception as e:  # pragma: nocover
            logging.error(f"Failed to create new driver instance on restart: {e}")
            raise e
