"""Library of known Dyson devices"""

import Domoticz
from base_device import baseDevice
from value_types import FanMode

class fanMode(baseDevice):
    Options = {"LevelActions" : "|||",
           "LevelNames" : "|OFF|ON|AUTO",
           "LevelOffHidden" : "true",
           "SelectorStyle" : "1"}
    state = None

    def __init__(self, unit):
        _device_unit = unit
        _message_key = 'fmod'
        self._create(unit)

    def update(self, value):
        if self._device_unit not in Devices:
            self._create(self._device_unit)
        self.state = FanMode(self._get_field_value(value))
        self._update_device(nValue, sValue, BatteryLevel=255, AlwaysUpdate=False)
        
    def _create(self, unit):
        Domoticz.Device(Name='Fan mode', Unit=unit, TypeName="Selector Switch", Image=7, Options=self.Options).Create()
        