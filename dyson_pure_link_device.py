"""Dyson Pure Link Device Logic"""

import base64, json, hashlib, os, time
#import paho.mqtt.client as mqtt
import Domoticz
from queue import Queue, Empty

from value_types import CONNECTION_STATE, DISCONNECTION_STATE, FanMode, StandbyMonitoring, ConnectionError, DisconnectionError, SensorsData, StateData

class DysonPureLinkDevice(object):
    """Plugin to connect to Dyson Pure Link device and get its sensors readings"""

    def __init__(self, password, serialNumber, deviceType, ipAdress, portNum):
        self.client = None
        self.config = None
        self.connected = Queue()
        self.disconnected = Queue()
        self.state_data_available = Queue()
        self.sensor_data_available = Queue()
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

    # #@staticmethod
    # def on_connect(self, client, userdata, flags, return_code):
        # """Static callback to handle on_connect event"""
        # Domoticz.Debug("dyson_pure_link_device: on_connect called with return_code: '"+str(return_code)+"'")
        # # Connection is successful with return_code: 0
        # if return_code:
            # userdata.connected.put_nowait(False)
            # raise ConnectionError(return_code)

        # # We subscribe to the status message
        # client.subscribe(userdata.device_status)
        # userdata.connected.put_nowait(True)

    # #@staticmethod
    # def on_disconnect(self, client, userdata, return_code):
        # """Static callback to handle on_disconnect event"""
        # Domoticz.Debug("dyson_pure_link_device: on_disconnect called with return_code: '"+str(return_code)+"'")
        # self._is_connected = false
        # if return_code:
            # raise DisconnectionError(return_code)

        # userdata.disconnected.put_nowait(True)

    # #@staticmethod
    # def on_message(self, client, userdata, message):
        # """Static callback to handle incoming messages"""
        # Domoticz.Debug("dyson_pure_link_device: onMessage called, len: state_data: "+str(len(userdata.state_data_available))+" sensordata: "+str(len(userdata.sensor_data_available)))
        # payload = message.payload.decode("utf-8")
        # json_message = json.loads(payload)
        
        # if StateData.is_state_data(json_message):
            # userdata.state_data_available.put_nowait(StateData(json_message))

        # if SensorsData.is_sensors_data(json_message):
            # userdata.sensor_data_available.put_nowait(SensorsData(json_message))

    def _request_state(self):
        """Publishes request for current state message"""
        Domoticz.Debug("dyson_pure_link_device: _request_state called")
        # if self.client:
            # command = json.dumps({
                    # 'msg': 'REQUEST-CURRENT-STATE',
                    # 'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            
            # Domoticz.Debug("_request_state command built")
            # self.client.publish(self.device_command, command);

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

    def _hashed_password(self):
        """Hash password (found in manual) to a base64 encoded of its shad512 value"""
        hash = hashlib.sha512()
        hash.update(self.password.encode('utf-8'))
        return base64.b64encode(hash.digest()).decode('utf-8')
        
    def connect_device(self):
        """
        Connects to device using provided connection arguments

        Returns: True/False depending on the result of connection
        """
        Domoticz.Debug("dyson_pure_link_device: connect_device called")

        # self.client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311, userdata=self)
        # self.client.username_pw_set(self.serial_number, self._hashed_password())
        # self.client.on_connect = self.on_connect
        # self.client.on_disconnect = self.on_disconnect
        # self.client.on_message = self.on_message
        # try:
            # self.client.connect(self.ip_address, port=self.port_number)
        # except ConnectionRefusedError as e:
            # self._is_connected = False
            # Domoticz.Error("Connect device: Connection Refused")
            # return False

        # self.client.loop_start()

        # self._is_connected = self.connected.get(timeout=10)
        # Domoticz.Debug("dyson_pure_link_device: are we connected? " + str(self._is_connected))

        # if self._is_connected:
            # self._request_state()

            # self.state_data = self.state_data_available.get(timeout=5)
            # self.sensor_data = self.sensor_data_available.get(timeout=5)

            # # Return True in case of successful connect and data retrieval
            # return True

        # # If any issue occurred return False
        # self.client = None
        # return False

    def set_fan_mode(self, mode):
        """Changes fan mode: ON|OFF|AUTO"""
        if self._is_connected:
            self._change_state({'fmod': mode})

    def set_fan_speed(self, speed):
        """Changes fan speed: 0001..0010|AUTO"""
        if self._is_connected:
            self._change_state({'fnsp': speed})

    def set_standby_monitoring(self, mode):
        """Changes standby monitoring: ON|OFF"""
        if self._is_connected:
            self._change_state({'rhtm': mode})

    def set_night_mode(self, mode):
        """Changes night mode: ON|OFF"""
        if self._is_connected:
            self._change_state({'nmod': mode})

    def set_oscilation(self, mode):
        """Changes oscilation mode: ON|OFF"""
        if self._is_connected:
            self._change_state({'oson': mode})

    def get_data(self):
        Domoticz.Debug("dyson_pure_link_device: get_data called")
        if self._is_connected:
            self._request_state()

            self.state_data = self.state_data_available.get(timeout=5)
            self.sensor_data = self.sensor_data_available.get(timeout=5)

            # Return True in case of successful connect and data retrieval
            #Domoticz.Debug("dyson_pure_link_device: get_data, state_data: " + str(self.state_data))
            return (self.state_data, self.sensor_data) if self.has_valid_data else tuple()

        # If any issue occurred return False
        self.client = None
        return False

    def request_data(self):
        """send requets for new data to device"""
        if self._is_connected:
            self._request_state()

            self.state_data = self.state_data_available.get(timeout=5)
            self.sensor_data = self.sensor_data_available.get(timeout=5)

            # Return data in case of successful connect and data retrieval
            return (self.state_data, self.sensor_data) if self.has_valid_data else ('noValidData','noValidData')
        else:
            return ('disconnected','disconnected')
        
    def disconnect_device(self):
        """Disconnects device and return the boolean result"""
        Domoticz.Debug("pure link device class: disconnect_device")
        # if self.client:
            # self.client.loop_stop()
            # self.client.disconnect()
            
            # # Wait until we get on disconnect message
            # #self._is_connected = not(self.disconnected.get(timeout=10))
            # self._is_connected = False
            # return self._is_connected
