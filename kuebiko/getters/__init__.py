from tempfile import gettempdir

from diskcache import Cache

from . import companies_house
from . import nspl
from . import sic


__all__ = ["sic", "nspl", "companies_house"]


## Create a cache on disk so that we can cache expensive S3 GETs
cache = Cache(f"{gettempdir()}/kuebiko_getters")
cache.expire()
