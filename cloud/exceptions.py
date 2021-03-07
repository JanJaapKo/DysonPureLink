"""Dyson exceptions."""


class DysonException(Exception):
    """Base class for exceptions."""
    pass

class DysonInvalidTargetTemperatureException(DysonException):
    """Invalid target temperature Exception."""

    CELSIUS = "Celsius"
    FAHRENHEIT = "Fahrenheit"

    def __init__(self, temperature_unit, current_value):
        """Dyson invalid target temperature.

        :param temperature_unit Celsius/Fahrenheit
        :param current_value invalid value
        """
        super(DysonInvalidTargetTemperatureException, self).__init__()
        self._temperature_unit = temperature_unit
        self._current_value = current_value

    @property
    def temperature_unit(self):
        """Temperature unit: Celsius or Fahrenheit."""
        return self._temperature_unit

    @property
    def current_value(self):
        """Return Current value."""
        return self._current_value

    def __repr__(self):
        """Return a String representation."""
        if self.temperature_unit == self.CELSIUS:
            return "{0} is not a valid temperature target. It must be " \
                   "between 1 to 37 inclusive.".format(self._current_value)
        if self.temperature_unit == self.FAHRENHEIT:
            return "{0} is not a valid temperature target. It must be " \
                   "between 34 to 98 inclusive.".format(self._current_value)


class DysonNotLoggedException(DysonException):
    """Not logged to Dyson Web Services Exception."""

    def __init__(self):
        """Dyson Not Logged Exception."""
        super(DysonNotLoggedException, self).__init__()
        
class DysonNetworkError(DysonException):
    """Represents network error."""
    pass


class DysonServerError(DysonException):
    """Represents Dyson server error."""
    pass

class DysonInvalidAccountStatus(DysonException):
    """Represents invalid account status."""
    pass

class DysonLoginFailure(DysonException):
    """Represents failure during logging in."""
    pass

class DysonOTPTooFrequently(DysonException):
    """Represents requesting OTP code too frequently."""
    pass

class DysonAuthRequired(DysonException):
    """Represents not logged into could."""
    pass

class DysonInvalidAuth(DysonException):
    """Represents invalid authentication."""
    pass

class DysonConnectTimeout(DysonException):
    """Represents mqtt connection timeout."""
    pass

class DysonNotConnected(DysonException):
    """Represents mqtt not connected."""
    pass

class DysonInvalidCredential(DysonException):
    """Requesents invalid mqtt credential."""
    pass

class DysonConnectionRefused(DysonException):
    """Represents mqtt connection refused by the server."""
    pass
