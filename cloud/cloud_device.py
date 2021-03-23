"""Dyson device cloud client."""


from .account import DysonAccount


class DysonCloudDevice:
    """Dyson device cloud client."""

    def __init__(self, account, serial):
        """Initialize the client."""
        self._account = account
        self._serial = serial
