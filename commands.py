"""basic commands for Dyson devices"""

import json, os, time
from cloud.exceptions import DysonInvalidTargetTemperatureException as DITTE

class DysonCommands(object):

    def __init__(self):
        self._serial = None
        self._product_type = None

    @property
    def serial(self):
        return self._serial

    @property
    def product_type(self):
        return self._product_type

    @property
    def device_command(self):
        return '{0}/{1}/command'.format(self.product_type, self.serial)

    @property
    def device_base_topic(self):
        return '{0}/{1}'.format(self.product_type, self.serial)

    @property
    def device_status(self):
        return '{0}/{1}/status/current'.format(self.product_type, self.serial)
        
    def request_state(self):
        """creates request for current state message"""
        command = json.dumps({
                'msg': 'REQUEST-CURRENT-STATE',
                'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            
        return(self.device_command, command);

    def _create_command(self, data):
        """create change state message"""
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

    def set_focus(self, mode):
        """Changes focus mode: ON|OFF"""
        command = self._create_command({'fdir': mode})
        return(self.device_command, command);

    def set_fan_mode_auto(self, mode):
        """Changes auto mode: ON|OFF"""
        command = self._create_command({'auto': mode})
        return(self.device_command, command);

    def set_fan_power(self, mode):
        """Changes power mode: ON|OFF"""
        #this command is to be determined to be ok
        command = self._create_command({'fpwr': mode})
        return(self.device_command, command);

    def set_heat_mode(self, mode):
        """Changes heating mode: HEAT|OFF"""
        command = self._create_command({'hmod': mode})
        return(self.device_command, command);

    def set_quality_target(self, mode):
        """Changes quality target: 0001..0004"""
        if mode == 10 : level = 4
        if mode == 20 : level = 3
        if mode == 30 : level = 1
        arg="000"+str(level)
        command = self._create_command({'qtar': arg})
        return(self.device_command, command);

    def set_heat_target(self, target):
        """Sends the target temperature"""
        arg = HeatTarget.celsius(target)
        command = self._create_command({'hmax': arg})
        return(self.device_command, command);

    def reset_filter(self):
        """Sends the command to reset the filter life counter"""
        command = self._create_command({'rstf': 'RSTF'})
        return(self.device_command, command);

class HeatTarget:
    """Heat Target for fan. Note dyson uses kelvin as the temperature unit."""

    @staticmethod
    def celsius(temperature):
        """Convert the given int celsius temperature to string in Kelvin.

        :param temperature temperature in celsius between 1 to 37 inclusive.
        """
        if temperature < 1 or temperature > 37:
            raise DITTE(DITTE.CELSIUS, temperature)
        return str((int(temperature) + 273) * 10)

    @staticmethod
    def fahrenheit(temperature):
        """Convert the given int fahrenheit temperature to string in Kelvin.

        :param temperature temperature in fahrenheit between 34 to 98
                            inclusive.
        """
        if temperature < 34 or temperature > 98:
            raise DITTE(DITTE.FAHRENHEIT, temperature)
        return str(int((int(temperature) + 459.67) * 5/9) * 10)
