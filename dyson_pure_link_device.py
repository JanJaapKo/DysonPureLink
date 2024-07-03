"""Dyson Pure Link Device Logic"""

import commands
from utils import decrypt_password

class DysonPureLinkDevice(commands.DysonCommands):
    """Dyson device created from plugin parameters"""

    def __init__(self, password, serialNumber, deviceType, name):
        self.sensor_data = None
        self.state_data = None
        self._is_connected = False
        self._password = decrypt_password(password)
        self._serial = serialNumber
        self._product_type = deviceType
        self._name = name

    @property
    def password(self):
        return self._password

    @property
    def device_base_topic(self):
        return '{0}/{1}'.format(self.product_type, self.serial)

    def __repr__(self):
        return "Dyson device called '{0}' with serial '{1}' of type '{2}'".format(self._name, self.serial, self.product_type)
