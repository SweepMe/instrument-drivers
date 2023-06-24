# -*- coding: utf-8 -*-
# *********************************************************************
# *
# * $Id: yocto_wireless.py 38899 2019-12-20 17:21:03Z mvuilleu $
# *
# * Implements yFindWireless(), the high-level API for Wireless functions
# *
# * - - - - - - - - - License information: - - - - - - - - -
# *
# *  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
# *
# *  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
# *  non-exclusive license to use, modify, copy and integrate this
# *  file into your software for the sole purpose of interfacing
# *  with Yoctopuce products.
# *
# *  You may reproduce and distribute copies of this file in
# *  source or object form, as long as the sole purpose of this
# *  code is to interface with Yoctopuce products. You must retain
# *  this notice in the distributed source file.
# *
# *  You should refer to Yoctopuce General Terms and Conditions
# *  for additional information regarding your rights and
# *  obligations.
# *
# *  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
# *  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
# *  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
# *  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
# *  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
# *  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
# *  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
# *  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
# *  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
# *  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
# *  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
# *  WARRANTY, OR OTHERWISE.
# *
# *********************************************************************/


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


# --- (generated code: YWlanRecord class start)
#noinspection PyProtectedMember
class YWlanRecord(object):
    """
    YWlanRecord objects are used to describe a wireless network.
    These objects are  used in particular in conjunction with the
    YWireless class.

    """
    #--- (end of generated code: YWlanRecord class start)
    # --- (generated code: YWlanRecord definitions)
    #--- (end of generated code: YWlanRecord definitions)

    def __init__(self, json_str):
        # --- (generated code: YWlanRecord attributes)
        self._ssid = ''
        self._channel = 0
        self._sec = ''
        self._rssi = 0
        #--- (end of generated code: YWlanRecord attributes)
        json = YJSONObject(json_str, 0, len(json_str))
        json.parse()
        self._ssid = json.getString("ssid")
        self._channel = json.getInt("channel")
        self._sec = json.getString("sec")
        self._rssi = json.getInt("rssi")

    # --- (generated code: YWlanRecord implementation)
    def get_ssid(self):
        """
        Returns the name of the wireless network (SSID).

        @return a string with the name of the wireless network (SSID).
        """
        return self._ssid

    def get_channel(self):
        """
        Returns the 802.11 b/g/n channel number used by this network.

        @return an integer corresponding to the channel.
        """
        return self._channel

    def get_security(self):
        """
        Returns the security algorithm used by the wireless network.
        If the network implements to security, the value is "OPEN".

        @return a string with the security algorithm.
        """
        return self._sec

    def get_linkQuality(self):
        """
        Returns the quality of the wireless network link, in per cents.

        @return an integer between 0 and 100 corresponding to the signal quality.
        """
        return self._rssi

#--- (end of generated code: YWlanRecord implementation)

# --- (generated code: YWlanRecord functions)
#--- (end of generated code: YWlanRecord functions)


# --- (generated code: YWireless class start)
#noinspection PyProtectedMember
class YWireless(YFunction):
    """
    The YWireless class provides control over wireless network parameters
    and status for devices that are wireless-enabled.
    Note that TCP/IP parameters are configured separately, using class YNetwork.

    """
    #--- (end of generated code: YWireless class start)
    # --- (generated code: YWireless definitions)
    LINKQUALITY_INVALID = YAPI.INVALID_UINT
    SSID_INVALID = YAPI.INVALID_STRING
    CHANNEL_INVALID = YAPI.INVALID_UINT
    MESSAGE_INVALID = YAPI.INVALID_STRING
    WLANCONFIG_INVALID = YAPI.INVALID_STRING
    SECURITY_UNKNOWN = 0
    SECURITY_OPEN = 1
    SECURITY_WEP = 2
    SECURITY_WPA = 3
    SECURITY_WPA2 = 4
    SECURITY_INVALID = -1
    WLANSTATE_DOWN = 0
    WLANSTATE_SCANNING = 1
    WLANSTATE_CONNECTED = 2
    WLANSTATE_REJECTED = 3
    WLANSTATE_INVALID = -1
    #--- (end of generated code: YWireless definitions)

    def __init__(self, func):
        super(YWireless, self).__init__(func)
        self._className = "Wireless"
        # --- (generated code: YWireless attributes)
        self._callback = None
        self._linkQuality = YWireless.LINKQUALITY_INVALID
        self._ssid = YWireless.SSID_INVALID
        self._channel = YWireless.CHANNEL_INVALID
        self._security = YWireless.SECURITY_INVALID
        self._message = YWireless.MESSAGE_INVALID
        self._wlanConfig = YWireless.WLANCONFIG_INVALID
        self._wlanState = YWireless.WLANSTATE_INVALID
        #--- (end of generated code: YWireless attributes)

    # --- (generated code: YWireless implementation)
    def _parseAttr(self, json_val):
        if json_val.has("linkQuality"):
            self._linkQuality = json_val.getInt("linkQuality")
        if json_val.has("ssid"):
            self._ssid = json_val.getString("ssid")
        if json_val.has("channel"):
            self._channel = json_val.getInt("channel")
        if json_val.has("security"):
            self._security = json_val.getInt("security")
        if json_val.has("message"):
            self._message = json_val.getString("message")
        if json_val.has("wlanConfig"):
            self._wlanConfig = json_val.getString("wlanConfig")
        if json_val.has("wlanState"):
            self._wlanState = json_val.getInt("wlanState")
        super(YWireless, self)._parseAttr(json_val)

    def get_linkQuality(self):
        """
        Returns the link quality, expressed in percent.

        @return an integer corresponding to the link quality, expressed in percent

        On failure, throws an exception or returns YWireless.LINKQUALITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.LINKQUALITY_INVALID
        res = self._linkQuality
        return res

    def get_ssid(self):
        """
        Returns the wireless network name (SSID).

        @return a string corresponding to the wireless network name (SSID)

        On failure, throws an exception or returns YWireless.SSID_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.SSID_INVALID
        res = self._ssid
        return res

    def get_channel(self):
        """
        Returns the 802.11 channel currently used, or 0 when the selected network has not been found.

        @return an integer corresponding to the 802.11 channel currently used, or 0 when the selected
        network has not been found

        On failure, throws an exception or returns YWireless.CHANNEL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.CHANNEL_INVALID
        res = self._channel
        return res

    def get_security(self):
        """
        Returns the security algorithm used by the selected wireless network.

        @return a value among YWireless.SECURITY_UNKNOWN, YWireless.SECURITY_OPEN, YWireless.SECURITY_WEP,
        YWireless.SECURITY_WPA and YWireless.SECURITY_WPA2 corresponding to the security algorithm used by
        the selected wireless network

        On failure, throws an exception or returns YWireless.SECURITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.SECURITY_INVALID
        res = self._security
        return res

    def get_message(self):
        """
        Returns the latest status message from the wireless interface.

        @return a string corresponding to the latest status message from the wireless interface

        On failure, throws an exception or returns YWireless.MESSAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.MESSAGE_INVALID
        res = self._message
        return res

    def get_wlanConfig(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.WLANCONFIG_INVALID
        res = self._wlanConfig
        return res

    def set_wlanConfig(self, newval):
        rest_val = newval
        return self._setAttr("wlanConfig", rest_val)

    def get_wlanState(self):
        """
        Returns the current state of the wireless interface. The state YWireless.WLANSTATE_DOWN means that
        the network interface is
        not connected to a network. The state YWireless.WLANSTATE_SCANNING means that the network interface
        is scanning available
        frequencies. During this stage, the device is not reachable, and the network settings are not yet
        applied. The state
        YWireless.WLANSTATE_CONNECTED means that the network settings have been successfully applied ant
        that the device is reachable
        from the wireless network. If the device is configured to use ad-hoc or Soft AP mode, it means that
        the wireless network
        is up and that other devices can join the network. The state YWireless.WLANSTATE_REJECTED means
        that the network interface has
        not been able to join the requested network. The description of the error can be obtain with the
        get_message() method.

        @return a value among YWireless.WLANSTATE_DOWN, YWireless.WLANSTATE_SCANNING,
        YWireless.WLANSTATE_CONNECTED and YWireless.WLANSTATE_REJECTED corresponding to the current state
        of the wireless interface

        On failure, throws an exception or returns YWireless.WLANSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWireless.WLANSTATE_INVALID
        res = self._wlanState
        return res

    @staticmethod
    def FindWireless(func):
        """
        Retrieves a wireless LAN interface for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the wireless LAN interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWireless.isOnline() to test if the wireless LAN interface is
        indeed online at a given time. In case of ambiguity when looking for
        a wireless LAN interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the wireless LAN interface, for instance
                YHUBWLN1.wireless.

        @return a YWireless object allowing you to drive the wireless LAN interface.
        """
        # obj
        obj = YFunction._FindFromCache("Wireless", func)
        if obj is None:
            obj = YWireless(func)
            YFunction._AddToCache("Wireless", func, obj)
        return obj

    def startWlanScan(self):
        """
        Triggers a scan of the wireless frequency and builds the list of available networks.
        The scan forces a disconnection from the current network. At then end of the process, the
        the network interface attempts to reconnect to the previous network. During the scan, the wlanState
        switches to YWireless.WLANSTATE_DOWN, then to YWireless.WLANSTATE_SCANNING. When the scan is completed,
        get_wlanState() returns either YWireless.WLANSTATE_DOWN or YWireless.WLANSTATE_SCANNING. At this
        point, the list of detected network can be retrieved with the get_detectedWlans() method.

        On failure, throws an exception or returns a negative error code.
        """
        # config
        config = self.get_wlanConfig()
        # // a full scan is triggered when a config is applied
        return self.set_wlanConfig(config)

    def joinNetwork(self, ssid, securityKey):
        """
        Changes the configuration of the wireless lan interface to connect to an existing
        access point (infrastructure mode).
        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_wlanConfig("INFRA:" + ssid + "\\" + securityKey)

    def adhocNetwork(self, ssid, securityKey):
        """
        Changes the configuration of the wireless lan interface to create an ad-hoc
        wireless network, without using an access point. On the YoctoHub-Wireless-g
        and YoctoHub-Wireless-n,
        you should use softAPNetwork() instead, which emulates an access point
        (Soft AP) which is more efficient and more widely supported than ad-hoc networks.

        When a security key is specified for an ad-hoc network, the network is protected
        by a WEP40 key (5 characters or 10 hexadecimal digits) or WEP128 key (13 characters
        or 26 hexadecimal digits). It is recommended to use a well-randomized WEP128 key
        using 26 hexadecimal digits to maximize security.
        Remember to call the saveToFlash() method and then to reboot the module
        to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_wlanConfig("ADHOC:" + ssid + "\\" + securityKey)

    def softAPNetwork(self, ssid, securityKey):
        """
        Changes the configuration of the wireless lan interface to create a new wireless
        network by emulating a WiFi access point (Soft AP). This function can only be
        used with the YoctoHub-Wireless-g and the YoctoHub-Wireless-n.

        On the YoctoHub-Wireless-g, when a security key is specified for a SoftAP network,
        the network is protected by a WEP40 key (5 characters or 10 hexadecimal digits) or
        WEP128 key (13 characters or 26 hexadecimal digits). It is recommended to use a
        well-randomized WEP128 key using 26 hexadecimal digits to maximize security.

        On the YoctoHub-Wireless-n, when a security key is specified for a SoftAP network,
        the network will be protected by WPA2.

        Remember to call the saveToFlash() method and then to reboot the module to apply this setting.

        @param ssid : the name of the network to connect to
        @param securityKey : the network key, as a character string

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_wlanConfig("SOFTAP:" + ssid + "\\" + securityKey)

    def get_detectedWlans(self):
        """
        Returns a list of YWlanRecord objects that describe detected Wireless networks.
        This list is not updated when the module is already connected to an access point (infrastructure mode).
        To force an update of this list, startWlanScan() must be called.
        Note that an languages without garbage collections, the returned list must be freed by the caller.

        @return a list of YWlanRecord objects, containing the SSID, channel,
                link quality and the type of security of the wireless network.

        On failure, throws an exception or returns an empty list.
        """
        # json
        wlanlist = []
        res = []

        json = self._download("wlan.json?by=name")
        wlanlist = self._json_get_array(json)
        del res[:]
        for y in wlanlist:
            res.append(YWlanRecord(y))
        return res

    def nextWireless(self):
        """
        Continues the enumeration of wireless LAN interfaces started using yFirstWireless().
        Caution: You can't make any assumption about the returned wireless LAN interfaces order.
        If you want to find a specific a wireless LAN interface, use Wireless.findWireless()
        and a hardwareID or a logical name.

        @return a pointer to a YWireless object, corresponding to
                a wireless LAN interface currently online, or a None pointer
                if there are no more wireless LAN interfaces to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YWireless.FindWireless(hwidRef.value)

#--- (end of generated code: YWireless implementation)

    # --- (generated code: YWireless functions)

    @staticmethod
    def FirstWireless():
        """
        Starts the enumeration of wireless LAN interfaces currently accessible.
        Use the method YWireless.nextWireless() to iterate on
        next wireless LAN interfaces.

        @return a pointer to a YWireless object, corresponding to
                the first wireless LAN interface currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Wireless", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YWireless.FindWireless(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YWireless functions)
