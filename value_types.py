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

SENSOR_INIT_STATES = ['INIT', 'OFF', 'INV']

class Warnings():
    """Enum for warnings"""
    FILTER = 'Filter life exceeded'
    NONE = 'No warning'
    _warning = None
    
    def __init__(self, warning):
        """go from string to warning object"""
        if warning.upper() == 'FLTR': self._warning = self.FILTER
        else: 
            self._warning = self.NONE
    
    def __repr__(self):
        return self._warning

class Errors():
    """enums for error codes returned in state data"""
    NO_ERROR_CODES = ['02C0', '02C9']
    NO_ERROR = 'No error'
    OTHER = 'Error code: '
    _error = None
    
    def __init__(self, error):
        self._code = error
        if error in self.NO_ERROR_CODES: self._error = self.NO_ERROR
        else: self._error = self.OTHER
        
    def __repr__(self):
        error_text = self._error if self._error == self.NO_ERROR else self.OTHER + self._code
        return error_text

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
        if self._state == self.OFF: return 0
        if self._state == self.HEAT: return 1

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
    particulate_matter_25 = None
    particulate_matter_10 = None
    nitrogenDioxideDensity = None
    heat_target = None
    
    def __init__(self, message):
    
    #'data': {'tact': 'OFF', 'hact': 'OFF', 'pact': '0000', 'vact': '0003', 'sltm': 'OFF'}}
    
        data = message['data']
        humidity = data['hact']
        temperature = data['tact']
        sleep_timer = data['sltm']

        self.humidity = None if humidity in SENSOR_INIT_STATES else int(humidity)
        self.temperature = None if temperature in SENSOR_INIT_STATES else kelvin_to_celsius(float(temperature) / 10)
        self.sleep_timer = 0 if sleep_timer in SENSOR_INIT_STATES else int(sleep_timer)

        if 'pact' in data:
            self.particles = None if data['pact'] in SENSOR_INIT_STATES else int(data['pact'])
        if 'vact' in data:
            self.volatile_compounds = None if data['vact'] in SENSOR_INIT_STATES else int(data['vact'])
        if 'va10' in data:
            self.volatile_compounds = None if data['va10'] in SENSOR_INIT_STATES else int(data['va10'])
        if 'p25r' in data:
            self.particles2_5 = None if data['p25r'] in SENSOR_INIT_STATES else int(data['p25r'])
        if 'p10r' in data:
            self.particles10 = None if data['p10r'] in SENSOR_INIT_STATES else int(data['p10r']) 
        if 'pm25' in data:
            self.particulate_matter_25 = None if data['pm25'] in SENSOR_INIT_STATES else int(data['pm25'])
        if 'pm10' in data:
            self.particulate_matter_10 = None if data['pm10'] in SENSOR_INIT_STATES else int(data['pm10']) 
        if 'noxl' in data:
            self.nitrogenDioxideDensity = None if data['noxl'] in SENSOR_INIT_STATES else int(data['noxl'])

    def __repr__(self):
        """Return a String representation"""
        if self.particles is not None:
            particles = self.particles
        elif self.particles2_5 is not None:
            particles = "PM 2,5: {0}, PM 10: {1}".format(self.particles2_5, self.particles10)
        elif self.particulate_matter_25 is not None:
            particles = "PM 25: {0}, PM 10: {1}".format(self.particulate_matter_25, self.particulate_matter_10)
        else:
            particles = "no measurement"

        return 'SensorsData: Temperature: {:.1f} C, Humidity: {} %, Volatile Compounds: {}, Particles: {}, sleep timer: {}'.format(
            self.temperature, self.humidity, self.volatile_compounds, particles, self.sleep_timer)

    @property
    def has_data(self):
        return self.temperature is not None and self.humidity is not None

    @staticmethod
    def is_sensors_data(message):
        return message['msg'] in ['ENVIRONMENTAL-CURRENT-SENSOR-DATA']

class StateData(object):
    """Value type for state data"""
    error = None
    error_code = None
    fan_mode = None
    fan_mode_auto = None
    fan_state = None
    night_mode = None
    oscillation = None
    standby_monitoring = None
    fan_speed = None
    focus = None
    filter_life = None
    quality_target = None
    warning_code = None
    warning = None
    heat_mode = None
    heat_state = None
    heat_target = None
    oscillation_status = None
    night_mode_speed = None
    oscillation_angle_low = None
    oscillation_angle_high = None

    def __init__(self, message):
        data = message['product-state']
        
        if 'fmod' in data:
            self.fan_mode = FanMode(self._get_field_value(data['fmod'])) #  ON, OFF, AUTO, (FAN?)
        if 'fpwr' in data:
            self.fan_mode = FanMode(self._get_field_value(data['fpwr'])) # ON, OFF 
        if 'auto' in data:
            self.fan_mode_auto = FanMode(self._get_field_value(data['auto'])) # ON, OFF
        if 'fnst' in data:
            self.fan_state = FanMode(self._get_field_value(data['fnst'])) # ON , OFF, (FAN?)
        if 'nmod' in data:
            self.night_mode = FanMode(self._get_field_value(data['nmod'])) # ON , OFF
        if 'fnsp' in data:
            self.fan_speed = self._get_field_value(data['fnsp']) # 0001 - 0010, AUTO
        if 'oson' in data:
            self.oscillation = FanMode(self._get_field_value(data['oson'])) #ON , OFF
        if 'fdir' in data:
            self.focus = FanMode(self._get_field_value(data['fdir'])) #ON , OFF
        if 'hflr' in data:
            self.filter_life = None if self._get_field_value(data['hflr']) in SENSOR_INIT_STATES or self._get_field_value(data['cflr']) in SENSOR_INIT_STATES else int((int(self._get_field_value(data['hflr'])) + int(self._get_field_value(data['cflr']))) / 2) # // With TP04 models average cflr and hflr
        if 'filf' in data:
            self.filter_life = int(self._get_field_value(data['filf'])) #0000 - 4300
        if 'qtar' in data:
            self.quality_target = QualityTarget(self._get_field_value(data['qtar'])) #0001 (high), 0003 (medium) , 0004 (normal)
        if 'hmod' in data:
            self.heat_mode = HeatMode(self._get_field_value(data['hmod'])) #OFF, HEAT
        if 'hmax' in data:
            #self.heat_target = kelvin_to_celsius(self._get_field_value(data['hmax'])) #temperature target
            target = self._get_field_value(data['hmax'])
            self.heat_target = None if target == 'OFF' else int(kelvin_to_celsius(float(target) / 10))
        if 'hsta' in data:
            self.heat_state = HeatMode(self._get_field_value(data['hsta'])) #OFF, HEAT
        if 'rhtm' in data:
            self.standby_monitoring = FanMode(self._get_field_value(data['rhtm'])) # ON, OFF
        if 'oscs' in data:
            self.oscillation_status = FanMode(self._get_field_value(data['oscs'])) #ON , OFF
        if 'nmdv' in data:
            self.night_mode_speed = self._get_field_value(data['nmdv']) #0001 - 0010 ?
        if 'osal' in data:
            self.oscillation_angle_low = self._get_field_value(data['osal']) #0000 - 9999 ?
        if 'osau' in data:
            self.oscillation_angle_high = self._get_field_value(data['osau']) #0000 - 9999 ?

        self.error_code = self._get_field_value(data['ercd']) #I think this is an errorcode: NONE when filter needs replacement
        self.error = Errors(self.error_code)
        self.warning_code = self._get_field_value(data['wacd']) #I think this is Warning: FLTR when filter needs replacement
        self.warning = Warnings(self.warning_code)

    def __repr__(self):
        """Return a String representation"""
        return 'StateData: Fan mode: {0} + state: {1}, speed: {2}, AirQual target: {3} night mode: {4}, Oscillation: {5}, Filter life: {6}, Standby monitoring: {7}, error: {8}, warning: {9}'.format(
            self.fan_mode, self.fan_state, self.fan_speed, self.quality_target, self.night_mode, self.oscillation, self.filter_life, self.standby_monitoring, self.error, self.warning)

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
    return kelvin_value - 273.15
