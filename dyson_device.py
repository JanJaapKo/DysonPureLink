"""Base Dyson devices."""

import json
import time
import commands

from utils import printable_fields
from utils import decrypt_password

DEFAULT_PORT = 1883

class NetworkDevice:
    """Network device."""

    def __init__(self, name, address, port):
        """Create a new network device.

        :param name: Device name
        :param address: Device address
        :param port: Device port
        """
        self._name = name
        self._address = address
        self._port = port

    @property
    def name(self):
        """Device name."""
        return self._name

    @property
    def address(self):
        """Device address."""
        return self._address

    @property
    def port(self):
        """Device port."""
        return self._port

    def __repr__(self):
        """Return a String representation."""
        fields = [("name", self.name), ("address", self.address),
                  ("port", str(self.port))]
        return 'NetworkDevice(' + ",".join(printable_fields(fields)) + ')'


class DysonDevice(commands.DysonCommands):
    """Abstract Dyson device built from informantion from Cload Account."""

    def __init__(self, json_body):
        """Create a new Dyson device.

        :param json_body: JSON message returned by the HTTPS API
        """
        self._active = json_body['Active']
        self._name = json_body['Name'] #device name
        self._version = json_body['Version'] #sw version on device
        self._credentials = decrypt_password(json_body['LocalCredentials']) #registered password
        self._auto_update = json_body['AutoUpdate'] #
        self._new_version_available = json_body['NewVersionAvailable'] #is there a new version available?
        self._serial = json_body['Serial'] #device serial number
        self._product_type = json_body['ProductType'] #technical product type
        self._network_device = None
        self._connected = False
        self._device_available = False
        self._current_state = None

    @property
    def active(self):
        """Active status."""
        return self._active

    @property
    def name(self):
        """Device name."""
        return self._name

    @property
    def version(self):
        """Device version."""
        return self._version

    @property
    def password(self):
        """Device encrypted credentials."""
        return self._credentials

    @property
    def auto_update(self):
        """Auto update configuration."""
        return self._auto_update

    @property
    def new_version_available(self):
        """Return if new version available."""
        return self._new_version_available

    @property
    def network_device(self):
        """Network device."""
        return self._network_device

    @property
    def device_available(self):
        """Return True if device is fully available, else false."""
        return self._device_available

    def _fields(self):
        """Return list of field tuples."""
        fields = [("serial", self.serial), ("active", str(self.active)),
                  ("name", self.name), ("version", self.version),
                  ("auto_update", str(self.auto_update)),
                  ("new_version_available", str(self.new_version_available)),
                  ("product_type", self.product_type),
                  ("network_device", str(self.network_device))]
        return fields

    def __repr__(self):
        return "Dyson device from Cloud: '{0}' with serial '{1}' of type '{2}', with version '{3}'".format(self.name, self.serial, self.product_type, self.version)
