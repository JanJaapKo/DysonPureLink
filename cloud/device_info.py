"""Dyson device info."""

from .utils import decrypt_password

class DysonDeviceInfo:
    """Dyson device info."""
    active = True
    serial = '' 
    name = ''
    version = ''
    credential = ''
    auto_update = False
    new_version_available = False
    product_type = ''

    def __init__(self, active, serial, name, version, credential, auto_update, new_version_available, product_type):
        self.active = active
        self.serial = serial
        self.name = name
        self.version = version
        self.credential = credential
        self.auto_update = auto_update
        self.new_version_available = new_version_available
        self.product_type = product_type

    @classmethod
    def from_raw(cls, raw):
        """Parse raw data."""
        return cls(
            raw["Active"] if "Active" in raw else False,
            raw["Serial"],
            raw["Name"],
            raw["Version"],
            raw["LocalCredentials"],
            #decrypt_password(raw["LocalCredentials"]),
            raw["AutoUpdate"],
            raw["NewVersionAvailable"],
            raw["ProductType"],
        )
