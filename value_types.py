"""Value types, enums and mappings package"""

# Map for connection return code and its meaning
CONNECTION_STATE = {
    0: 'Connection successful',
    1: 'Connection refused: incorrect protocol version',
    2: 'Connection refused: invalid client identifier',
    3: 'Connection refused: server unavailable',
    4: 'Connection refused: bad username or password',
    5: 'Connection refused: not authorised',
    99: 'Connection refused: timeout'
}

DISCONNECTION_STATE = {
    0: 'Disconnection successful',
    50: 'Disconnection error: unexpected error',
    99: 'Disconnection error: timeout'
}

class FanMode():
    """Enum for fan mode"""

    OFF = 'OFF'
    ON = 'ON'
    AUTO = 'AUTO'
    _state = None
    
    def __init__(self, state):
        """go from string to state object"""
        #print("FanMode:init:state",state)
        if state.upper() == 'OFF': self._state = self.OFF
        if state.upper() == 'FAN': self._state = self.ON
        if state.upper() == 'ON': self._state = self.ON
        if state.upper() == 'AUTO': self._state = self.AUTO
        #print("FanMode:init:_state",self._state)
    
    def __repr__(self):
        return self._state
        
    @property
    def state(self):
        if self._state == self.OFF: return 0
        if self._state == self.ON: return 1
        if self._state == self.AUTO: return 2
    
class StandbyMonitoring(object):
    """Enum for monitor air quality when on standby"""

    ON = 'ON'
    OFF = 'OFF'

"""Custom Errors"""


class ConnectionError(Exception):
    """Custom error to handle connect device issues"""

    def __init__(self, return_code, *args):
        super(ConnectionError, self).__init__(*args)
        self.message = CONNECTION_STATE[return_code]

class DisconnectionError(Exception):
    """Custom error to handle disconnect device issues"""
    def __init__(self, return_code, *args):
        super(DisconnectionError, self).__init__(*args)
        self.message = DISCONNECTION_STATE[return_code] if return_code in DISCONNECTION_STATE else DISCONNECTION_STATE[50]

class SensorsData(object):
    """Value type for sensors data"""

    def __init__(self, message):
        data = message['data']
        humidity = data['hact']
        temperature = data['tact']
        volatile_compounds = data['vact']
        sleep_timer = data['sltm']

        self.particles = int(data['pact'])
        self.humidity = None if humidity == 'OFF' else int(humidity)
        self.temperature = None if temperature == 'OFF' else self.kelvin_to_celsius(float(temperature) / 10)
        self.volatile_compounds = 0 if volatile_compounds == 'INIT' else int(volatile_compounds)
        self.sleep_timer = 0 if sleep_timer == 'OFF' else int(sleep_timer)

    def __repr__(self):
        """Return a String representation"""
        return 'SensorsData: Temperature: {0} C, Humidity: {1} %, Volatile Compounds: {2}, Particles: {3}, sleep timer: {4}'.format(
            self.temperature, self.humidity, self.volatile_compounds, self.particles, self.sleep_timer)

    @property
    def has_data(self):
        return self.temperature is not None or self.humidity is not None

    @staticmethod
    def is_sensors_data(message):
        return message['msg'] in ['ENVIRONMENTAL-CURRENT-SENSOR-DATA']

    @staticmethod
    def kelvin_to_fahrenheit (kelvin_value):
        return kelvin_value * 9 / 5 - 459.67

    @staticmethod
    def kelvin_to_celsius (kelvin_value):
        return kelvin_value - 272.15

class StateData(object):
    """Value type for state data"""
    fan_mode = None
    fan_modeC = None
    fan_state = None
    night_mode = None
    oscillation = None
    standby_monitoring = None
    fan_speed = None

    def __init__(self, message):
        data = message['product-state']
        
        #print("StateData.init: incoming data: ", data)
        #print("StateData.init: incoming message: ", message)

        self.fan_mode = FanMode(self._get_field_value(data['fmod'])) #  ON, OFF, AUTO, (FAN?)
        self.fan_state = FanMode(self._get_field_value(data['fnst'])) # ON , OFF, (FAN?)
        self.night_mode = FanMode(self._get_field_value(data['nmod'])) # ON , OFF
        self.fan_speed = self._get_field_value(data['fnsp']) # 0001 - 0010, AUTO
        self.oscillation = FanMode(self._get_field_value(data['oson'])) #ON , OFF
        self.filter_life = int(self._get_field_value(data['filf'])) #0000 - 4300
        self.quality_target = self._get_field_value(data['qtar']) #0001 , 0003...
        self.standby_monitoring = FanMode(self._get_field_value(data['rhtm'])) # ON, OFF
        self.error_code = self._get_field_value(data['ercd']) #I think this is an errorcode: NONE when filter needs replacement
        self.warning_code = self._get_field_value(data['wacd']) #I think this is Warning: FLTR when filter needs replacement
        #print("StateData.init: all message fields parsed.")
        

    def __repr__(self):
        """Return a String representation"""
        return 'StateData: Fan mode: {0} + state: {1}, speed: {2}, AirQual: {3} night mode: {4}, Oscillation: {5}, Filter life: {6}, Standby monitoring: {7}, ErrCode: {8}'.format(
            self.fan_mode, self.fan_state, self.fan_speed, self.quality_target, self.night_mode, self.oscillation, self.filter_life, self.standby_monitoring, self.error_code)

    @property
    def has_data(self):
        return self.fan_speed is not None or self.fan_mode is not None

    @staticmethod
    def _get_field_value(field):
        """Get field value"""
        return field[-1] if isinstance(field, list) else field

    @staticmethod
    def is_state_data(message):
        return message['msg'] in ['CURRENT-STATE', 'STATE-CHANGE']
