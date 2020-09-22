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
        if state.upper() == 'OFF': self._state = self.OFF
        if state.upper() == 'FAN': self._state = self.ON
        if state.upper() == 'ON': self._state = self.ON
        if state.upper() == 'AUTO': self._state = self.AUTO
    
    def __repr__(self):
        return self._state
        
    @property
    def state(self):
        if self._state == self.OFF: return 0
        if self._state == self.ON: return 1
        if self._state == self.AUTO: return 2

class QualityTarget():
    """Enum for air quality target"""
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    NORMAL = 'NORMAL'
    UNKNOWN = 'UNKNOWN'
    OFF = 'OFF'
    _state = None
    
    def __init__(self, state):
        """go from string to state object"""
        if state.upper() == '0001': self._state = self.HIGH
        if state.upper() == '0002': self._state = self.UNKNOWN
        if state.upper() == '0003': self._state = self.MEDIUM
        if state.upper() == '0004': self._state = self.NORMAL
        if state.upper() == 'OFF': self._state = self.OFF
    
    def __repr__(self):
        return self._state
        
    @property
    def state(self):
        if self._state == self.NORMAL: return 0
        if self._state == self.MEDIUM: return 1
        if self._state == self.HIGH: return 2
        if self._state == self.UNKNOWN: return 3
        if self._state == self.OFF: return 4
    
class StandbyMonitoring(object):
    """Enum for monitor air quality when on standby"""

    ON = 'ON'
    OFF = 'OFF'

class HeatMode():
    """Enum for heater mode and state"""

    HEAT = 'HEAT'
    OFF = 'OFF'
    _state = None
    
    def __init__(self, state):
        """go from string to state object"""
        if state.upper() == 'OFF': self._state = self.OFF
        if state.upper() == 'HEAT': self._state = self.HEAT

    def __repr__(self):
        return self._state

    @property
    def state(self):
        if self._state == self.OFF: return 10
        if self._state == self.HEAT: return 20

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
    humidity = None
    temperature = None
    volatile_compounds = None
    particles = None
    particles2_5 = None
    particles10 = None
    nitrogenDioxideDensity = None
    heat_target = None
    
    def __init__(self, message):
        data = message['data']
        humidity = data['hact']
        temperature = data['tact']
        volatile_compounds = data['vact']
        sleep_timer = data['sltm']

        if 'pact' in data:
            self.particles = None if data['pact'] == 'INIT' or data['pact'] == 'OFF' else int(data['pact'])
        self.humidity = None if humidity == 'OFF' else int(humidity)
        self.temperature = None if temperature == 'OFF' else kelvin_to_celsius(float(temperature) / 10)
        self.volatile_compounds = None if volatile_compounds == 'INIT' or volatile_compounds == 'OFF' else int(volatile_compounds)
        self.sleep_timer = 0 if sleep_timer == 'OFF' else int(sleep_timer)

        if 'p25r' in data:
            self.particles2_5 = int(data['p25r'])
        if 'p10r' in data:
            self.particles10 = int(data['p10r']) 
        if 'noxl' in data:
            self.nitrogenDioxideDensity = int(data['noxl'])

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

class StateData(object):
    """Value type for state data"""
    fan_mode = None
    fan_mode_auto = None
    fan_state = None
    night_mode = None
    oscillation = None
    standby_monitoring = None
    fan_speed = None
    focus = None
    filter_life = None
    error_code = None
    warning_code = None
    heat_mode = None
    heat_target = None

    def __init__(self, message):
        data = message['product-state']
        
        if 'fmod' in data:
            self.fan_mode = FanMode(self._get_field_value(data['fmod'])) #  ON, OFF, AUTO, (FAN?)
        if 'fpwr' in data:
            self.fan_mode = FanMode(self._get_field_value(data['fpwr'])) # ON, OFF 
        if 'auto' in data:
            self.fan_mode_auto = FanMode(self._get_field_value(data['auto'])) # ON, OFF
        self.fan_state = FanMode(self._get_field_value(data['fnst'])) # ON , OFF, (FAN?)
        self.night_mode = FanMode(self._get_field_value(data['nmod'])) # ON , OFF
        self.fan_speed = self._get_field_value(data['fnsp']) # 0001 - 0010, AUTO
        self.oscillation = FanMode(self._get_field_value(data['oson'])) #ON , OFF
        if 'fdir' in data:
            self.focus = FanMode(self._get_field_value(data['fdir'])) #ON , OFF
        if 'hflr' in data:
            self.filter_life = int((int(self._get_field_value(data['hflr'])) + int(self._get_field_value(data['cflr']))) / 2) # // With TP04 models average cflr and hflr
        if 'filf' in data:
            self.filter_life = int(self._get_field_value(data['filf'])) #0000 - 4300
        if 'qtar' in data:
            self.quality_target = QualityTarget(self._get_field_value(data['qtar'])) #0001 (high), 0003 (medium) , 0004 (normal)
        if 'hmod' in data:
            self.heat_mode = HeatMode(self._get_field_value(data['hmod'])) #OFF, HEAT
        if 'hmax' in data:
            #self.heat_target = kelvin_to_celsius(self._get_field_value(data['hmax'])) #temperature target
            target = data['hmax']
            self.heat_target = None if target == 'OFF' else kelvin_to_celsius(float(target) / 10)


        self.standby_monitoring = FanMode(self._get_field_value(data['rhtm'])) # ON, OFF
        self.error_code = self._get_field_value(data['ercd']) #I think this is an errorcode: NONE when filter needs replacement
        self.warning_code = self._get_field_value(data['wacd']) #I think this is Warning: FLTR when filter needs replacement

    def __repr__(self):
        """Return a String representation"""
        return 'StateData: Fan mode: {0} + state: {1}, speed: {2}, AirQual target: {3} night mode: {4}, Oscillation: {5}, Filter life: {6}, Standby monitoring: {7}, ErrCode: {8}'.format(
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

def kelvin_to_fahrenheit (kelvin_value):
    return kelvin_value * 9 / 5 - 459.67

def kelvin_to_celsius (kelvin_value):
    return kelvin_value - 272.15
