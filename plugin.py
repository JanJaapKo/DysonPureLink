# Basic Python Plugin Example
#
# Author: Jan-Jaap Kostelijk
#
"""
<plugin key="DysonPureLink" name="Dyson Pure Link" author="Jan-Jaap Kostelijk" version="3.0.2" wikilink="https://github.com/JanJaapKo/DysonPureLink/wiki" externallink="https://github.com/JanJaapKo/DysonPureLink">
    <description>
        <h2>Dyson Pure Link plugin</h2><br/>
        Connects to Dyson Pure Link devices.
        It reads the machine's states and sensors and it can control it via commands.<br/><br/>
		This plugin has been tested with a PureCool type 475 (pre 2018), it is assumed the other types work too. There are known issues in retreiving information from the cloud account, see git page for the issues.<br/><br/>
        <h2>Configuration</h2>
        To configure the plugin, provide all in step A and choose step B or C. See the Wiki for more info.<br/><br/>
        <ol type="A">
            <li>provide the machine's local network adress:</li>
            <ol>
                <li>the machine's IP adress</li>
                <li>the port number (should normally remain 1883)</li>
            </ol>
            <li>When using local credentials as on your Pure Cool Link device, provide:</li>
            <ol>
                <li>select the correct machine type number</li>
                <li>enter the device serial number</li>
                <li>enter the device password</li>
            </ol>
            <li>When using the Dyson account credentials, provide:</li>
            <ol>
                <li>enter the email adress under "Cloud account email adress"</li>
                <li>enter the password under "Cloud account password"</li>
                <li>optional: enter the machine's name under "machine name" when there is more than 1 machines linked to the account</li>
            </ol>
        </ol>
        
    </description>
    <params>
		<param field="Address" label="IP Address" required="true"/>
		<param field="Port" label="Port" width="30px" required="true" default="1883"/>
		<param field="Mode1" label="Dyson type number (local)" width="75px">
            <options>
                <option label="438" value="438"/>
                <option label="455" value="455"/>
                <option label="465" value="465"/>
                <option label="469" value="469"/>
                <option label="475" value="475" default="true"/>
                <option label="527" value="527"/>
            </options>
        </param>
		<param field="Username" label="Device Serial No. (local)" required="false"/>
		<param field="Password" label="Device Password (local, see machine)" required="false" password="true"/>
		<param field="Mode5" label="Cloud account email adress" default="sinterklaas@gmail.com" width="300px" required="false"/>
        <param field="Mode3" label="Cloud account password" required="false" default="" password="true"/>
        <param field="Mode6" label="Machine name (cloud account)" required="false" default=""/>
		<param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
        <param field="Mode2" label="Refresh interval" width="75px">
            <options>
                <option label="20s" value="2"/>
                <option label="1m" value="6"/>
                <option label="5m" value="30" default="true"/>
                <option label="10m" value="60"/>
                <option label="15m" value="90"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import time
import base64, hashlib
from mqtt import MqttClient
from dyson_pure_link_device import DysonPureLinkDevice
from dyson import DysonAccount
from value_types import SensorsData, StateData

class DysonPureLinkPlugin:
    #define class variables
    enabled = False
    mqttClient = None
    #unit numbers for devices to create
    #for Pure Cool models
    fanModeUnit = 1
    nightModeUnit = 2
    fanSpeedUnit = 3
    fanSpeedUnitV2 = 23
    fanOscillationUnit = 4
    standbyMonitoringUnit = 5
    filterLifeUnit = 6
    qualityTargetUnit = 7
    tempHumUnit = 8
    volatileUnit = 9
    particlesUnit = 10
    sleepTimeUnit = 11
    fanStateUnit = 12
    fanFocusUnit = 13
    fanModeAutoUnit = 14
    particles2_5Unit = 15
    particles10Unit = 16
    nitrogenDioxideDensityUnit = 17
    heatModeUnit = 18
    heatTargetUnit = 19
    heatStateUnit = 20
    particlesMatter25Unit = 21
    particlesMatter10Unit = 22


    runCounter = 6
    pingCounter = 3

    def __init__(self):
        self.myDevice = None
        self.password = None
        self.ip_address = None
        self.port_number = None
        self.sensor_data = None
        self.state_data = None
        self.mqttClient = None

    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters['Mode4'] == 'Debug':
            Domoticz.Debugging(2)
            DumpConfigToLog()
        if Parameters['Mode4'] == 'Verbose':
            Domoticz.Debugging(1+2+4+8+16+64)
            DumpConfigToLog()
        
        #PureLink needs polling, get from config
        Domoticz.Heartbeat(10)
        
        #read out parameters for local connection
        self.ip_address = Parameters["Address"].strip()
        self.port_number = Parameters["Port"].strip()
        self.password = self._hashed_password(Parameters['Password'])
        mqtt_client_id = ""
        self.runCounter = int(Parameters['Mode2'])
        self.pingCounter = int(self.runCounter/2)
        
        #create a Dyson account
        Domoticz.Debug("=== start making connection to Dyson account ===")
        dysonAccount = DysonAccount(Parameters['Mode5'], Parameters['Mode3'], "NL")
        dysonAccount.login()
        #deviceList = ()
        deviceList = []
        deviceList = dysonAccount.devices()
        
        if deviceList == None or len(deviceList)<1:
            Domoticz.Log("No devices found in Dyson cloud account")
        else:
            Domoticz.Debug("Number of devices from cloud: '"+str(len(deviceList))+"'")

        if deviceList != None and len(deviceList) > 0:
            if len(Parameters['Mode6']) > 0:
                if Parameters['Mode6'] in deviceList:
                    self.myDevice = deviceList[Parameters['Mode6']]
                else:
                    Domoticz.Error("The configured device name '" + Parameters['Mode6'] + "' was not found in the cloud account. Available options: " + str(list(deviceList)))
                    return
            elif len(deviceList) == 1:
                self.myDevice = deviceList[list(deviceList)[0]]
                Domoticz.Log("1 device found in cloud, none configured, assuming we need this one: '" + self.myDevice.name + "'")
            else:
                Domoticz.Error("More than 1 device found in cloud account but no device name given to select")
                return
            Domoticz.Debug("local device pwd:      '"+self.password+"'")
            Domoticz.Debug("cloud device pwd:      '"+self.myDevice.password+"'")
            Parameters['Username'] = self.myDevice.serial #take username from account
            Parameters['Password'] = self.myDevice.password #override the default password with the one returned from the cloud
        elif len(Parameters['Username'])>0:
            Domoticz.Log("No cloud devices found, the local credentials will be used")
            #create a Dyson device object using plugin parameters
            Domoticz.Debug("local device pwd:      '"+self.password+"'")
            Domoticz.Debug("local device usn:      '"+Parameters['Username']+"'")
            Parameters['Password'] = self.password
            self.myDevice = DysonPureLinkDevice(Parameters['Password'], Parameters['Username'], Parameters['Mode1'])
        else:
            Domoticz.Error("No usable credentials found")
            return

        #check, per device, if it is created. If not,create it
        Options = {"LevelActions" : "|||",
                   "LevelNames" : "|OFF|ON|AUTO",
                   "LevelOffHidden" : "true",
                   "SelectorStyle" : "1"}
        if self.fanModeUnit not in Devices:
            Domoticz.Device(Name='Fan mode', Unit=self.fanModeUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()
        if self.fanStateUnit not in Devices:
            Domoticz.Device(Name='Fan state', Unit=self.fanStateUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.heatStateUnit not in Devices:
            Domoticz.Device(Name='Heating state', Unit=self.heatStateUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.nightModeUnit not in Devices:
            Domoticz.Device(Name='Night mode', Unit=self.nightModeUnit, Type=244, Subtype=62,  Switchtype=0, Image=9).Create()
            
        Options = {"LevelActions" : "|||||||||||",
                   "LevelNames" : "|1|2|3|4|5|6|7|8|9|10|Auto",
                   "LevelOffHidden" : "true",
                   "SelectorStyle" : "1"}
        if self.fanSpeedUnit not in Devices:
            Domoticz.Device(Name='Fan speed', Unit=self.fanSpeedUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()
        Options = {"LevelActions" : "|||||||||||",
            "LevelNames" : "1|2|3|4|5|6|7|8|9|10|AUTO",
            "LevelOffHidden" : "false",
            "SelectorStyle" : "1"}
        if self.fanSpeedUnitV2 not in Devices:
            Domoticz.Device(Name='Fan speed', Unit=self.fanSpeedUnitV2, TypeName="Selector Switch", Image=7, Options=Options).Create()

        if self.fanOscillationUnit not in Devices:
            Domoticz.Device(Name='Oscilation mode', Unit=self.fanOscillationUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.standbyMonitoringUnit not in Devices:
            Domoticz.Device(Name='Standby monitor', Unit=self.standbyMonitoringUnit, Type=244, Subtype=62,Image=7, Switchtype=0).Create()
        if self.filterLifeUnit not in Devices:
            Domoticz.Device(Name='Remaining filter life', Unit=self.filterLifeUnit, TypeName="Custom").Create()
        if self.tempHumUnit not in Devices:
            Domoticz.Device(Name='Temperature and Humidity', Unit=self.tempHumUnit, TypeName="Temp+Hum").Create()
        if self.volatileUnit not in Devices:
            Domoticz.Device(Name='Volatile organic', Unit=self.volatileUnit, TypeName="Air Quality").Create()
        if self.sleepTimeUnit not in Devices:
            Domoticz.Device(Name='Sleep timer', Unit=self.sleepTimeUnit, TypeName="Custom").Create()

        if self.particlesUnit not in Devices:
            Domoticz.Device(Name='Dust', Unit=self.particlesUnit, TypeName="Air Quality").Create()
        if self.qualityTargetUnit not in Devices:
            Options = {"LevelActions" : "|||",
                       "LevelNames" : "|Normal|Sensitive (Medium)|Very Sensitive (High)|Off",
                       "LevelOffHidden" : "true",
                       "SelectorStyle" : "1"}
            Domoticz.Device(Name='Air quality setpoint', Unit=self.qualityTargetUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()

        if self.particles2_5Unit not in Devices:
            Domoticz.Device(Name='Dust (PM 2,5)', Unit=self.particles2_5Unit, TypeName="Air Quality").Create()
        if self.particles10Unit not in Devices:
            Domoticz.Device(Name='Dust (PM 10)', Unit=self.particles10Unit, TypeName="Air Quality").Create()
        if self.particlesMatter25Unit not in Devices:
            Domoticz.Device(Name='Particles (PM 25)', Unit=self.particlesMatter25Unit, TypeName="Air Quality").Create()
        if self.particlesMatter10Unit not in Devices:
            Domoticz.Device(Name='Particles (PM 10)', Unit=self.particlesMatter10Unit, TypeName="Air Quality").Create()
        if self.fanModeAutoUnit not in Devices:
            Domoticz.Device(Name='Fan mode auto', Unit=self.fanModeAutoUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.fanFocusUnit not in Devices:
            Domoticz.Device(Name='Fan focus mode', Unit=self.fanFocusUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.nitrogenDioxideDensityUnit not in Devices:
            Domoticz.Device(Name='Nitrogen Dioxide Density (NOx)', Unit=self.nitrogenDioxideDensityUnit, TypeName="Air Quality").Create()
        if self.heatModeUnit not in Devices:
            Options = {"LevelActions" : "||",
                       "LevelNames" : "|Off|Heating",
                       "LevelOffHidden" : "true",
                       "SelectorStyle" : "1"}
            Domoticz.Device(Name='Heat mode', Unit=self.heatModeUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()
        if self.heatTargetUnit not in Devices:
            Domoticz.Device(Name='Heat target', Unit=self.heatTargetUnit, Type=242, Subtype=1).Create()


        Domoticz.Log("Device instance created: " + str(self.myDevice))
        self.base_topic = self.myDevice.device_base_topic
        Domoticz.Debug("base topic defined: '"+self.base_topic+"'")

        #create the connection
        if self.myDevice != None:
            self.mqttClient = MqttClient(self.ip_address, self.port_number, mqtt_client_id, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
    
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("DysonPureLink plugin: onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        topic = ''
        payload = ''
        
        if Unit == self.qualityTargetUnit and Level<=100:
            topic, payload = self.myDevice.set_quality_target(Level)
        if Unit == self.fanSpeedUnitV2:
            if Level<=90:
                arg="0000"+str(1+Level//10)
                topic, payload = self.myDevice.set_fan_speed(arg[-4:]) #use last 4 characters as speed level or AUTO
            else:
                topic, payload = self.myDevice.set_fan_mode_auto("ON") #use last 4 characters as speed level or AUTO
        if Unit == self.fanSpeedUnit and Level<=100:
            arg="0000"+str(Level//10)
            topic, payload = self.myDevice.set_fan_speed(arg[-4:]) #use last 4 characters as speed level or AUTO
        if Unit == self.fanModeUnit or (Unit == self.fanSpeedUnit and Level>100):
            if Level == 10: arg="OFF"
            if Level == 20: arg="FAN"
            if Level >=30: arg="AUTO"
            topic, payload = self.myDevice.set_fan_mode(arg) 
        if Unit == self.fanStateUnit:
            if Level == 10: arg="OFF"
            if Level == 20: arg="ON"
            topic, payload = self.myDevice.set_fan_state(arg) 
        if Unit == self.fanOscillationUnit:
            topic, payload = self.myDevice.set_oscilation(str(Command).upper()) 
        if Unit == self.fanFocusUnit:
            topic, payload = self.myDevice.set_focus(str(Command).upper()) 
        if Unit == self.fanModeAutoUnit:
            topic, payload = self.myDevice.set_fan_mode_auto(str(Command).upper()) 
        if Unit == self.standbyMonitoringUnit:
            topic, payload = self.myDevice.set_standby_monitoring(str(Command).upper()) 
        if Unit == self.nightModeUnit:
            topic, payload = self.myDevice.set_night_mode(str(Command).upper()) 
        if Unit == self.heatModeUnit:
            if Level == 10: arg="OFF"
            if Level == 20: arg="HEAT"
            topic, payload = self.myDevice.set_heat_mode(arg) 
        if Unit == self.heatTargetUnit:
            topic, payload = self.myDevice.set_heat_target(Level) 

        self.mqttClient.Publish(topic, payload)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called: Connection '"+str(Connection)+"', Status: '"+str(Status)+"', Description: '"+Description+"'")
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("DysonPureLink plugin: onNotification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onHeartbeat(self):
        if self.myDevice != None:
            self.runCounter = self.runCounter - 1
            # self.pingCounter = self.pingCounter - 1
            # if self.pingCounter <= 0 and self.runCounter > 0:
                # self.mqttClient.onHeartbeat()
                # self.pingCounter = int(int(Parameters['Mode2'])/2)
            if self.runCounter <= 0:
                Domoticz.Debug("DysonPureLink plugin: Poll unit")
                self.runCounter = int(Parameters['Mode2'])
                #self.pingCounter = int(int(Parameters['Mode2'])/2)
                topic, payload = self.myDevice.request_state()
                self.mqttClient.Publish(topic, payload) #ask for update of current status
                
            else:
                Domoticz.Debug("Polling unit in " + str(self.runCounter) + " heartbeats.")
                self.mqttClient.onHeartbeat()

    def onDeviceRemoved(self, unit):
        Domoticz.Log("DysonPureLink plugin: onDeviceRemoved called for unit '" + str(unit) + "'")
    
    def updateDevices(self):
        """Update the defined devices from incoming mesage info"""
        #update the devices
        if self.state_data.oscillation is not None:
            UpdateDevice(self.fanOscillationUnit, self.state_data.oscillation.state, str(self.state_data.oscillation))
        if self.state_data.night_mode is not None:
            UpdateDevice(self.nightModeUnit, self.state_data.night_mode.state, str(self.state_data.night_mode))

        # Fan speed  
        if self.state_data.fan_speed is not None:
            f_rate = self.state_data.fan_speed
            if (f_rate == "AUTO"):
                sValueNew = "110" # Auto
            else:
                sValueNew = str(int(f_rate) * 10)
            UpdateDevice(self.fanSpeedUnit, 1, sValueNew)
        if self.state_data.fan_speed is not None:
            # Fan speed  
            f_rate = self.state_data.fan_speed
    
            if (f_rate == "AUTO"):
                nValueNew = 100
                sValueNew = "100" # Auto
            else:
                nValueNew = (int(f_rate)-1)*10
                sValueNew = str((int(f_rate)-1) * 10)
            UpdateDevice(self.fanSpeedUnitV2, nValueNew, sValueNew)
        
        if self.state_data.fan_mode is not None:
            UpdateDevice(self.fanModeUnit, self.state_data.fan_mode.state, str((self.state_data.fan_mode.state+1)*10))
        if self.state_data.fan_state is not None:
            UpdateDevice(self.fanStateUnit, self.state_data.fan_state.state, str((self.state_data.fan_state.state+1)*10))
        if self.state_data.filter_life is not None:
            UpdateDevice(self.filterLifeUnit, self.state_data.filter_life, str(self.state_data.filter_life))
        if self.state_data.quality_target is not None:
            UpdateDevice(self.qualityTargetUnit, self.state_data.quality_target.state, str((self.state_data.quality_target.state+1)*10))
        if self.state_data.standby_monitoring is not None:
            UpdateDevice(self.standbyMonitoringUnit, self.state_data.standby_monitoring.state, str((self.state_data.standby_monitoring.state+1)*10))
        if self.state_data.fan_mode_auto is not None:
            UpdateDevice(self.fanModeAutoUnit, self.state_data.fan_mode_auto.state, str((self.state_data.fan_mode_auto.state+1)*10))
        if self.state_data.focus is not None:
            UpdateDevice(self.fanFocusUnit, self.state_data.focus.state, str(self.state_data.focus))
        if self.state_data.heat_mode is not None:
            UpdateDevice(self.heatModeUnit, self.state_data.heat_mode.state, str((self.state_data.heat_mode.state+1)*10))
        if self.state_data.heat_target is not None:
            UpdateDevice(self.heatTargetUnit, 0, str(self.state_data.heat_target))
        if self.state_data.heat_state is not None:
            UpdateDevice(self.heatStateUnit, self.state_data.heat_state.state, str((self.state_data.heat_state.state+1)*10))
        Domoticz.Debug("update StateData: " + str(self.state_data))


    def updateSensors(self):
        """Update the defined devices from incoming mesage info"""
        #update the devices
        if self.sensor_data.temperature is not None and self.sensor_data.humidity is not None :
            tempNum = int(self.sensor_data.temperature)
            humNum = int(self.sensor_data.humidity)
            UpdateDevice(self.tempHumUnit, 1, str(self.sensor_data.temperature)[:4] +';'+ str(self.sensor_data.humidity) + ";1")
        if self.sensor_data.volatile_compounds is not None:
            UpdateDevice(self.volatileUnit, self.sensor_data.volatile_compounds, str(self.sensor_data.volatile_compounds))
        if self.sensor_data.particles is not None:
            UpdateDevice(self.particlesUnit, self.sensor_data.particles, str(self.sensor_data.particles))
        if self.sensor_data.particles2_5 is not None:
            UpdateDevice(self.particles2_5Unit, self.sensor_data.particles2_5, str(self.sensor_data.particles2_5))
        if self.sensor_data.particles10 is not None:
            UpdateDevice(self.particles10Unit, self.sensor_data.particles10, str(self.sensor_data.particles10))
        if self.sensor_data.particulate_matter_25 is not None:
            UpdateDevice(self.particlesMatter25Unit, self.sensor_data.particulate_matter_25, str(self.sensor_data.particulate_matter_25))
        if self.sensor_data.particulate_matter_10 is not None:
            UpdateDevice(self.particlesMatter10Unit, self.sensor_data.particulate_matter_10, str(self.sensor_data.particulate_matter_10))
        if self.sensor_data.nitrogenDioxideDensity is not None:
            UpdateDevice(self.nitrogenDioxideDensityUnit, self.sensor_data.nitrogenDioxideDensity, str(self.sensor_data.nitrogenDioxideDensity))
        if self.sensor_data.heat_target is not None:
            UpdateDevice(self.heatTargetUnit, self.sensor_data.heat_target, str(self.sensor_data.heat_target))
        UpdateDevice(self.sleepTimeUnit, self.sensor_data.sleep_timer, str(self.sensor_data.sleep_timer))
        Domoticz.Debug("update SensorData: " + str(self.sensor_data))
        #Domoticz.Debug("update StateData: " + str(self.state_data))

    def onMQTTConnected(self):
        """connection to device established"""
        Domoticz.Debug("onMQTTConnected called")
        Domoticz.Log("MQTT connection established")
        self.mqttClient.Subscribe([self.base_topic + '/status/current', self.base_topic + '/status/connection', self.base_topic + '/status/faults']) #subscribe to all topics on the machine
        topic, payload = self.myDevice.request_state()
        self.mqttClient.Publish(topic, payload) #ask for update of current status

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")
        
    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT Publish: MQTT message incoming: " + topic + " " + str(message))

        if (topic == self.base_topic + '/status/current'):
            #update of the machine's status
            if StateData.is_state_data(message):
                Domoticz.Debug("machine state or state change recieved")
                self.state_data = StateData(message)
                self.updateDevices()
            if SensorsData.is_sensors_data(message):
                Domoticz.Debug("sensor state recieved")
                self.sensor_data = SensorsData(message)
                self.updateSensors()

        if (topic == self.base_topic + '/status/connection'):
            #connection status received
            Domoticz.Debug("connection state recieved")

        if (topic == self.base_topic + '/status/software'):
            #connection status received
            Domoticz.Debug("software state recieved")
            
        if (topic == self.base_topic + '/status/summary'):
            #connection status received
            Domoticz.Debug("summary state recieved")

    def _hashed_password(self, pwd):
        """Hash password (found in manual) to a base64 encoded of its sha512 value"""
        hash = hashlib.sha512()
        hash.update(pwd.encode('utf-8'))
        return base64.b64encode(hash.digest()).decode('utf-8')

def UpdateDevice(Unit, nValue, sValue, BatteryLevel=255, AlwaysUpdate=False):
    if Unit not in Devices: return
    if Devices[Unit].nValue != nValue\
        or Devices[Unit].sValue != sValue\
        or Devices[Unit].BatteryLevel != BatteryLevel\
        or AlwaysUpdate == True:

        Devices[Unit].Update(nValue, str(sValue), BatteryLevel=BatteryLevel)

        Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
            Devices[Unit].Name,
            nValue,
            sValue,
            BatteryLevel
        ))
        
global _plugin
_plugin = DysonPureLinkPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onDeviceRemoved(Unit):
    global _plugin
    _plugin.onDeviceRemoved(Unit)

    # Generic helper functions
def DumpConfigToLog():
    Domoticz.Debug("Parameter count: " + str(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "Parameter '" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
