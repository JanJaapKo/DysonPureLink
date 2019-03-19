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
        #return self.state_data.has_data and self.sensor_data.has_data
    
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

    def _change_state(self, data):
        """Publishes request for change state message"""
        Domoticz.Debug("dyson_pure_link_device: _change_state called")
        # if self.client:
            
            # command = json.dumps({
                # 'msg': 'STATE-SET',
                # 'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                # 'mode-reason': 'LAPP',
                # 'data': data
            # })
            
            # Domoticz.Log("send MQTT command: " + command)

            # self.client.publish(self.device_command, command, 1)

            # self.state_data = self.state_data_available.get(timeout=5)

    def set_fan_mode(self, mode):
        """Changes fan mode: ON|OFF|AUTO"""
        self._change_state({'fmod': mode})

    def set_fan_speed(self, speed):
        """Changes fan speed: 0001..0010|AUTO"""
        self._change_state({'fnsp': speed})

    def set_standby_monitoring(self, mode):
        """Changes standby monitoring: ON|OFF"""
        self._change_state({'rhtm': mode})

    def set_night_mode(self, mode):
        """Changes night mode: ON|OFF"""
        self._change_state({'nmod': mode})

    def set_oscilation(self, mode):
        """Changes oscilation mode: ON|OFF"""
        self._change_state({'oson': mode})
