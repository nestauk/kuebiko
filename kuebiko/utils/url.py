"""Utilities for parsing, constructing, and manipulating URL's."""
import toolz.curried as t
from icontract import ensure
from urllib3.util.url import Url


## Functions here are short and clear, taking and returning well defined
## objects (`Url` or `bool`). One-line docstrings and type-hints are sufficient.


## By running this function with the `ensure` "contract" we are automatically
## testing this function.
@ensure(lambda url, result: result.scheme == "http")
def use_http(url: Url) -> Url:
    """Swap use of https to http."""
    return url._replace(scheme="http")


## Defining a "contract" for the remaining functions doesn't give much
## benefit as it would duplicate the logic of the function body


@ensure(lambda url, result: result.scheme == (url.scheme or "http"))
def default_to_http(url: Url) -> Url:
    """If `url` lacks `scheme` set to 'http'."""
    if not url.scheme:
        return url._replace(scheme="http")
    else:
        ## We don't need to return a copy here because `Url`s are immutable.
        ## If they were, we should return `copy.copy(url)`
        return url


@ensure(lambda url, result: result.scheme == (url.scheme or "https"))
def default_to_https(url: Url) -> Url:
    """If `url` lacks `scheme` set to 'https'."""
    if not url.scheme:
        return url._replace(scheme="https")
    else:
        ## We don't need to return a copy here because `Url`s are immutable.
        ## If they were, we should return `copy.copy(url)`
        return url


@t.curry  # TODO: remove currying
def is_internal_link(url1: Url, url2: Url) -> bool:
    """Checks if `url1` has the same host as `url2` or has a relative path (no host)."""
    locations_match = url1.host == url2.host
    relative_link = not url1.host and url1.path
    return locations_match or relative_link


@t.curry  # TODO: remove currying
def resolve_link(link: Url, other: Url) -> Url:
    """If `link` lacks `host` or `scheme` get them from `other`."""
    host = link.host or other.host
    scheme = link.scheme or other.scheme
    return link._replace(host=host, scheme=scheme)
