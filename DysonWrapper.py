#!/usr/bin/python

from __future__ import print_function
import argparse
import base64, json, hashlib, os, time

from dyson_pure_link_device import DysonPureLink
from value_types import FanMode, StandbyMonitoring


class DysonWrapper(object):
    def __init__(self):
        #nothing to do yet
        boolie = True
        self.config = None
        
        
    def getConnected(self, dyson_pure_link):
    """wrapper to get connection"""

        # Connect device and print result
        IAmConnected = dyson_pure_link.connect_device()
        #print('Connected: ', IAmConnected)
        if IAmConnected:
            # Get and print state and sensors data
            for entry in dyson_pure_link.get_data():
                print(entry)
        
        return IAmConnected

    def getDisConnected(self, dyson_pure_link, IAmConnected):
        if IAmConnected:
            # Disconnect device (IMPORTANT) and print result
            print('Disconnected: ', dyson_pure_link.disconnect_device())

    def getUpdate(self, dyson_pure_link, IAmConnected):
        if IAmConnected:
            # Get and print state and sensors data
            for entry in dyson_pure_link.get_data():
                print(entry)


    def setFan(self, dyson_pure_link, IAmConnected, argsFan):
        # Start new instance of Dyson Pure Link Device
        # self.config = self.parse_config()
        # dyson_pure_link = DysonPureLink(self.password, self.serial_number, self.device_type, self.ip_address, self.port_number)

        # Parse and print config file
        #print('Parsed config file: ', dyson_pure_link.parse_config())

        # Connect device and print result
        # IAmConnected = dyson_pure_link.connect_device()
        print('Connected: ', IAmConnected)
        if IAmConnected:
            print('Testing fan mode')
            dyson_pure_link.set_fan_mode(argsFan)
            for entry in dyson_pure_link.get_data():
                print(entry)

        # if IAmConnected:
            # # Disconnect device (IMPORTANT) and print result
            # print('Disconnected: ', dyson_pure_link.disconnect_device())

    def setStandby(self, dyson_pure_link, IAmConnected, argsStandby):
        # Start new instance of Dyson Pure Link Device

        print('Connected: ', IAmConnected)
        if IAmConnected:
            print('Testing standby mode')
            dyson_pure_link.set_standby_monitoring(argsStandby)
            for entry in dyson_pure_link.get_data():
                print(entry)

    def setSpeed(self, dyson_pure_link, IAmConnected, argsSpeed):
        # Start new instance of Dyson Pure Link Device

        print('Connected: ', IAmConnected)
        if IAmConnected:
            print('Testing standby mode')
            dyson_pure_link.set_fan_speed(argsSpeed)
            for entry in dyson_pure_link.get_data():
                print(entry)

        # if IAmConnected:
            # # Disconnect device (IMPORTANT) and print result
            # print('Disconnected: ', dyson_pure_link.disconnect_device())

    def parse_config(self):
        """Parses config file if any"""
        file_name = '{}/dyson_pure_link.yaml'.format(os.path.dirname(os.path.abspath(__file__)))
        #print("file name is " + file_name)

        if os.path.isfile(file_name):
            config = yaml.safe_load(open(file_name))
            #print("we read this config: " + str(config))

        return config
            
if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('-fan')
    args_parser.add_argument('-standby')
    args_parser.add_argument('-speed')
    args = args_parser.parse_args()
    
    myWrapper = DysonWrapper()
    dyson_pure_link = DysonPureLink(myWrapper.password, myWrapper.serial_number, myWrapper.device_type, myWrapper.ip_address, myWrapper.port_number)

    isItConnected = myWrapper.getConnected(dyson_pure_link)
    
    # Set Fan mode command
    if args.fan:
        myWrapper.setFan(dyson_pure_link, isItConnected, args.fan)

    # Set Standby monitoring command
    if args.standby:
        myWrapper.setStandby(dyson_pure_link, isItConnected, args.standby)

    # Set fan speed command
    if args.speed:
        myWrapper.setSpeed(dyson_pure_link, isItConnected, args.speed)
        
        
    myWrapper.getDisConnected(dyson_pure_link, isItConnected)
