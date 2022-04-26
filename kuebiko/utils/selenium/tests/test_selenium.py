# from unittest.mock import patch

# from pytest import raises
# from selenium.common.exceptions import (
#     InvalidSessionIdException,
#     TimeoutException,
#     WebDriverException,
# )
# from urllib3.exceptions import MaxRetryError
# from urllib3.util.url import parse_url

# from kuebiko.utils.selenium import (
#     DriverContainer,
#     get,
#     get_with_retry,
# )
# from kuebiko.utils.selenium.constants import CHROME_NETWORK_ERRORS
# from kuebiko.utils.selenium.error_handling import (
#     BrowserCrashError,
#     PossibleSchemeError,
# )


# @patch(
#     "kuebiko.utils.selenium.get_page.get",
#     side_effect=TimeoutException("Timeout"),
# )
# def test_get_retry_halts(get_mock):
#     driver_container = object

#     assert get_with_retry(driver_container, "localhost") is None
#     assert get_mock.call_count == 2

#     get_mock.side_effect = BrowserCrashError("Crash")
#     get_mock.reset_mock()

#     assert get_with_retry(driver_container, "localhost") is None
#     assert get_mock.call_count == 2


# def n_errors_then_response(exc, n=1, response="RESPONSE"):
#     for _ in range(n):
#         yield exc
#     yield response


# @patch(
#     "kuebiko.utils.selenium.get_page.get",
#     side_effect=n_errors_then_response(TimeoutException("Timeout")),
# )
# def test_get_retry_on_one_timeout_succeeds(get_mock):
#     driver_container = object

#     assert get_with_retry(driver_container, HTTPS_URL) == "RESPONSE"
#     assert get_mock.call_count == 2


# @patch(
#     "kuebiko.utils.selenium.get_page.get",
#     side_effect=n_errors_then_response(PossibleSchemeError()),
# )
# def test_get_retry_on_scheme_error_succeeds(get_mock):
#     driver_container = object

#     assert get_with_retry(driver_container, HTTPS_URL) == "RESPONSE"
#     assert get_mock.call_count == 2


# def test_get_timeout():
#     driver_container = mock_driver_container()
#     driver_container._driver.get.side_effect = TimeoutException("Timeout")

#     with raises(TimeoutException):
#         get(driver_container, HTTPS_URL)


# def test_get_webdriverexception():
#     driver_container = DriverContainer()  # mock_driver_container()

#     for _, code in CHROME_NETWORK_ERRORS.items():
#         # driver_container._driver.get.side_effect = WebDriverException(msg)
#         url = parse_url(f"chrome://network-error/{code}")
#         print(url)
#         with raises(PossibleSchemeError):
#             get(driver_container, url)
#         # assert get(driver_container, HTTP_URL) is None

#     driver_container = mock_driver_container()
#     # TODO: How can we actually trigger these exceptions for real?
#     #       If selenium error messages change then tests don't save us
#     # TODO: Does this only apply to chromium?
#     driver_container._driver.get.side_effect = TimeoutException()
#     with raises(TimeoutException):
#         get(driver_container, HTTPS_URL)

#     driver_container._driver.get.side_effect = InvalidSessionIdException()
#     with raises(BrowserCrashError):
#         get(driver_container, HTTPS_URL)

#     driver_container._driver.get.side_effect = WebDriverException(
#         "session deleted because of page crash"
#     )
#     with raises(BrowserCrashError):
#         get(driver_container, HTTPS_URL)

#     driver_container._driver.get.side_effect = WebDriverException("unknown error")
#     with raises(WebDriverException):
#         get(driver_container, HTTPS_URL)

#     driver_container._driver.get.side_effect = WebDriverException(
#         "ERR_NAME_NOT_RESOLVED"
#     )
#     assert get(driver_container, HTTP_URL) is None
#     with raises(PossibleSchemeError):
#         get(driver_container, HTTPS_URL)
