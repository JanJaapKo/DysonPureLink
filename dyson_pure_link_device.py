"""Dyson Pure Link Device Logic"""

import commands

from value_types import CONNECTION_STATE, DISCONNECTION_STATE, FanMode, StandbyMonitoring, ConnectionError, DisconnectionError, SensorsData, StateData

class DysonPureLinkDevice(commands.DysonCommands):
    """Dyson device created from plugin parameters"""

    def __init__(self, password, serialNumber, deviceType):
        self.sensor_data = None
        self.state_data = None
        self._is_connected = False
        self._password = password
        self._serial = serialNumber
        self._product_type = deviceType

    @property
    def password(self):
        return self._password

    def __repr__(self):
        return 'Dyson device from plugin with serial {0} of type {1}'.format(self.serial, self.product_type)