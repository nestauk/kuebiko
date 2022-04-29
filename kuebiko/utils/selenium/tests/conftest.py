from unittest.mock import MagicMock

import pytest
from urllib3.util.url import parse_url

from kuebiko.utils.selenium import DriverContainer


@pytest.fixture
def https_url():
    return parse_url("https://google.com")


@pytest.fixture
def http_url():
    return parse_url("http://google.com")


@pytest.fixture
def url():
    ## `url` works offline making the test more robust
    return parse_url("file:///tmp")


@pytest.fixture
def crash_url():
    return parse_url("chrome://crash")


## This could really speed up our tests but we risk breaking things
## because the object underlying the cache is stateful!
# DriverContainer = functools.lru_cache(DriverContainer)
## Instead we can scope fixtures to get the speed up in a more controlled manner
@pytest.fixture(scope="module")
def driver_container():
    dc = DriverContainer()

    yield dc
    dc.__exit__()


@pytest.fixture(scope="module")
def mock_driver_container_():
    """Setup a mocked DriverContainer."""
    dc = DriverContainer()
    yield dc
    dc.__exit__()


## This fixture needs to reset every function so our mock objects are reset
@pytest.fixture
def mock_driver_container(mock_driver_container_):
    """Setup a mocked DriverContainer."""
    mock_driver_container_.restart_driver = MagicMock()
    mock_driver_container_._driver.get = MagicMock()
    mock_driver_container_._driver.execute_script = MagicMock()

    with open("/tmp/foo.txt", "a") as f:
        f.write(".")
    return mock_driver_container_


def n_errors_then_response(exc, n=1, response="RESPONSE"):
    for _ in range(n):
        yield exc
    yield response
