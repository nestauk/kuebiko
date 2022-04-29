from unittest.mock import Mock, patch

from pytest import mark, raises
from selenium.common.exceptions import (
    InvalidSessionIdException,
    TimeoutException,
    WebDriverException,
)

from kuebiko.utils.selenium import (
    get,
    get_with_retry,
)
from kuebiko.utils.selenium.constants import CHROME_NETWORK_ERRORS, DEFAULT_RETRIES
from kuebiko.utils.selenium.error_handling import (
    BrowserCrashError,
    PossibleSchemeError,
)
from conftest import n_errors_then_response  # noqa


@mark.parametrize(
    "side_effect", [TimeoutException("Timeout"), BrowserCrashError("Crash")]
)
@patch("kuebiko.utils.selenium.get_page.get")
def test_get_retry_halts_on_constant_error(get_mock, side_effect, url):
    driver_container = object

    get_mock.side_effect = side_effect
    assert get_with_retry(driver_container, url) is None
    assert get_mock.call_count == DEFAULT_RETRIES


@mark.parametrize(
    "side_effect",
    [
        n_errors_then_response(TimeoutException("Timeout"), n=DEFAULT_RETRIES - 1),
        n_errors_then_response(BrowserCrashError("Crash"), n=DEFAULT_RETRIES - 1),
        n_errors_then_response(PossibleSchemeError("Scheme"), n=DEFAULT_RETRIES - 1),
    ],
)
@patch(
    "kuebiko.utils.selenium.get_page.get",
)
def test_get_retry_succeeds_on_transient_error(get_mock, side_effect, url):
    driver_container = object

    get_mock.side_effect = side_effect
    assert get_with_retry(driver_container, url) == "RESPONSE"
    assert get_mock.call_count == DEFAULT_RETRIES


@mark.parametrize(
    "side_effect, narrowed_exc",
    [
        (TimeoutException(), None),
        (BrowserCrashError(), None),
        (PossibleSchemeError(), None),
        (
            InvalidSessionIdException(),
            BrowserCrashError(),
        ),
        (
            WebDriverException("session deleted because of page crash"),
            BrowserCrashError(),
        ),
        (WebDriverException(), None),
    ],
)
def test_get_raises_error(mock_driver_container, side_effect, narrowed_exc, url):
    mock_driver_container._driver.get.side_effect = side_effect

    with raises(narrowed_exc.__class__ if narrowed_exc else side_effect.__class__):
        get(mock_driver_container, url)


@mark.parametrize(
    "side_effect, narrowed_exc",
    [
        (WebDriverException(str(msg)), PossibleSchemeError())
        for msg in CHROME_NETWORK_ERRORS.keys()
    ],
)
def test_network_error_raises_possibleschemeerror_without_http(
    mock_driver_container, side_effect, narrowed_exc, url
):
    mock_driver_container._driver.get.side_effect = side_effect

    with raises(narrowed_exc.__class__ if narrowed_exc else side_effect.__class__):
        get(mock_driver_container, url)


@mark.parametrize(
    "side_effect",
    [WebDriverException(str(msg)) for msg in CHROME_NETWORK_ERRORS.keys()],
)
def test_network_error_returns_none_on_http_foo(
    mock_driver_container, side_effect, http_url
):
    mock_driver_container._driver.get.side_effect = side_effect
    assert get(mock_driver_container, http_url) is None


def test_get_succeeds_foo(url, driver_container):
    callback = Mock(side_effect=print)

    assert get(driver_container, url, callback)
    assert get(driver_container, url)
    callback.assert_called_once()
