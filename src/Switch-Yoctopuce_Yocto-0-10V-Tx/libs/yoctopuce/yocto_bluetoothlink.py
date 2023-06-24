# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_bluetoothlink.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindBluetoothLink(), the high-level API for BluetoothLink functions
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


#--- (YBluetoothLink class start)
#noinspection PyProtectedMember
class YBluetoothLink(YFunction):
    """
    BluetoothLink function provides control over Bluetooth link
    and status for devices that are Bluetooth-enabled.

    """
    #--- (end of YBluetoothLink class start)
    #--- (YBluetoothLink return codes)
    #--- (end of YBluetoothLink return codes)
    #--- (YBluetoothLink dlldef)
    #--- (end of YBluetoothLink dlldef)
    #--- (YBluetoothLink yapiwrapper)
    #--- (end of YBluetoothLink yapiwrapper)
    #--- (YBluetoothLink definitions)
    OWNADDRESS_INVALID = YAPI.INVALID_STRING
    PAIRINGPIN_INVALID = YAPI.INVALID_STRING
    REMOTEADDRESS_INVALID = YAPI.INVALID_STRING
    REMOTENAME_INVALID = YAPI.INVALID_STRING
    PREAMPLIFIER_INVALID = YAPI.INVALID_UINT
    VOLUME_INVALID = YAPI.INVALID_UINT
    LINKQUALITY_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    MUTE_FALSE = 0
    MUTE_TRUE = 1
    MUTE_INVALID = -1
    LINKSTATE_DOWN = 0
    LINKSTATE_FREE = 1
    LINKSTATE_SEARCH = 2
    LINKSTATE_EXISTS = 3
    LINKSTATE_LINKED = 4
    LINKSTATE_PLAY = 5
    LINKSTATE_INVALID = -1
    #--- (end of YBluetoothLink definitions)

    def __init__(self, func):
        super(YBluetoothLink, self).__init__(func)
        self._className = 'BluetoothLink'
        #--- (YBluetoothLink attributes)
        self._callback = None
        self._ownAddress = YBluetoothLink.OWNADDRESS_INVALID
        self._pairingPin = YBluetoothLink.PAIRINGPIN_INVALID
        self._remoteAddress = YBluetoothLink.REMOTEADDRESS_INVALID
        self._remoteName = YBluetoothLink.REMOTENAME_INVALID
        self._mute = YBluetoothLink.MUTE_INVALID
        self._preAmplifier = YBluetoothLink.PREAMPLIFIER_INVALID
        self._volume = YBluetoothLink.VOLUME_INVALID
        self._linkState = YBluetoothLink.LINKSTATE_INVALID
        self._linkQuality = YBluetoothLink.LINKQUALITY_INVALID
        self._command = YBluetoothLink.COMMAND_INVALID
        #--- (end of YBluetoothLink attributes)

    #--- (YBluetoothLink implementation)
    def _parseAttr(self, json_val):
        if json_val.has("ownAddress"):
            self._ownAddress = json_val.getString("ownAddress")
        if json_val.has("pairingPin"):
            self._pairingPin = json_val.getString("pairingPin")
        if json_val.has("remoteAddress"):
            self._remoteAddress = json_val.getString("remoteAddress")
        if json_val.has("remoteName"):
            self._remoteName = json_val.getString("remoteName")
        if json_val.has("mute"):
            self._mute = (json_val.getInt("mute") > 0 if 1 else 0)
        if json_val.has("preAmplifier"):
            self._preAmplifier = json_val.getInt("preAmplifier")
        if json_val.has("volume"):
            self._volume = json_val.getInt("volume")
        if json_val.has("linkState"):
            self._linkState = json_val.getInt("linkState")
        if json_val.has("linkQuality"):
            self._linkQuality = json_val.getInt("linkQuality")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YBluetoothLink, self)._parseAttr(json_val)

    def get_ownAddress(self):
        """
        Returns the MAC-48 address of the bluetooth interface, which is unique on the bluetooth network.

        @return a string corresponding to the MAC-48 address of the bluetooth interface, which is unique on
        the bluetooth network

        On failure, throws an exception or returns YBluetoothLink.OWNADDRESS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.OWNADDRESS_INVALID
        res = self._ownAddress
        return res

    def get_pairingPin(self):
        """
        Returns an opaque string if a PIN code has been configured in the device to access
        the SIM card, or an empty string if none has been configured or if the code provided
        was rejected by the SIM card.

        @return a string corresponding to an opaque string if a PIN code has been configured in the device to access
                the SIM card, or an empty string if none has been configured or if the code provided
                was rejected by the SIM card

        On failure, throws an exception or returns YBluetoothLink.PAIRINGPIN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.PAIRINGPIN_INVALID
        res = self._pairingPin
        return res

    def set_pairingPin(self, newval):
        """
        Changes the PIN code used by the module for bluetooth pairing.
        Remember to call the saveToFlash() method of the module to save the
        new value in the device flash.

        @param newval : a string corresponding to the PIN code used by the module for bluetooth pairing

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("pairingPin", rest_val)

    def get_remoteAddress(self):
        """
        Returns the MAC-48 address of the remote device to connect to.

        @return a string corresponding to the MAC-48 address of the remote device to connect to

        On failure, throws an exception or returns YBluetoothLink.REMOTEADDRESS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.REMOTEADDRESS_INVALID
        res = self._remoteAddress
        return res

    def set_remoteAddress(self, newval):
        """
        Changes the MAC-48 address defining which remote device to connect to.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the MAC-48 address defining which remote device to connect to

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("remoteAddress", rest_val)

    def get_remoteName(self):
        """
        Returns the bluetooth name the remote device, if found on the bluetooth network.

        @return a string corresponding to the bluetooth name the remote device, if found on the bluetooth network

        On failure, throws an exception or returns YBluetoothLink.REMOTENAME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.REMOTENAME_INVALID
        res = self._remoteName
        return res

    def get_mute(self):
        """
        Returns the state of the mute function.

        @return either YBluetoothLink.MUTE_FALSE or YBluetoothLink.MUTE_TRUE, according to the state of the
        mute function

        On failure, throws an exception or returns YBluetoothLink.MUTE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.MUTE_INVALID
        res = self._mute
        return res

    def set_mute(self, newval):
        """
        Changes the state of the mute function. Remember to call the matching module
        saveToFlash() method to save the setting permanently.

        @param newval : either YBluetoothLink.MUTE_FALSE or YBluetoothLink.MUTE_TRUE, according to the
        state of the mute function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("mute", rest_val)

    def get_preAmplifier(self):
        """
        Returns the audio pre-amplifier volume, in per cents.

        @return an integer corresponding to the audio pre-amplifier volume, in per cents

        On failure, throws an exception or returns YBluetoothLink.PREAMPLIFIER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.PREAMPLIFIER_INVALID
        res = self._preAmplifier
        return res

    def set_preAmplifier(self, newval):
        """
        Changes the audio pre-amplifier volume, in per cents.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the audio pre-amplifier volume, in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("preAmplifier", rest_val)

    def get_volume(self):
        """
        Returns the connected headset volume, in per cents.

        @return an integer corresponding to the connected headset volume, in per cents

        On failure, throws an exception or returns YBluetoothLink.VOLUME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.VOLUME_INVALID
        res = self._volume
        return res

    def set_volume(self, newval):
        """
        Changes the connected headset volume, in per cents.

        @param newval : an integer corresponding to the connected headset volume, in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("volume", rest_val)

    def get_linkState(self):
        """
        Returns the bluetooth link state.

        @return a value among YBluetoothLink.LINKSTATE_DOWN, YBluetoothLink.LINKSTATE_FREE,
        YBluetoothLink.LINKSTATE_SEARCH, YBluetoothLink.LINKSTATE_EXISTS, YBluetoothLink.LINKSTATE_LINKED
        and YBluetoothLink.LINKSTATE_PLAY corresponding to the bluetooth link state

        On failure, throws an exception or returns YBluetoothLink.LINKSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.LINKSTATE_INVALID
        res = self._linkState
        return res

    def get_linkQuality(self):
        """
        Returns the bluetooth receiver signal strength, in pourcents, or 0 if no connection is established.

        @return an integer corresponding to the bluetooth receiver signal strength, in pourcents, or 0 if
        no connection is established

        On failure, throws an exception or returns YBluetoothLink.LINKQUALITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.LINKQUALITY_INVALID
        res = self._linkQuality
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBluetoothLink.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindBluetoothLink(func):
        """
        Retrieves a Bluetooth sound controller for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the Bluetooth sound controller is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YBluetoothLink.isOnline() to test if the Bluetooth sound controller is
        indeed online at a given time. In case of ambiguity when looking for
        a Bluetooth sound controller by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the Bluetooth sound controller, for instance
                MyDevice.bluetoothLink1.

        @return a YBluetoothLink object allowing you to drive the Bluetooth sound controller.
        """
        # obj
        obj = YFunction._FindFromCache("BluetoothLink", func)
        if obj is None:
            obj = YBluetoothLink(func)
            YFunction._AddToCache("BluetoothLink", func, obj)
        return obj

    def connect(self):
        """
        Attempt to connect to the previously selected remote device.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("C")

    def disconnect(self):
        """
        Disconnect from the previously selected remote device.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("D")

    def nextBluetoothLink(self):
        """
        Continues the enumeration of Bluetooth sound controllers started using yFirstBluetoothLink().
        Caution: You can't make any assumption about the returned Bluetooth sound controllers order.
        If you want to find a specific a Bluetooth sound controller, use BluetoothLink.findBluetoothLink()
        and a hardwareID or a logical name.

        @return a pointer to a YBluetoothLink object, corresponding to
                a Bluetooth sound controller currently online, or a None pointer
                if there are no more Bluetooth sound controllers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YBluetoothLink.FindBluetoothLink(hwidRef.value)

#--- (end of YBluetoothLink implementation)

#--- (YBluetoothLink functions)

    @staticmethod
    def FirstBluetoothLink():
        """
        Starts the enumeration of Bluetooth sound controllers currently accessible.
        Use the method YBluetoothLink.nextBluetoothLink() to iterate on
        next Bluetooth sound controllers.

        @return a pointer to a YBluetoothLink object, corresponding to
                the first Bluetooth sound controller currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("BluetoothLink", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YBluetoothLink.FindBluetoothLink(serialRef.value + "." + funcIdRef.value)

#--- (end of YBluetoothLink functions)
