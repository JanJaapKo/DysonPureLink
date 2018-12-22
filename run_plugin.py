#!/usr/bin/python

import Domoticz
import base64, os

from dyson_pure_link_device import DysonPureLinkDevice
from value_types import FanMode, StandbyMonitoring


class DysonWrapper(object):
    def __init__(self, password, serialNumber, deviceType, ipAdress, portNum):
        #nothing to do yet
        boolie = True
        #self.config = None
        self.password = password
        self.serial_number = serialNumber
        self.device_type = deviceType
        self.ip_address = ipAdress
        self.port_number = int(portNum)
        self.dyson_pure_link = DysonPureLinkDevice(self.password, self.serial_number, self.device_type, self.ip_address, self.port_number)
        
    def getConnected(self):
        # Start new instance of Dyson Pure Link Device

        # Connect device and print result
        Domoticz.Debug("DysonWrapper: getConnected called")

        IAmConnected = self.dyson_pure_link.connect_device()
        Domoticz.Debug('Connected: ' + str(IAmConnected))
        if IAmConnected:
            # Get and print state and sensors data
            for entry in self.dyson_pure_link.get_data():
                Domoticz.Debug(str(entry))
        
        return IAmConnected

    def getDisConnected(self, IAmConnected):
        Domoticz.Debug("DysonWrapper: getDisConnected called")
        if IAmConnected:
            # Disconnect device (IMPORTANT) and print result
            connected = self.dyson_pure_link.disconnect_device()
            Domoticz.Debug('Disconnected: ' + str(connected))
            return connected

    def getUpdate(self, IAmConnected):
        Domoticz.Debug("DysonWrapper: getUpdate called")
        if IAmConnected:
            # Get and print state and sensors data
            (stateData, sensorData) = self.dyson_pure_link.get_data()
            # for entry in (sensorData,stateData):
            #Domoticz.Debug("DysonWrapper: getUpdate, stateData: "+str(stateData))
                
            return (stateData, sensorData)

    def setFan(self, IAmConnected, argsFan):
        # Start new instance of Dyson Pure Link Device

        # Connect device and print result
        # IAmConnected = dyson_pure_link.connect_device()
        Domoticz.Debug("DysonWrapper: setFan called")
        Domoticz.Debug('Connected: ' + str(IAmConnected))
        if IAmConnected:
            Domoticz.Debug('Testing fan mode')
            self.dyson_pure_link.set_fan_mode(argsFan)
            for entry in self.dyson_pure_link.get_data():
                Domoticz.Debug(str(entry))

    def setStandby(self, IAmConnected, argsStandby):
        # Start new instance of Dyson Pure Link Device

        Domoticz.Debug("DysonWrapper: setStandby called")
        Domoticz.Debug('Connected: ' + str(IAmConnected))
        if IAmConnected:
            Domoticz.Debug('Testing standby mode')
            self.dyson_pure_link.set_standby_monitoring(argsStandby)
            for entry in self.dyson_pure_link.get_data():
                Domoticz.Debug(str(entry))
    def setNightMode(self, IAmConnected, argsNight):
        # Start new instance of Dyson Pure Link Device

        print('Connected: ', IAmConnected)
        if IAmConnected:
            print('Testing night mode')
            self.dyson_pure_link.set_night_mode(argsNight)
            for entry in self.dyson_pure_link.get_data():
                print(entry)

    def setSpeed(self, IAmConnected, argsSpeed):
        # Start new instance of Dyson Pure Link Device

        Domoticz.Debug('Connected: ' + str(IAmConnected))
        if IAmConnected:
            Domoticz.Debug('Testing setSpeed, argument: ' + argsSpeed)
            self.dyson_pure_link.set_fan_speed(argsSpeed)
            for entry in self.dyson_pure_link.get_data():
                Domoticz.Debug(str(entry))

    def setOscilation(self, IAmConnected, argsOsc):
        # Start new instance of Dyson Pure Link Device

        print('Connected: ', IAmConnected)
        if IAmConnected:
            print('Testing oscilation mode')
            self.dyson_pure_link.set_oscilation(argsOsc)
            for entry in self.dyson_pure_link.get_data():
                print(entry)
           
# if __name__ == '__main__':
    # args_parser = argparse.ArgumentParser()
    # args_parser.add_argument('-fan')
    # args_parser.add_argument('-standby')
    # args_parser.add_argument('-speed')
    # args = args_parser.parse_args()

    # myWrapper = DysonWrapper('ltojcjwq','NN2-EU-JEA3830A','475','192.168.1.15', '1883')
    # dyson_pure_link = DysonPureLinkDevice(myWrapper.password, myWrapper.serial_number, myWrapper.device_type, myWrapper.ip_address, myWrapper.port_number)

    # isItConnected = myWrapper.getConnected(dyson_pure_link)
    
    # # Set Fan mode command
    # if args.fan:
        # myWrapper.setFan(dyson_pure_link, isItConnected, args.fan)

    # # Set Standby monitoring command
    # if args.standby:
        # myWrapper.setStandby(dyson_pure_link, isItConnected, args.standby)

    # # Set fan speed command
    # if args.speed:
        # myWrapper.setSpeed(dyson_pure_link, isItConnected, args.speed)
        
        
    # myWrapper.getDisConnected(dyson_pure_link, isItConnected)
