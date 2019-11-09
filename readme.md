# Dyson Pure Link - Domoticz Python plugin
Domoticz plugin to integrate the Dyson PureLink devices

## Prerequisites

Requires Domoticz version V4.10548 or later (due to password hashing)
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
Set the following parameters: <br>
IP Adress: adres where your machine is connected to <br>
Port number: 1883 <br>
Dyson account password: the password used in the app <br>
Dyson account email adress: the adress used to create the account <br>
log level: use verbose preferably <br>

You can ommit the parameters: <br>
Dyson Password (see machine): <br>
Dyson Serial No.: <br>
Dyson type (Pure Cool only at this moment): <br>
See the Wiki page for more information

## Credits

based on info from the following sources:

- https://www.hackster.io/uladzislau-bayouski/merge-the-dyson-link-b763c3
- http://aakira.hatenablog.com/entry/2016/08/12/012654
