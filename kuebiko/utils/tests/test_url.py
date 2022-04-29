from hypothesis import example, given, settings
from hypothesis.provisional import urls
from urllib3.util.url import parse_url, Url

from kuebiko.utils.url import (
    default_to_http,
    default_to_https,
    is_internal_link,
    resolve_link,
    use_http,
)

settings.register_profile("dev", max_examples=100)
settings.register_profile("production", max_examples=10_000)
settings.load_profile("dev")


GOOD_URL = "https://nesta.org.uk/about"
PATH_ONLY = "/path_only"
MISSING_SCHEME = "missing_scheme.com"


@given(urls())
@example(GOOD_URL)
def test_use_http_gen(s):
    url = parse_url(s)
    use_http(url)


@given(urls())
@example(GOOD_URL)
@example(MISSING_SCHEME)
def test_default_to_http(s):
    url = parse_url(s)
    default_to_http(url)


@given(urls())
@example(GOOD_URL)
@example(MISSING_SCHEME)
def test_default_to_https(s):
    url = parse_url(s)
    default_to_https(url)


@given(urls())
@example(GOOD_URL)
def test_is_internal_link(s):

    # Self identical
    url = parse_url(s)
    assert is_internal_link(url, url)

    def _internalise(url):
        """Drop host and ensure a path exists."""
        d = url._asdict()
        d.pop("host")

        if not d["path"]:
            d["path"] = "foo"
        return Url(**d)

    # Relative links are internal
    internal_url = _internalise(url)
    assert is_internal_link(internal_url, url)

    def _externalise(url):
        """Change host to be different."""
        d = url._asdict()
        d["host"] += "_diff"
        return Url(**d)

    # Different hosts are not internal
    external_url = _externalise(url)
    assert not is_internal_link(external_url, url)


@given(s1=urls(), s2=urls())
@example(s1=PATH_ONLY, s2=GOOD_URL)
@example(s1=PATH_ONLY, s2=PATH_ONLY)
@example(s1=MISSING_SCHEME, s2=GOOD_URL)
@example(s1=MISSING_SCHEME, s2=PATH_ONLY)
@example(s1="https://", s2=GOOD_URL)
@example(s1="https://", s2=PATH_ONLY)
def test_resolve_link(s1, s2):
    url1 = parse_url(s1)
    url2 = parse_url(s2)
    resolve_link(url1, url2)
