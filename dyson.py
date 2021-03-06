"""Dyson Pure Cool Link library."""

import Domoticz
import requests
from dyson_device import DysonDevice
from requests.auth import HTTPBasicAuth

DYSON_API_URL = "appapi.cp.dyson.com"
DYSON_API_URL_CN = "appapi.cp.dyson.cn"
DYSON_API_USER_AGENT = "DysonLink/29019 CFNetwork/1188 Darwin/20.0.0"
DYSON_API_USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.1.0; Google Build/OPM6.171019.030.E1)"

class DysonAccount:
    """Dyson account."""

    def __init__(self, email, password, country):
        """Create a new Dyson account.

        :param email: User email
        :param password: User password
        :param country: 2 characters language code
        """
        self._email = email
        self._password = password
        self._country = country
        self._logged = False
        self._auth = None
        self._credentials = None
        self._headers = {'User-Agent': DYSON_API_USER_AGENT}
        if country == "CN":
            self._dyson_api_url = DYSON_API_URL_CN
        else:
            self._dyson_api_url = DYSON_API_URL

    def login(self):
        """Login to dyson web services."""
        # Must first check account status
        uri = "https://{0}/v3/userregistration/userstatus".format(self._dyson_api_url)
        uri = "https://{0}/v3/userregistration/email/userstatus".format(self._dyson_api_url)
        #params={"country": self._country, "email": self._email},
        Domoticz.Debug("Request URL: '" + uri + "'")
        accountstatus = requests.get(
            uri,
            params={"country": self._country},
            data={"email": self._email},
            headers=self._headers,
            verify=False
        )
        Domoticz.Debug("Request text: '" + accountstatus.text + "'")

        if accountstatus.status_code == requests.codes.ok:
            json_status = accountstatus.json()
            if json_status['accountStatus'] != "ACTIVE":
                # The account is not active
                Domoticz.Error("Login to Dyson account failed: not active")
                self._logged = False
                return self._logged
            else:
                Domoticz.Debug("Account is active, authenticationMethod:  '" + json_status['authenticationMethod'] + "'")
        else:
            Domoticz.Error("Login to Dyson account/userStatus failed: '" +str(accountstatus.status_code)+", " +str(accountstatus.reason)+"'")
            self._logged = False
            return self._logged

        request_body = {
            "Email": self._email,
            "Password": self._password
        }
        
        uri = "https://{0}/v1/userregistration/authenticate?country={1}".format(self._dyson_api_url, self._country)
        Domoticz.Debug("Request URL: '" + uri + "'")
        login = requests.post(
            uri,
            headers=self._headers,
            json=request_body,
            verify=False
        )
        
        if login.status_code == requests.codes.ok:
            json_response = login.json()
            Domoticz.Debug("Login OK, JSON response: '"+str(json_response)+"'")
            self._credentials = json_response
            self._auth = HTTPBasicAuth(json_response["Account"], json_response["Password"])
            self._logged = True
        else:
            self._logged = False
            Domoticz.Error("Login to Dyson account/authenticate failed: '" +str(login.status_code)+", " +str(login.reason)+"'")
            Domoticz.Debug("Login to Dyson account/authenticate failed, returned info: " + str(login.json()))
        return self._logged

    def devices(self, credentials):
        """Return all devices linked to the account."""
        if self._logged:
            Domoticz.Debug("Fetching devices from Dyson Web Services.")
            #Dyson seems to maintain 2 versions of the interface, request devices from both.
            device_v1_response = requests.get(
                "https://{0}/v1/provisioningservice/manifest".format(
                    self._dyson_api_url),
                headers=self._headers,
                verify=False,
                #auth=author)
                auth=self._auth)
            Domoticz.Debug("Reply from Dyson's v1 api: "+str(device_v1_response.json())+"'")
            device_v2_response = requests.get(
                "https://{0}/v2/provisioningservice/manifest".format(
                    self._dyson_api_url),
                headers=self._headers,
                verify=False,
                #auth=author)
                auth=self._auth)
            Domoticz.Debug("Reply from Dyson's v2 api: "+str(device_v2_response.json())+"'")
            devices_dict = {} #using a dictionary to overwright double entries
            for device in device_v1_response.json():
                Domoticz.Debug("Device returned from Dyson v1 api: "+str(device)+"'")
                dyson_device = DysonDevice(device)
                devices_dict[dyson_device.name] = dyson_device
            for device in device_v2_response.json():
                Domoticz.Debug("Device returned from Dyson v2 api: "+str(device)+"'")
                dyson_device = DysonDevice(device)
                devices_dict[dyson_device.name] = dyson_device
            return devices_dict
        else:
            Domoticz.Log("Not logged to Dyson Web Services.")
            #raise DysonNotLoggedException()

    @property
    def logged(self):
        """Return True if user is logged, else False."""
        return self._logged

    @property
    def credentials(self):
        """Return device credentials as JSON string"""
        return self._credentials

    @property
    def authentication(self):
        """Return authentication object"""
        return self._auth
