from pytest import mark, raises
from selenium.common.exceptions import (
    InvalidSessionIdException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from urllib3.exceptions import MaxRetryError

from kuebiko.utils.selenium import DriverContainer


def test_dunder_exit_quits_driver(url):
    url = str(url)
    with DriverContainer() as driver_container:
        driver_process = driver_container._driver.service.process
        driver_container._driver.get(url)
    with raises(MaxRetryError):
        driver_container._driver.get(url)
    assert driver_process.returncode is not None, "Process not terminated"


def test_call_gives_blank_page(driver_container):
    nonempty_content = "data:text/html;,I have a body"
    blank_page = "<html><head></head><body></body></html>"

    driver_container._driver.get(nonempty_content)
    driver_container()
    assert driver_container._driver.page_source == blank_page


def test_restart_driver_allows_get(driver_container, url, crash_url):
    crash_url = str(crash_url)
    url = str(url)
    # with DriverContainer() as driver_container:
    # Crash browser
    with raises(WebDriverException):
        driver_container().get(crash_url)
    # Vanilla get (no restart) fails
    with raises(WebDriverException):
        driver_container._driver.get(url)
    # Wrapped get succeeds
    driver_container().get(url)


@mark.parametrize(
    "side_effect",
    [
        MaxRetryError(pool="", url=""),
        InvalidSessionIdException(),
        WebDriverException("session deleted because of page crash"),
        UnexpectedAlertPresentException(),
    ],
)
def test_restart_driver_called_if_corrupt(mock_driver_container, side_effect):
    mock_driver_container._driver.execute_script.side_effect = side_effect
    mock_driver_container()
    mock_driver_container.restart_driver.assert_called_once()


def test_restart_driver_not_called_if_not_corrupt(mock_driver_container):
    mock_driver_container._driver.execute_script.side_effect = WebDriverException(
        "any old message"
    )
    with raises(WebDriverException):
        mock_driver_container()
        mock_driver_container.restart_driver.assert_not_called()

    mock_driver_container._driver.execute_script.side_effect = [
        UnexpectedAlertPresentException(),
        None,
    ]
    mock_driver_container()
    mock_driver_container.restart_driver.assert_not_called()

    mock_driver_container._driver.execute_script.side_effect = None
    mock_driver_container()
    mock_driver_container.restart_driver.assert_not_called()
