# Dyson Pure Link - Domoticz Python plugin
Domoticz plugin to integrate the Dyson PureLink devices

## Prerequisites

Requires Domoticz version V4.10548 or later (due to password hashing). Follow the Domoticz guide on [Using Python Plugins](https://www.domoticz.com/wiki/Using_Python_plugins) to enable the plugin framework.

The following Python modules installed
```
sudo apt-get update
sudo apt-get install python3-requests
sudo pip3 install crypto
```

## Installation

1. Clone repository into your domoticz plugins folder
```
cd domoticz/plugins
git clone https://github.com/JanJaapKo/DysonPureLink
```
to update:
```
cd domoticz/plugins/DysonPureLink
git pull https://github.com/JanJaapKo/DysonPureLink
```
2. Restart domoticz
3. Go to "Hardware" page and add new item with type "DysonPureLink"
4. Set your MQTT server address and port to plugin settings

## Configuration
At first setup, the plugin needs to connect to the Dyson cloud provider to get the credentials to acces the machine. Since early 2021 a 2-factor authentication is needed, which leads to a 2 step setup according the steps below.
1. fill in the following parameters:<br>
a. ```machine IP adress```<br>
b. ```Port number (normally 1883)```<br>
c. ```Cloud account email adress```<br>
d. ```Cloud account password```<br>
 
2. As a result an email with a verification code (aka OTP code) will be sent to the mail adress specified at c.<br>
e. fill in the verification code in ```email verification code```<br>
f. specify the machine's name (as you did when registering the machine) if you have more than 1 Dyson device in ```Machine name (cloud account)```<br>

See the [Wiki](https://github.com/JanJaapKo/DysonPureLink/wiki) page for extended configuration information.

## Known issues/limitation
- Due to the connection (ip adress) only 1 machine can be connected to 1 instance of the plugin. When you own more than 1 device, create a plugin instance per machine and use the name filtering to select the device.
- Dyson is regularly updating its cloud API leading to the following error on restart of the plugin/Domoticz: ``` Login to Dyson account failed: '401, Unauthorized' ```. According to [etheralm/issue37](https://github.com/etheralm/libpurecool/issues/37) the solution for now (March 2021) is to log in with the Dyson mobile app first

## Credits

based on info from the following sources:

- https://github.com/shenxn/libdyson
- https://www.hackster.io/uladzislau-bayouski/merge-the-dyson-link-b763c3
- http://aakira.hatenablog.com/entry/2016/08/12/012654
- https://github.com/CharlesBlonde/libpurecoollink
- https://github.com/etheralm/libpurecool
