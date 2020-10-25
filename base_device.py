"""Dyson base device representation in Domoticz."""

import json, Domoticz

class baseDevice:
    _message_key = ""
    _device_unit = 0
        
    def create_command(self, argument):
        command = self._create_command({self._message_key: argument})
        return(command);

    def _create_command(self, data):
        """create change state message"""
        command = json.dumps({
            'msg': 'STATE-SET',
            'mode-reason': 'LAPP',
            'data': data,
            'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
        return command
    
    @property
    def device_unit(self):
        return self._device_unit
        
    @property
    def message_key(self):
        return self._message_key

    def _update_device(self, nValue, sValue, BatteryLevel=255, AlwaysUpdate=False):
        if self._device_unit not in Devices: return
        if Devices[self._device_unit].nValue != nValue\
            or Devices[self._device_unit].sValue != sValue\
            or Devices[self._device_unit].BatteryLevel != BatteryLevel\
            or AlwaysUpdate == True:

            Devices[self._device_unit].Update(nValue, str(sValue), BatteryLevel=BatteryLevel)

            Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
                Devices[self._device_unit].Name,
                nValue,
                sValue,
                BatteryLevel
            ))

    @staticmethod
    def _get_field_value(field):
        """Get field value"""
        return field[-1] if isinstance(field, list) else field
