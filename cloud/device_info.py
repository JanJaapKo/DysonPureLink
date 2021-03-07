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

    @classmethod
    def from_raw(cls, raw):
        """Parse raw data."""
        return cls(
            raw["Active"] if "Active" in raw else None,
            raw["Serial"],
            raw["Name"],
            raw["Version"],
            decrypt_password(raw["LocalCredentials"]),
            raw["AutoUpdate"],
            raw["NewVersionAvailable"],
            raw["ProductType"],
        )
