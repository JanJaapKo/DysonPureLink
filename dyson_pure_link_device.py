"""Dyson Pure Link Device Logic"""

import json, os, time
import Domoticz

from value_types import CONNECTION_STATE, DISCONNECTION_STATE, FanMode, StandbyMonitoring, ConnectionError, DisconnectionError, SensorsData, StateData

class DysonPureLinkDevice(object):
    """Plugin to connect to Dyson Pure Link device and get its sensors readings"""

    def __init__(self, password, serialNumber, deviceType, ipAdress, portNum):
        self.sensor_data = None
        self.state_data = None
        self._is_connected = False
        self._password = password
        self._serial_number = serialNumber
        self._device_type = deviceType
        self._ip_address = ipAdress
        self._port_number = int(portNum)

    @property
    def has_valid_data(self):
        return self.sensor_data and self.sensor_data.has_data
    
    def is_connected(self):
        return self._is_connected

    @property
    def password(self):
        return self._password

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def device_type(self):
        return self._device_type

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def port_number(self):
        return self._port_number

    @property
    def device_command(self):
        return '{0}/{1}/command'.format(self.device_type, self.serial_number)

    @property
    def device_status(self):
        return '{0}/{1}/status/current'.format(self.device_type, self.serial_number)

    def request_state(self):
        """creates request for current state message"""
        Domoticz.Debug("dyson_pure_link_device: request_state called")
        command = json.dumps({
                'msg': 'REQUEST-CURRENT-STATE',
                'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            
        Domoticz.Debug("request_state command built")
        return(self.device_command, command);

    def _create_command(self, data):
        """create change state message"""
        Domoticz.Debug("dyson_pure_link_device: _create_command called")
        command = json.dumps({
            'msg': 'STATE-SET',
            'mode-reason': 'LAPP',
            'data': data,
            'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        return command

    def set_fan_mode(self, mode):
        """Changes fan mode: ON|OFF|AUTO|FAN"""
        command = self._create_command({'fmod': mode})
        return(self.device_command, command);

    def set_fan_state(self, state):
        """Changes fan mode: ON|OFF|AUTO"""
        command = self._create_command({'fnst': state})
        return(self.device_command, command);

    def set_fan_speed(self, speed):
        """Changes fan speed: 0001..0010|AUTO"""
        command = self._create_command({'fnsp': speed})
        return(self.device_command, command);

    def set_standby_monitoring(self, mode):
        """Changes standby monitoring: ON|OFF"""
        command = self._create_command({'rhtm': mode})
        return(self.device_command, command);

    def set_night_mode(self, mode):
        """Changes night mode: ON|OFF"""
        command = self._create_command({'nmod': mode})
        return(self.device_command, command);

    def set_oscilation(self, mode):
        """Changes oscilation mode: ON|OFF"""
        command = self._create_command({'oson': mode})
        return(self.device_command, command);
