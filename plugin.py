# Basic Python Plugin Example
#
# Author: Jan-Jaap Kostelijk
#
"""
<plugin key="DysonPureLink" name="Dyson Pure Link" author="Jan-Jaap Kostelijk" version="1.0.0" >
    <description>
        <h2>Dyson Pure Link plugin</h2><br/>
        Connects to Dyson Pure Link device, CoolLink 475<br/>
        reads states and sensors for now<br/>
		Has been tested with type 475, assumed the others work too.
    </description>
    <params>
		<param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.15"/>
		<param field="Port" label="Port" width="30px" required="true" default="1883"/>
		<param field="Mode1" label="Dyson type (Pure Cool only at this moment)">
            <options>
                <option label="455" value="455"/>
                <option label="465" value="465"/>
                <option label="475" value="475" default="true"/>
            </options>
        </param>
		<param field="Username" label="Dyson Serial No." default="NN2-EU-JEA3830A" required="true"/>
		<param field="Password" label="Dyson Password (see machine)" required="true" password="true"/>
        <param field="Mode3" label="MQTT Client ID (optional)" width="300px" required="false" default=""/>
		<param field="Mode5" label="Update count (10 sec)" default="3" required="true"/>
		<param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import time
#import base64, hashlib, os
from mqtt import MqttClient

from value_types import CONNECTION_STATE, DISCONNECTION_STATE, FanMode, StandbyMonitoring, ConnectionError, DisconnectionError, SensorsData, StateData

class DysonPureLink:
    #define class variables
    enabled = False
    IThinkIAmConnected = False
    #myWrapper = None
    mqttClient = None
    #unit numbers for devices to create
    #for Pure Cool models
    fanModeUnit = 1
    fanStateUnit = 12
    nightModeUnit = 2
    fanSpeedUnit = 3
    fanOscillationUnit = 4
    standbyMonitoringUnit = 5
    filterLifeUnit = 6
    qualityTargetUnit = 7
    tempHumUnit = 8
    volatileUnit = 9
    particlesUnit = 10
    sleepTimeUnit = 11
    runCounter = 0

    def __init__(self):
        self.password = None
        self.serial_number = None
        self.device_type = None
        self.ip_address = None
        self.port_number = None
        self.sensor_data = None
        self.state_data = None
        self.mqttClient = None

    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters['Mode4'] == 'Debug':
            Domoticz.Debugging(1)
            DumpConfigToLog()
        
        #PureLink needs polling, get from config
        self.runCounter = int(Parameters["Mode5"])
        Domoticz.Heartbeat(10)
        
        #check, per device, if it is created. If not,create it
        Options = {"LevelActions" : "|||",
                   "LevelNames" : "|OFF|ON|AUTO",
                   "LevelOffHidden" : "true",
                   "SelectorStyle" : "1"}
        if self.fanModeUnit not in Devices:
            Domoticz.Device(Name='Fan mode', Unit=self.fanModeUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()
        Options = {"LevelActions" : "||",
                   "LevelNames" : "|OFF|ON",
                   "LevelOffHidden" : "true",
                   "SelectorStyle" : "1"}
        if self.fanStateUnit not in Devices:
            Domoticz.Device(Name='Fan state', Unit=self.fanStateUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()
        if self.nightModeUnit not in Devices:
            Domoticz.Device(Name='Night mode', Unit=self.nightModeUnit, Type=244, Subtype=62,  Switchtype=0, Image=9).Create()
            
        Options = {"LevelActions" : "|||||||||||",
                   "LevelNames" : "|1|2|3|4|5|6|7|8|9|10|Auto",
                   "LevelOffHidden" : "false",
                   "SelectorStyle" : "1"}
        if self.fanSpeedUnit not in Devices:
            Domoticz.Device(Name='Fan speed', Unit=self.fanSpeedUnit, TypeName="Selector Switch", Image=7, Options=Options).Create()

        if self.fanOscillationUnit not in Devices:
            Domoticz.Device(Name='Oscilation mode', Unit=self.fanOscillationUnit, Type=244, Subtype=62, Image=7, Switchtype=0).Create()
        if self.standbyMonitoringUnit not in Devices:
            Domoticz.Device(Name='Standby monitor', Unit=self.standbyMonitoringUnit, Type=244, Subtype=62,Image=7, Switchtype=0).Create()
        if self.filterLifeUnit not in Devices:
            Domoticz.Device(Name='Remaining filter life', Unit=self.filterLifeUnit, TypeName="Custom").Create()
        if self.qualityTargetUnit not in Devices:
            Domoticz.Device(Name='Air quality setpoint', Unit=self.qualityTargetUnit, TypeName="Custom").Create()
        if self.tempHumUnit not in Devices:
            Domoticz.Device(Name='Temperature and Humidity', Unit=self.tempHumUnit, TypeName="Temp+Hum").Create()
        if self.volatileUnit not in Devices:
            Domoticz.Device(Name='Volatile organic', Unit=self.volatileUnit, TypeName="Air Quality").Create()
        if self.particlesUnit not in Devices:
            Domoticz.Device(Name='Dust', Unit=self.particlesUnit, TypeName="Air Quality").Create()

        #read out parameters
        self.ip_address = Parameters["Address"].replace(" ", "")
        self.port_number = int(Parameters["Port"].replace(" ", ""))
        self.serial_number = Parameters['Username']
        self.device_type = Parameters['Mode1']
        self.password = Parameters['Password']
        self.base_topic = "{0}/{1}/command".format(self.device_type, self.serial_number)
        mqtt_client_id = Parameters["Mode3"].strip()


        #create the connection
        self.mqttClient = MqttClient(self.ip_address, self.port_number, mqtt_client_id, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)
        
        # Connect device and print result
        #Domoticz.Log('Connected: ' + str(self.connect_device()))
        self.IThinkIAmConnected = False
        #self.IThinkIAmConnected = self.myWrapper.getConnected()
        #Domoticz.Log('onStart: Connected: ' + str(self.IThinkIAmConnected))
        
        #(self.state_data, self.sensor_data) = self.myWrapper.getUpdate(self.IThinkIAmConnected)
        #Domoticz.Debug("onStart: " + str(self.state_data))
        #Domoticz.Debug("onStart: " + str(self.sensor_data))
        
        #self.updateAllDevices()
        
        
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("DysonPureLink plugin: onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Unit == self.fanSpeedUnit and Level<=100:
            arg="0000"+str(Level//10)
            #self.myWrapper.setSpeed(self.IThinkIAmConnected,arg[-4:]) #use last 4 characters as speed level or AUTO
        if Unit == self.fanModeUnit or (Unit == self.fanSpeedUnit and Level>100):
            if Level == 10: arg="OFF"
            if Level == 20: arg="ON"
            if Level >=30: arg="AUTO"
            #self.myWrapper.setFan(self.IThinkIAmConnected,arg) 

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("DysonPureLink plugin: onNotification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onHeartbeat(self):
        self.mqttClient.onHeartbeat()

    def onDeviceRemoved(self):
        Domoticz.Log("DysonPureLink plugin: onDeviceRemoved called")
    
    def updateAllDevices(self):
        """Update the defined devices from incoming mesage info"""
        #update the devices
        pass
        # tempNum = int(self.sensor_data.temperature)
        # humNum = int(self.sensor_data.humidity)
        # UpdateDevice(self.fanOscillationUnit, self.state_data.oscillation.state, str(self.state_data.oscillation))
        # UpdateDevice(self.nightModeUnit, self.state_data.night_mode.state, str(self.state_data.night_mode))
        # UpdateDevice(self.tempHumUnit, 1, str(self.sensor_data.temperature)[:4] +';'+ str(self.sensor_data.humidity) + ";1")
        # UpdateDevice(self.volatileUnit, self.sensor_data.volatile_compounds, str(self.sensor_data.volatile_compounds))
        # UpdateDevice(self.particlesUnit, self.sensor_data.particles, str(self.sensor_data.particles))

        # # Fan speed  
        # f_rate = self.state_data.fan_speed
        # if (f_rate == "AUTO"):
            # sValueNew = "110" # Auto
        # else:
            # sValueNew = str(int(f_rate) * 10)

        # UpdateDevice(self.fanSpeedUnit, 1, sValueNew)
        # UpdateDevice(self.fanModeUnit, self.state_data.fan_mode.state, str((self.state_data.fan_mode.state+1)*10))
        # UpdateDevice(self.fanStateUnit, self.state_data.fan_state.state, str((self.state_data.fan_state.state+1)*10))
        # UpdateDevice(self.filterLifeUnit, self.state_data.filter_life, str(self.state_data.filter_life))
            

    def onMQTTConnected(self):
        self.mqttClient.Subscribe([self.base_topic + '/#'])

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, message):
        Domoticz.Debug("MQTT Publish 1: MQTT message: " + topic + " " + str(message))

        if (topic == self.base_topic + '/bridge/state'):
            if message == 'online':
                self.mqttClient.Publish(self.base_topic + '/bridge/config/devices', '')

            Domoticz.Log('Zigbee2mqtt bridge is ' + message)
            return

        if (topic == self.base_topic + '/bridge/log'):
            if message['type'] == 'devices':
                Domoticz.Log('Received available devices list from bridge')


# def UpdateDevice(Unit, nValue, sValue, BatteryLevel=255, AlwaysUpdate=False):
    # if Unit not in Devices: return
    # if Devices[Unit].nValue != nValue\
        # or Devices[Unit].sValue != sValue\
        # or Devices[Unit].BatteryLevel != BatteryLevel\
        # or AlwaysUpdate == True:

        # Devices[Unit].Update(nValue, str(sValue), BatteryLevel=BatteryLevel)

        # Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
            # Devices[Unit].Name,
            # nValue,
            # sValue,
            # BatteryLevel
        # ))

        
global _plugin
_plugin = DysonPureLink()

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

def onDeviceRemoved():
    global _plugin
    _plugin.onDeviceRemoved()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return