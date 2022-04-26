"""Isolated test module due to destructing module scoped fixture, `driver_container`."""
from unittest.mock import MagicMock

from selenium.common.exceptions import WebDriverException


def test_dunder_exit_falls_back_on_kill(mock_driver_container):
    mock_driver_container._driver.quit = MagicMock(
        side_effect=WebDriverException("Failed to quit")
    )
    with mock_driver_container as driver_container:
        driver_process = driver_container._driver.service.process
    assert driver_process.returncode is not None, "Process not terminated"
