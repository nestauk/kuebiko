## Defining custom exceptions allows us to pin-point specific errors within
## our model of the system and handle them appropriately
class PossibleSchemeError(Exception):
    """Indicates Selenium scraping failed, likely due to scheme error."""

    pass


class BrowserCrashError(Exception):
    """Indicates Selenium scraping failed due to browser crash."""

    pass
