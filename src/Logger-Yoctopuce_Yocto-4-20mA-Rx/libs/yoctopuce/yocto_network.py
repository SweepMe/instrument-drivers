# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_network.py 39573 2020-03-10 17:20:22Z seb $
#
#  Implements yFindNetwork(), the high-level API for Network functions
#
#  - - - - - - - - - License information: - - - - - - - - -
#
#  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#
#  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#  non-exclusive license to use, modify, copy and integrate this
#  file into your software for the sole purpose of interfacing
#  with Yoctopuce products.
#
#  You may reproduce and distribute copies of this file in
#  source or object form, as long as the sole purpose of this
#  code is to interface with Yoctopuce products. You must retain
#  this notice in the distributed source file.
#
#  You should refer to Yoctopuce General Terms and Conditions
#  for additional information regarding your rights and
#  obligations.
#
#  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#  WARRANTY, OR OTHERWISE.
#
# *********************************************************************


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (YNetwork class start)
#noinspection PyProtectedMember
class YNetwork(YFunction):
    """
    YNetwork objects provide access to TCP/IP parameters of Yoctopuce
    devices that include a built-in network interface.

    """
    #--- (end of YNetwork class start)
    #--- (YNetwork return codes)
    #--- (end of YNetwork return codes)
    #--- (YNetwork dlldef)
    #--- (end of YNetwork dlldef)
    #--- (YNetwork yapiwrapper)
    #--- (end of YNetwork yapiwrapper)
    #--- (YNetwork definitions)
    MACADDRESS_INVALID = YAPI.INVALID_STRING
    IPADDRESS_INVALID = YAPI.INVALID_STRING
    SUBNETMASK_INVALID = YAPI.INVALID_STRING
    ROUTER_INVALID = YAPI.INVALID_STRING
    IPCONFIG_INVALID = YAPI.INVALID_STRING
    PRIMARYDNS_INVALID = YAPI.INVALID_STRING
    SECONDARYDNS_INVALID = YAPI.INVALID_STRING
    NTPSERVER_INVALID = YAPI.INVALID_STRING
    USERPASSWORD_INVALID = YAPI.INVALID_STRING
    ADMINPASSWORD_INVALID = YAPI.INVALID_STRING
    HTTPPORT_INVALID = YAPI.INVALID_UINT
    DEFAULTPAGE_INVALID = YAPI.INVALID_STRING
    WWWWATCHDOGDELAY_INVALID = YAPI.INVALID_UINT
    CALLBACKURL_INVALID = YAPI.INVALID_STRING
    CALLBACKCREDENTIALS_INVALID = YAPI.INVALID_STRING
    CALLBACKINITIALDELAY_INVALID = YAPI.INVALID_UINT
    CALLBACKSCHEDULE_INVALID = YAPI.INVALID_STRING
    CALLBACKMINDELAY_INVALID = YAPI.INVALID_UINT
    CALLBACKMAXDELAY_INVALID = YAPI.INVALID_UINT
    POECURRENT_INVALID = YAPI.INVALID_UINT
    READINESS_DOWN = 0
    READINESS_EXISTS = 1
    READINESS_LINKED = 2
    READINESS_LAN_OK = 3
    READINESS_WWW_OK = 4
    READINESS_INVALID = -1
    DISCOVERABLE_FALSE = 0
    DISCOVERABLE_TRUE = 1
    DISCOVERABLE_INVALID = -1
    CALLBACKMETHOD_POST = 0
    CALLBACKMETHOD_GET = 1
    CALLBACKMETHOD_PUT = 2
    CALLBACKMETHOD_INVALID = -1
    CALLBACKENCODING_FORM = 0
    CALLBACKENCODING_JSON = 1
    CALLBACKENCODING_JSON_ARRAY = 2
    CALLBACKENCODING_CSV = 3
    CALLBACKENCODING_YOCTO_API = 4
    CALLBACKENCODING_JSON_NUM = 5
    CALLBACKENCODING_EMONCMS = 6
    CALLBACKENCODING_AZURE = 7
    CALLBACKENCODING_INFLUXDB = 8
    CALLBACKENCODING_MQTT = 9
    CALLBACKENCODING_YOCTO_API_JZON = 10
    CALLBACKENCODING_PRTG = 11
    CALLBACKENCODING_INFLUXDB_V2 = 12
    CALLBACKENCODING_INVALID = -1
    #--- (end of YNetwork definitions)

    def __init__(self, func):
        super(YNetwork, self).__init__(func)
        self._className = 'Network'
        #--- (YNetwork attributes)
        self._callback = None
        self._readiness = YNetwork.READINESS_INVALID
        self._macAddress = YNetwork.MACADDRESS_INVALID
        self._ipAddress = YNetwork.IPADDRESS_INVALID
        self._subnetMask = YNetwork.SUBNETMASK_INVALID
        self._router = YNetwork.ROUTER_INVALID
        self._ipConfig = YNetwork.IPCONFIG_INVALID
        self._primaryDNS = YNetwork.PRIMARYDNS_INVALID
        self._secondaryDNS = YNetwork.SECONDARYDNS_INVALID
        self._ntpServer = YNetwork.NTPSERVER_INVALID
        self._userPassword = YNetwork.USERPASSWORD_INVALID
        self._adminPassword = YNetwork.ADMINPASSWORD_INVALID
        self._httpPort = YNetwork.HTTPPORT_INVALID
        self._defaultPage = YNetwork.DEFAULTPAGE_INVALID
        self._discoverable = YNetwork.DISCOVERABLE_INVALID
        self._wwwWatchdogDelay = YNetwork.WWWWATCHDOGDELAY_INVALID
        self._callbackUrl = YNetwork.CALLBACKURL_INVALID
        self._callbackMethod = YNetwork.CALLBACKMETHOD_INVALID
        self._callbackEncoding = YNetwork.CALLBACKENCODING_INVALID
        self._callbackCredentials = YNetwork.CALLBACKCREDENTIALS_INVALID
        self._callbackInitialDelay = YNetwork.CALLBACKINITIALDELAY_INVALID
        self._callbackSchedule = YNetwork.CALLBACKSCHEDULE_INVALID
        self._callbackMinDelay = YNetwork.CALLBACKMINDELAY_INVALID
        self._callbackMaxDelay = YNetwork.CALLBACKMAXDELAY_INVALID
        self._poeCurrent = YNetwork.POECURRENT_INVALID
        #--- (end of YNetwork attributes)

    #--- (YNetwork implementation)
    def _parseAttr(self, json_val):
        if json_val.has("readiness"):
            self._readiness = json_val.getInt("readiness")
        if json_val.has("macAddress"):
            self._macAddress = json_val.getString("macAddress")
        if json_val.has("ipAddress"):
            self._ipAddress = json_val.getString("ipAddress")
        if json_val.has("subnetMask"):
            self._subnetMask = json_val.getString("subnetMask")
        if json_val.has("router"):
            self._router = json_val.getString("router")
        if json_val.has("ipConfig"):
            self._ipConfig = json_val.getString("ipConfig")
        if json_val.has("primaryDNS"):
            self._primaryDNS = json_val.getString("primaryDNS")
        if json_val.has("secondaryDNS"):
            self._secondaryDNS = json_val.getString("secondaryDNS")
        if json_val.has("ntpServer"):
            self._ntpServer = json_val.getString("ntpServer")
        if json_val.has("userPassword"):
            self._userPassword = json_val.getString("userPassword")
        if json_val.has("adminPassword"):
            self._adminPassword = json_val.getString("adminPassword")
        if json_val.has("httpPort"):
            self._httpPort = json_val.getInt("httpPort")
        if json_val.has("defaultPage"):
            self._defaultPage = json_val.getString("defaultPage")
        if json_val.has("discoverable"):
            self._discoverable = (json_val.getInt("discoverable") > 0 if 1 else 0)
        if json_val.has("wwwWatchdogDelay"):
            self._wwwWatchdogDelay = json_val.getInt("wwwWatchdogDelay")
        if json_val.has("callbackUrl"):
            self._callbackUrl = json_val.getString("callbackUrl")
        if json_val.has("callbackMethod"):
            self._callbackMethod = json_val.getInt("callbackMethod")
        if json_val.has("callbackEncoding"):
            self._callbackEncoding = json_val.getInt("callbackEncoding")
        if json_val.has("callbackCredentials"):
            self._callbackCredentials = json_val.getString("callbackCredentials")
        if json_val.has("callbackInitialDelay"):
            self._callbackInitialDelay = json_val.getInt("callbackInitialDelay")
        if json_val.has("callbackSchedule"):
            self._callbackSchedule = json_val.getString("callbackSchedule")
        if json_val.has("callbackMinDelay"):
            self._callbackMinDelay = json_val.getInt("callbackMinDelay")
        if json_val.has("callbackMaxDelay"):
            self._callbackMaxDelay = json_val.getInt("callbackMaxDelay")
        if json_val.has("poeCurrent"):
            self._poeCurrent = json_val.getInt("poeCurrent")
        super(YNetwork, self)._parseAttr(json_val)

    def get_readiness(self):
        """
        Returns the current established working mode of the network interface.
        Level zero (DOWN_0) means that no hardware link has been detected. Either there is no signal
        on the network cable, or the selected wireless access point cannot be detected.
        Level 1 (LIVE_1) is reached when the network is detected, but is not yet connected.
        For a wireless network, this shows that the requested SSID is present.
        Level 2 (LINK_2) is reached when the hardware connection is established.
        For a wired network connection, level 2 means that the cable is attached at both ends.
        For a connection to a wireless access point, it shows that the security parameters
        are properly configured. For an ad-hoc wireless connection, it means that there is
        at least one other device connected on the ad-hoc network.
        Level 3 (DHCP_3) is reached when an IP address has been obtained using DHCP.
        Level 4 (DNS_4) is reached when the DNS server is reachable on the network.
        Level 5 (WWW_5) is reached when global connectivity is demonstrated by properly loading the
        current time from an NTP server.

        @return a value among YNetwork.READINESS_DOWN, YNetwork.READINESS_EXISTS,
        YNetwork.READINESS_LINKED, YNetwork.READINESS_LAN_OK and YNetwork.READINESS_WWW_OK corresponding to
        the current established working mode of the network interface

        On failure, throws an exception or returns YNetwork.READINESS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.READINESS_INVALID
        res = self._readiness
        return res

    def get_macAddress(self):
        """
        Returns the MAC address of the network interface. The MAC address is also available on a sticker
        on the module, in both numeric and barcode forms.

        @return a string corresponding to the MAC address of the network interface

        On failure, throws an exception or returns YNetwork.MACADDRESS_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.MACADDRESS_INVALID
        res = self._macAddress
        return res

    def get_ipAddress(self):
        """
        Returns the IP address currently in use by the device. The address may have been configured
        statically, or provided by a DHCP server.

        @return a string corresponding to the IP address currently in use by the device

        On failure, throws an exception or returns YNetwork.IPADDRESS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.IPADDRESS_INVALID
        res = self._ipAddress
        return res

    def get_subnetMask(self):
        """
        Returns the subnet mask currently used by the device.

        @return a string corresponding to the subnet mask currently used by the device

        On failure, throws an exception or returns YNetwork.SUBNETMASK_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.SUBNETMASK_INVALID
        res = self._subnetMask
        return res

    def get_router(self):
        """
        Returns the IP address of the router on the device subnet (default gateway).

        @return a string corresponding to the IP address of the router on the device subnet (default gateway)

        On failure, throws an exception or returns YNetwork.ROUTER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.ROUTER_INVALID
        res = self._router
        return res

    def get_ipConfig(self):
        """
        Returns the IP configuration of the network interface.

        If the network interface is setup to use a static IP address, the string starts with "STATIC:" and
        is followed by three
        parameters, separated by "/". The first is the device IP address, followed by the subnet mask
        length, and finally the
        router IP address (default gateway). For instance: "STATIC:192.168.1.14/16/192.168.1.1"

        If the network interface is configured to receive its IP from a DHCP server, the string start with
        "DHCP:" and is followed by
        three parameters separated by "/". The first is the fallback IP address, then the fallback subnet
        mask length and finally the
        fallback router IP address. These three parameters are used when no DHCP reply is received.

        @return a string corresponding to the IP configuration of the network interface

        On failure, throws an exception or returns YNetwork.IPCONFIG_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.IPCONFIG_INVALID
        res = self._ipConfig
        return res

    def set_ipConfig(self, newval):
        rest_val = newval
        return self._setAttr("ipConfig", rest_val)

    def get_primaryDNS(self):
        """
        Returns the IP address of the primary name server to be used by the module.

        @return a string corresponding to the IP address of the primary name server to be used by the module

        On failure, throws an exception or returns YNetwork.PRIMARYDNS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.PRIMARYDNS_INVALID
        res = self._primaryDNS
        return res

    def set_primaryDNS(self, newval):
        """
        Changes the IP address of the primary name server to be used by the module.
        When using DHCP, if a value is specified, it overrides the value received from the DHCP server.
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param newval : a string corresponding to the IP address of the primary name server to be used by the module

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("primaryDNS", rest_val)

    def get_secondaryDNS(self):
        """
        Returns the IP address of the secondary name server to be used by the module.

        @return a string corresponding to the IP address of the secondary name server to be used by the module

        On failure, throws an exception or returns YNetwork.SECONDARYDNS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.SECONDARYDNS_INVALID
        res = self._secondaryDNS
        return res

    def set_secondaryDNS(self, newval):
        """
        Changes the IP address of the secondary name server to be used by the module.
        When using DHCP, if a value is specified, it overrides the value received from the DHCP server.
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param newval : a string corresponding to the IP address of the secondary name server to be used by the module

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("secondaryDNS", rest_val)

    def get_ntpServer(self):
        """
        Returns the IP address of the NTP server to be used by the device.

        @return a string corresponding to the IP address of the NTP server to be used by the device

        On failure, throws an exception or returns YNetwork.NTPSERVER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.NTPSERVER_INVALID
        res = self._ntpServer
        return res

    def set_ntpServer(self, newval):
        """
        Changes the IP address of the NTP server to be used by the module. Use an empty
        string to restore the factory set  address.
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param newval : a string corresponding to the IP address of the NTP server to be used by the module

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("ntpServer", rest_val)

    def get_userPassword(self):
        """
        Returns a hash string if a password has been set for "user" user,
        or an empty string otherwise.

        @return a string corresponding to a hash string if a password has been set for "user" user,
                or an empty string otherwise

        On failure, throws an exception or returns YNetwork.USERPASSWORD_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.USERPASSWORD_INVALID
        res = self._userPassword
        return res

    def set_userPassword(self, newval):
        """
        Changes the password for the "user" user. This password becomes instantly required
        to perform any use of the module. If the specified value is an
        empty string, a password is not required anymore.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the password for the "user" user

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if len(newval) > YAPI.HASH_BUF_SIZE:
            self._throw(YAPI.INVALID_ARGUMENT, "Password too long :" + newval)
            return YAPI.INVALID_ARGUMENT
        rest_val = newval
        return self._setAttr("userPassword", rest_val)

    def get_adminPassword(self):
        """
        Returns a hash string if a password has been set for user "admin",
        or an empty string otherwise.

        @return a string corresponding to a hash string if a password has been set for user "admin",
                or an empty string otherwise

        On failure, throws an exception or returns YNetwork.ADMINPASSWORD_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.ADMINPASSWORD_INVALID
        res = self._adminPassword
        return res

    def set_adminPassword(self, newval):
        """
        Changes the password for the "admin" user. This password becomes instantly required
        to perform any change of the module state. If the specified value is an
        empty string, a password is not required anymore.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the password for the "admin" user

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if len(newval) > YAPI.HASH_BUF_SIZE:
            self._throw(YAPI.INVALID_ARGUMENT, "Password too long :" + newval)
            return YAPI.INVALID_ARGUMENT
        rest_val = newval
        return self._setAttr("adminPassword", rest_val)

    def get_httpPort(self):
        """
        Returns the TCP port used to serve the hub web UI.

        @return an integer corresponding to the TCP port used to serve the hub web UI

        On failure, throws an exception or returns YNetwork.HTTPPORT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.HTTPPORT_INVALID
        res = self._httpPort
        return res

    def set_httpPort(self, newval):
        """
        Changes the the TCP port used to serve the hub web UI. The default value is port 80,
        which is the default for all Web servers. Regardless of the value set here,
        the hub will always reply on port 4444, which is used by default by Yoctopuce
        API library. When you change this parameter, remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the the TCP port used to serve the hub web UI

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("httpPort", rest_val)

    def get_defaultPage(self):
        """
        Returns the HTML page to serve for the URL "/"" of the hub.

        @return a string corresponding to the HTML page to serve for the URL "/"" of the hub

        On failure, throws an exception or returns YNetwork.DEFAULTPAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.DEFAULTPAGE_INVALID
        res = self._defaultPage
        return res

    def set_defaultPage(self, newval):
        """
        Changes the default HTML page returned by the hub. If not value are set the hub return
        "index.html" which is the web interface of the hub. It is possible to change this page
        for file that has been uploaded on the hub. The maximum filename size is 15 characters.
        When you change this parameter, remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the default HTML page returned by the hub

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("defaultPage", rest_val)

    def get_discoverable(self):
        """
        Returns the activation state of the multicast announce protocols to allow easy
        discovery of the module in the network neighborhood (uPnP/Bonjour protocol).

        @return either YNetwork.DISCOVERABLE_FALSE or YNetwork.DISCOVERABLE_TRUE, according to the
        activation state of the multicast announce protocols to allow easy
                discovery of the module in the network neighborhood (uPnP/Bonjour protocol)

        On failure, throws an exception or returns YNetwork.DISCOVERABLE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.DISCOVERABLE_INVALID
        res = self._discoverable
        return res

    def set_discoverable(self, newval):
        """
        Changes the activation state of the multicast announce protocols to allow easy
        discovery of the module in the network neighborhood (uPnP/Bonjour protocol).
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : either YNetwork.DISCOVERABLE_FALSE or YNetwork.DISCOVERABLE_TRUE, according to the
        activation state of the multicast announce protocols to allow easy
                discovery of the module in the network neighborhood (uPnP/Bonjour protocol)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("discoverable", rest_val)

    def get_wwwWatchdogDelay(self):
        """
        Returns the allowed downtime of the WWW link (in seconds) before triggering an automated
        reboot to try to recover Internet connectivity. A zero value disables automated reboot
        in case of Internet connectivity loss.

        @return an integer corresponding to the allowed downtime of the WWW link (in seconds) before
        triggering an automated
                reboot to try to recover Internet connectivity

        On failure, throws an exception or returns YNetwork.WWWWATCHDOGDELAY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.WWWWATCHDOGDELAY_INVALID
        res = self._wwwWatchdogDelay
        return res

    def set_wwwWatchdogDelay(self, newval):
        """
        Changes the allowed downtime of the WWW link (in seconds) before triggering an automated
        reboot to try to recover Internet connectivity. A zero value disables automated reboot
        in case of Internet connectivity loss. The smallest valid non-zero timeout is
        90 seconds. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the allowed downtime of the WWW link (in seconds)
        before triggering an automated
                reboot to try to recover Internet connectivity

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("wwwWatchdogDelay", rest_val)

    def get_callbackUrl(self):
        """
        Returns the callback URL to notify of significant state changes.

        @return a string corresponding to the callback URL to notify of significant state changes

        On failure, throws an exception or returns YNetwork.CALLBACKURL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKURL_INVALID
        res = self._callbackUrl
        return res

    def set_callbackUrl(self, newval):
        """
        Changes the callback URL to notify significant state changes. Remember to call the
        saveToFlash() method of the module if the modification must be kept.

        @param newval : a string corresponding to the callback URL to notify significant state changes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("callbackUrl", rest_val)

    def get_callbackMethod(self):
        """
        Returns the HTTP method used to notify callbacks for significant state changes.

        @return a value among YNetwork.CALLBACKMETHOD_POST, YNetwork.CALLBACKMETHOD_GET and
        YNetwork.CALLBACKMETHOD_PUT corresponding to the HTTP method used to notify callbacks for
        significant state changes

        On failure, throws an exception or returns YNetwork.CALLBACKMETHOD_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKMETHOD_INVALID
        res = self._callbackMethod
        return res

    def set_callbackMethod(self, newval):
        """
        Changes the HTTP method used to notify callbacks for significant state changes.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YNetwork.CALLBACKMETHOD_POST, YNetwork.CALLBACKMETHOD_GET and
        YNetwork.CALLBACKMETHOD_PUT corresponding to the HTTP method used to notify callbacks for
        significant state changes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("callbackMethod", rest_val)

    def get_callbackEncoding(self):
        """
        Returns the encoding standard to use for representing notification values.

        @return a value among YNetwork.CALLBACKENCODING_FORM, YNetwork.CALLBACKENCODING_JSON,
        YNetwork.CALLBACKENCODING_JSON_ARRAY, YNetwork.CALLBACKENCODING_CSV,
        YNetwork.CALLBACKENCODING_YOCTO_API, YNetwork.CALLBACKENCODING_JSON_NUM,
        YNetwork.CALLBACKENCODING_EMONCMS, YNetwork.CALLBACKENCODING_AZURE,
        YNetwork.CALLBACKENCODING_INFLUXDB, YNetwork.CALLBACKENCODING_MQTT,
        YNetwork.CALLBACKENCODING_YOCTO_API_JZON, YNetwork.CALLBACKENCODING_PRTG and
        YNetwork.CALLBACKENCODING_INFLUXDB_V2 corresponding to the encoding standard to use for
        representing notification values

        On failure, throws an exception or returns YNetwork.CALLBACKENCODING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKENCODING_INVALID
        res = self._callbackEncoding
        return res

    def set_callbackEncoding(self, newval):
        """
        Changes the encoding standard to use for representing notification values.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YNetwork.CALLBACKENCODING_FORM, YNetwork.CALLBACKENCODING_JSON,
        YNetwork.CALLBACKENCODING_JSON_ARRAY, YNetwork.CALLBACKENCODING_CSV,
        YNetwork.CALLBACKENCODING_YOCTO_API, YNetwork.CALLBACKENCODING_JSON_NUM,
        YNetwork.CALLBACKENCODING_EMONCMS, YNetwork.CALLBACKENCODING_AZURE,
        YNetwork.CALLBACKENCODING_INFLUXDB, YNetwork.CALLBACKENCODING_MQTT,
        YNetwork.CALLBACKENCODING_YOCTO_API_JZON, YNetwork.CALLBACKENCODING_PRTG and
        YNetwork.CALLBACKENCODING_INFLUXDB_V2 corresponding to the encoding standard to use for
        representing notification values

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("callbackEncoding", rest_val)

    def get_callbackCredentials(self):
        """
        Returns a hashed version of the notification callback credentials if set,
        or an empty string otherwise.

        @return a string corresponding to a hashed version of the notification callback credentials if set,
                or an empty string otherwise

        On failure, throws an exception or returns YNetwork.CALLBACKCREDENTIALS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKCREDENTIALS_INVALID
        res = self._callbackCredentials
        return res

    def set_callbackCredentials(self, newval):
        """
        Changes the credentials required to connect to the callback address. The credentials
        must be provided as returned by function get_callbackCredentials,
        in the form username:hash. The method used to compute the hash varies according
        to the the authentication scheme implemented by the callback, For Basic authentication,
        the hash is the MD5 of the string username:password. For Digest authentication,
        the hash is the MD5 of the string username:realm:password. For a simpler
        way to configure callback credentials, use function callbackLogin instead.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the credentials required to connect to the callback address

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("callbackCredentials", rest_val)

    def callbackLogin(self, username, password):
        """
        Connects to the notification callback and saves the credentials required to
        log into it. The password is not stored into the module, only a hashed
        copy of the credentials are saved. Remember to call the
        saveToFlash() method of the module if the modification must be kept.

        @param username : username required to log to the callback
        @param password : password required to log to the callback

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = username + ":" + password
        return self._setAttr("callbackCredentials", rest_val)

    def get_callbackInitialDelay(self):
        """
        Returns the initial waiting time before first callback notifications, in seconds.

        @return an integer corresponding to the initial waiting time before first callback notifications, in seconds

        On failure, throws an exception or returns YNetwork.CALLBACKINITIALDELAY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKINITIALDELAY_INVALID
        res = self._callbackInitialDelay
        return res

    def set_callbackInitialDelay(self, newval):
        """
        Changes the initial waiting time before first callback notifications, in seconds.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the initial waiting time before first callback
        notifications, in seconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("callbackInitialDelay", rest_val)

    def get_callbackSchedule(self):
        """
        Returns the HTTP callback schedule strategy, as a text string.

        @return a string corresponding to the HTTP callback schedule strategy, as a text string

        On failure, throws an exception or returns YNetwork.CALLBACKSCHEDULE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKSCHEDULE_INVALID
        res = self._callbackSchedule
        return res

    def set_callbackSchedule(self, newval):
        """
        Changes the HTTP callback schedule strategy, as a text string.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the HTTP callback schedule strategy, as a text string

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("callbackSchedule", rest_val)

    def get_callbackMinDelay(self):
        """
        Returns the minimum waiting time between two HTTP callbacks, in seconds.

        @return an integer corresponding to the minimum waiting time between two HTTP callbacks, in seconds

        On failure, throws an exception or returns YNetwork.CALLBACKMINDELAY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKMINDELAY_INVALID
        res = self._callbackMinDelay
        return res

    def set_callbackMinDelay(self, newval):
        """
        Changes the minimum waiting time between two HTTP callbacks, in seconds.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the minimum waiting time between two HTTP callbacks, in seconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("callbackMinDelay", rest_val)

    def get_callbackMaxDelay(self):
        """
        Returns the waiting time between two HTTP callbacks when there is nothing new.

        @return an integer corresponding to the waiting time between two HTTP callbacks when there is nothing new

        On failure, throws an exception or returns YNetwork.CALLBACKMAXDELAY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.CALLBACKMAXDELAY_INVALID
        res = self._callbackMaxDelay
        return res

    def set_callbackMaxDelay(self, newval):
        """
        Changes the waiting time between two HTTP callbacks when there is nothing new.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the waiting time between two HTTP callbacks when there
        is nothing new

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("callbackMaxDelay", rest_val)

    def get_poeCurrent(self):
        """
        Returns the current consumed by the module from Power-over-Ethernet (PoE), in milliamps.
        The current consumption is measured after converting PoE source to 5 Volt, and should
        never exceed 1800 mA.

        @return an integer corresponding to the current consumed by the module from Power-over-Ethernet
        (PoE), in milliamps

        On failure, throws an exception or returns YNetwork.POECURRENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YNetwork.POECURRENT_INVALID
        res = self._poeCurrent
        return res

    @staticmethod
    def FindNetwork(func):
        """
        Retrieves a network interface for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the network interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YNetwork.isOnline() to test if the network interface is
        indeed online at a given time. In case of ambiguity when looking for
        a network interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the network interface, for instance
                YHUBETH1.network.

        @return a YNetwork object allowing you to drive the network interface.
        """
        # obj
        obj = YFunction._FindFromCache("Network", func)
        if obj is None:
            obj = YNetwork(func)
            YFunction._AddToCache("Network", func, obj)
        return obj

    def useDHCP(self, fallbackIpAddr, fallbackSubnetMaskLen, fallbackRouter):
        """
        Changes the configuration of the network interface to enable the use of an
        IP address received from a DHCP server. Until an address is received from a DHCP
        server, the module uses the IP parameters specified to this function.
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param fallbackIpAddr : fallback IP address, to be used when no DHCP reply is received
        @param fallbackSubnetMaskLen : fallback subnet mask length when no DHCP reply is received, as an
                integer (e.g. 24 means 255.255.255.0)
        @param fallbackRouter : fallback router IP address, to be used when no DHCP reply is received

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_ipConfig("DHCP:" + fallbackIpAddr + "/" + str(int(fallbackSubnetMaskLen)) + "/" + fallbackRouter)

    def useDHCPauto(self):
        """
        Changes the configuration of the network interface to enable the use of an
        IP address received from a DHCP server. Until an address is received from a DHCP
        server, the module uses an IP of the network 169.254.0.0/16 (APIPA).
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_ipConfig("DHCP:")

    def useStaticIP(self, ipAddress, subnetMaskLen, router):
        """
        Changes the configuration of the network interface to use a static IP address.
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param ipAddress : device IP address
        @param subnetMaskLen : subnet mask length, as an integer (e.g. 24 means 255.255.255.0)
        @param router : router IP address (default gateway)

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_ipConfig("STATIC:" + ipAddress + "/" + str(int(subnetMaskLen)) + "/" + router)

    def ping(self, host):
        """
        Pings host to test the network connectivity. Sends four ICMP ECHO_REQUEST requests from the
        module to the target host. This method returns a string with the result of the
        4 ICMP ECHO_REQUEST requests.

        @param host : the hostname or the IP address of the target

        @return a string with the result of the ping.
        """
        # content

        content = self._download("ping.txt?host=" + host)
        return YByte2String(content)

    def triggerCallback(self):
        """
        Trigger an HTTP callback quickly. This function can even be called within
        an HTTP callback, in which case the next callback will be triggered 5 seconds
        after the end of the current callback, regardless if the minimum time between
        callbacks configured in the device.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_callbackMethod(self.get_callbackMethod())

    def set_periodicCallbackSchedule(self, interval, offset):
        """
        Setup periodic HTTP callbacks (simplified function).

        @param interval : a string representing the callback periodicity, expressed in
                seconds, minutes or hours, eg. "60s", "5m", "1h", "48h".
        @param offset : an integer representing the time offset relative to the period
                when the callback should occur. For instance, if the periodicity is
                24h, an offset of 7 will make the callback occur each day at 7AM.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_callbackSchedule("every " + interval + "+" + str(int(offset)))

    def nextNetwork(self):
        """
        Continues the enumeration of network interfaces started using yFirstNetwork().
        Caution: You can't make any assumption about the returned network interfaces order.
        If you want to find a specific a network interface, use Network.findNetwork()
        and a hardwareID or a logical name.

        @return a pointer to a YNetwork object, corresponding to
                a network interface currently online, or a None pointer
                if there are no more network interfaces to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YNetwork.FindNetwork(hwidRef.value)

#--- (end of YNetwork implementation)

#--- (YNetwork functions)

    @staticmethod
    def FirstNetwork():
        """
        Starts the enumeration of network interfaces currently accessible.
        Use the method YNetwork.nextNetwork() to iterate on
        next network interfaces.

        @return a pointer to a YNetwork object, corresponding to
                the first network interface currently online, or a None pointer
                if there are none.
        """
        devRef = YRefParam()
        neededsizeRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()
        size = YAPI.C_INTSIZE
        #noinspection PyTypeChecker,PyCallingNonCallable
        p = (ctypes.c_int * 1)()
        err = YAPI.apiGetFunctionsByClass("Network", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YNetwork.FindNetwork(serialRef.value + "." + funcIdRef.value)

#--- (end of YNetwork functions)
