import os
from typing import Dict

DEFAULT_TIMEOUT = 10
CHROME_NETWORK_ERRORS: Dict[str, int] = {
    "ERR_CONNECTION_CLOSED": -100,
    "ERR_CONNECTION_RESET": -101,
    "ERR_CONNECTION_REFUSED": -102,
    "ERR_NAME_NOT_RESOLVED": -105,
    "ERR_SSL_PROTOCOL_ERR": -107,
    "ERR_ADDRESS_UNREACHABLE": -109,
    "ERR_SSL_VERSION_OR_CIPHER_MISMATCH": -113,
    "ERR_SSL_UNRECOGNIZED_NAME_ALERT": -159,
    "ERR_BAD_SSL_CLIENT_AUTH_CERT": -117,
}

DEFAULT_RETRIES = 2
## Our tests will run quicker if we're not hanging around waiting for retry
DEFAULT_RETRY_WAIT = 0.02 if "IN_PYTEST" in os.environ else 2
