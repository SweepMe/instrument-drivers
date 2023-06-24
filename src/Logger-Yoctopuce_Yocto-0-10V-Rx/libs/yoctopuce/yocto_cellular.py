#*********************************************************************
#*
#* $Id: yocto_cellular.py 40298 2020-05-05 08:37:49Z seb $
#*
#* Implements yFindCellular(), the high-level API for Cellular functions
#*
#* - - - - - - - - - License information: - - - - - - - - -
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (generated code: YCellRecord class start)
#noinspection PyProtectedMember
class YCellRecord(object):
    """
    YCellRecord objects are used to describe a wireless network.
    These objects are used in particular in conjunction with the
    YCellular class.

    """
    #--- (end of generated code: YCellRecord class start)
    #--- (generated code: YCellRecord return codes)
    #--- (end of generated code: YCellRecord return codes)
    #--- (generated code: YCellRecord dlldef)
    #--- (end of generated code: YCellRecord dlldef)
    #--- (generated code: YCellRecord definitions)
    #--- (end of generated code: YCellRecord definitions)

    def __init__(self, int_mcc, int_mnc, int_lac, int_cellId, int_dbm, int_tad, str_oper):
        #--- (generated code: YCellRecord attributes)
        self._oper = ''
        self._mcc = 0
        self._mnc = 0
        self._lac = 0
        self._cid = 0
        self._dbm = 0
        self._tad = 0
        #--- (end of generated code: YCellRecord attributes)
        self._oper = str_oper
        self._mcc = int_mcc
        self._mnc = int_mnc
        self._lac = int_lac
        self._cid = int_cellId
        self._dbm = int_dbm
        self._tad = int_tad

#--- (generated code: YCellRecord implementation)
    def get_cellOperator(self):
        """
        Returns the name of the the cell operator, as received from the network.

        @return a string with the name of the the cell operator.
        """
        return self._oper

    def get_mobileCountryCode(self):
        """
        Returns the Mobile Country Code (MCC). The MCC is a unique identifier for each country.

        @return an integer corresponding to the Mobile Country Code (MCC).
        """
        return self._mcc

    def get_mobileNetworkCode(self):
        """
        Returns the Mobile Network Code (MNC). The MNC is a unique identifier for each phone
        operator within a country.

        @return an integer corresponding to the Mobile Network Code (MNC).
        """
        return self._mnc

    def get_locationAreaCode(self):
        """
        Returns the Location Area Code (LAC). The LAC is a unique identifier for each
        place within a country.

        @return an integer corresponding to the Location Area Code (LAC).
        """
        return self._lac

    def get_cellId(self):
        """
        Returns the Cell ID. The Cell ID is a unique identifier for each
        base transmission station within a LAC.

        @return an integer corresponding to the Cell Id.
        """
        return self._cid

    def get_signalStrength(self):
        """
        Returns the signal strength, measured in dBm.

        @return an integer corresponding to the signal strength.
        """
        return self._dbm

    def get_timingAdvance(self):
        """
        Returns the Timing Advance (TA). The TA corresponds to the time necessary
        for the signal to reach the base station from the device.
        Each increment corresponds about to 550m of distance.

        @return an integer corresponding to the Timing Advance (TA).
        """
        return self._tad

#--- (end of generated code: YCellRecord implementation)

#--- (generated code: YCellRecord functions)
#--- (end of generated code: YCellRecord functions)


#--- (generated code: YCellular class start)
#noinspection PyProtectedMember
class YCellular(YFunction):
    """
    The YCellular class provides control over cellular network parameters
    and status for devices that are GSM-enabled.
    Note that TCP/IP parameters are configured separately, using class YNetwork.

    """
    #--- (end of generated code: YCellular class start)
    #--- (generated code: YCellular return codes)
    #--- (end of generated code: YCellular return codes)
    #--- (generated code: YCellular dlldef)
    #--- (end of generated code: YCellular dlldef)
    #--- (generated code: YCellular definitions)
    LINKQUALITY_INVALID = YAPI.INVALID_UINT
    CELLOPERATOR_INVALID = YAPI.INVALID_STRING
    CELLIDENTIFIER_INVALID = YAPI.INVALID_STRING
    IMSI_INVALID = YAPI.INVALID_STRING
    MESSAGE_INVALID = YAPI.INVALID_STRING
    PIN_INVALID = YAPI.INVALID_STRING
    RADIOCONFIG_INVALID = YAPI.INVALID_STRING
    LOCKEDOPERATOR_INVALID = YAPI.INVALID_STRING
    APN_INVALID = YAPI.INVALID_STRING
    APNSECRET_INVALID = YAPI.INVALID_STRING
    PINGINTERVAL_INVALID = YAPI.INVALID_UINT
    DATASENT_INVALID = YAPI.INVALID_UINT
    DATARECEIVED_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    CELLTYPE_GPRS = 0
    CELLTYPE_EGPRS = 1
    CELLTYPE_WCDMA = 2
    CELLTYPE_HSDPA = 3
    CELLTYPE_NONE = 4
    CELLTYPE_CDMA = 5
    CELLTYPE_LTE_M = 6
    CELLTYPE_NB_IOT = 7
    CELLTYPE_EC_GSM_IOT = 8
    CELLTYPE_INVALID = -1
    AIRPLANEMODE_OFF = 0
    AIRPLANEMODE_ON = 1
    AIRPLANEMODE_INVALID = -1
    ENABLEDATA_HOMENETWORK = 0
    ENABLEDATA_ROAMING = 1
    ENABLEDATA_NEVER = 2
    ENABLEDATA_NEUTRALITY = 3
    ENABLEDATA_INVALID = -1
    #--- (end of generated code: YCellular definitions)

    def __init__(self, func):
        super(YCellular, self).__init__(func)
        self._className = 'Cellular'
        #--- (generated code: YCellular attributes)
        self._callback = None
        self._linkQuality = YCellular.LINKQUALITY_INVALID
        self._cellOperator = YCellular.CELLOPERATOR_INVALID
        self._cellIdentifier = YCellular.CELLIDENTIFIER_INVALID
        self._cellType = YCellular.CELLTYPE_INVALID
        self._imsi = YCellular.IMSI_INVALID
        self._message = YCellular.MESSAGE_INVALID
        self._pin = YCellular.PIN_INVALID
        self._radioConfig = YCellular.RADIOCONFIG_INVALID
        self._lockedOperator = YCellular.LOCKEDOPERATOR_INVALID
        self._airplaneMode = YCellular.AIRPLANEMODE_INVALID
        self._enableData = YCellular.ENABLEDATA_INVALID
        self._apn = YCellular.APN_INVALID
        self._apnSecret = YCellular.APNSECRET_INVALID
        self._pingInterval = YCellular.PINGINTERVAL_INVALID
        self._dataSent = YCellular.DATASENT_INVALID
        self._dataReceived = YCellular.DATARECEIVED_INVALID
        self._command = YCellular.COMMAND_INVALID
        #--- (end of generated code: YCellular attributes)

    #--- (generated code: YCellular implementation)
    def _parseAttr(self, json_val):
        if json_val.has("linkQuality"):
            self._linkQuality = json_val.getInt("linkQuality")
        if json_val.has("cellOperator"):
            self._cellOperator = json_val.getString("cellOperator")
        if json_val.has("cellIdentifier"):
            self._cellIdentifier = json_val.getString("cellIdentifier")
        if json_val.has("cellType"):
            self._cellType = json_val.getInt("cellType")
        if json_val.has("imsi"):
            self._imsi = json_val.getString("imsi")
        if json_val.has("message"):
            self._message = json_val.getString("message")
        if json_val.has("pin"):
            self._pin = json_val.getString("pin")
        if json_val.has("radioConfig"):
            self._radioConfig = json_val.getString("radioConfig")
        if json_val.has("lockedOperator"):
            self._lockedOperator = json_val.getString("lockedOperator")
        if json_val.has("airplaneMode"):
            self._airplaneMode = (json_val.getInt("airplaneMode") > 0 if 1 else 0)
        if json_val.has("enableData"):
            self._enableData = json_val.getInt("enableData")
        if json_val.has("apn"):
            self._apn = json_val.getString("apn")
        if json_val.has("apnSecret"):
            self._apnSecret = json_val.getString("apnSecret")
        if json_val.has("pingInterval"):
            self._pingInterval = json_val.getInt("pingInterval")
        if json_val.has("dataSent"):
            self._dataSent = json_val.getInt("dataSent")
        if json_val.has("dataReceived"):
            self._dataReceived = json_val.getInt("dataReceived")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YCellular, self)._parseAttr(json_val)

    def get_linkQuality(self):
        """
        Returns the link quality, expressed in percent.

        @return an integer corresponding to the link quality, expressed in percent

        On failure, throws an exception or returns YCellular.LINKQUALITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.LINKQUALITY_INVALID
        res = self._linkQuality
        return res

    def get_cellOperator(self):
        """
        Returns the name of the cell operator currently in use.

        @return a string corresponding to the name of the cell operator currently in use

        On failure, throws an exception or returns YCellular.CELLOPERATOR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.CELLOPERATOR_INVALID
        res = self._cellOperator
        return res

    def get_cellIdentifier(self):
        """
        Returns the unique identifier of the cellular antenna in use: MCC, MNC, LAC and Cell ID.

        @return a string corresponding to the unique identifier of the cellular antenna in use: MCC, MNC,
        LAC and Cell ID

        On failure, throws an exception or returns YCellular.CELLIDENTIFIER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.CELLIDENTIFIER_INVALID
        res = self._cellIdentifier
        return res

    def get_cellType(self):
        """
        Active cellular connection type.

        @return a value among YCellular.CELLTYPE_GPRS, YCellular.CELLTYPE_EGPRS, YCellular.CELLTYPE_WCDMA,
        YCellular.CELLTYPE_HSDPA, YCellular.CELLTYPE_NONE, YCellular.CELLTYPE_CDMA,
        YCellular.CELLTYPE_LTE_M, YCellular.CELLTYPE_NB_IOT and YCellular.CELLTYPE_EC_GSM_IOT

        On failure, throws an exception or returns YCellular.CELLTYPE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.CELLTYPE_INVALID
        res = self._cellType
        return res

    def get_imsi(self):
        """
        Returns the International Mobile Subscriber Identity (MSI) that uniquely identifies
        the SIM card. The first 3 digits represent the mobile country code (MCC), which
        is followed by the mobile network code (MNC), either 2-digit (European standard)
        or 3-digit (North American standard)

        @return a string corresponding to the International Mobile Subscriber Identity (MSI) that uniquely identifies
                the SIM card

        On failure, throws an exception or returns YCellular.IMSI_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.IMSI_INVALID
        res = self._imsi
        return res

    def get_message(self):
        """
        Returns the latest status message from the wireless interface.

        @return a string corresponding to the latest status message from the wireless interface

        On failure, throws an exception or returns YCellular.MESSAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.MESSAGE_INVALID
        res = self._message
        return res

    def get_pin(self):
        """
        Returns an opaque string if a PIN code has been configured in the device to access
        the SIM card, or an empty string if none has been configured or if the code provided
        was rejected by the SIM card.

        @return a string corresponding to an opaque string if a PIN code has been configured in the device to access
                the SIM card, or an empty string if none has been configured or if the code provided
                was rejected by the SIM card

        On failure, throws an exception or returns YCellular.PIN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.PIN_INVALID
        res = self._pin
        return res

    def set_pin(self, newval):
        """
        Changes the PIN code used by the module to access the SIM card.
        This function does not change the code on the SIM card itself, but only changes
        the parameter used by the device to try to get access to it. If the SIM code
        does not work immediately on first try, it will be automatically forgotten
        and the message will be set to "Enter SIM PIN". The method should then be
        invoked again with right correct PIN code. After three failed attempts in a row,
        the message is changed to "Enter SIM PUK" and the SIM card PUK code must be
        provided using method sendPUK.

        Remember to call the saveToFlash() method of the module to save the
        new value in the device flash.

        @param newval : a string corresponding to the PIN code used by the module to access the SIM card

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("pin", rest_val)

    def get_radioConfig(self):
        """
        Returns the type of protocol used over the serial line, as a string.
        Possible values are "Line" for ASCII messages separated by CR and/or LF,
        "Frame:[timeout]ms" for binary messages separated by a delay time,
        "Char" for a continuous ASCII stream or
        "Byte" for a continuous binary stream.

        @return a string corresponding to the type of protocol used over the serial line, as a string

        On failure, throws an exception or returns YCellular.RADIOCONFIG_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.RADIOCONFIG_INVALID
        res = self._radioConfig
        return res

    def set_radioConfig(self, newval):
        """
        Changes the type of protocol used over the serial line.
        Possible values are "Line" for ASCII messages separated by CR and/or LF,
        "Frame:[timeout]ms" for binary messages separated by a delay time,
        "Char" for a continuous ASCII stream or
        "Byte" for a continuous binary stream.
        The suffix "/[wait]ms" can be added to reduce the transmit rate so that there
        is always at lest the specified number of milliseconds between each bytes sent.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the type of protocol used over the serial line

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("radioConfig", rest_val)

    def get_lockedOperator(self):
        """
        Returns the name of the only cell operator to use if automatic choice is disabled,
        or an empty string if the SIM card will automatically choose among available
        cell operators.

        @return a string corresponding to the name of the only cell operator to use if automatic choice is disabled,
                or an empty string if the SIM card will automatically choose among available
                cell operators

        On failure, throws an exception or returns YCellular.LOCKEDOPERATOR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.LOCKEDOPERATOR_INVALID
        res = self._lockedOperator
        return res

    def set_lockedOperator(self, newval):
        """
        Changes the name of the cell operator to be used. If the name is an empty
        string, the choice will be made automatically based on the SIM card. Otherwise,
        the selected operator is the only one that will be used.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the name of the cell operator to be used

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("lockedOperator", rest_val)

    def get_airplaneMode(self):
        """
        Returns true if the airplane mode is active (radio turned off).

        @return either YCellular.AIRPLANEMODE_OFF or YCellular.AIRPLANEMODE_ON, according to true if the
        airplane mode is active (radio turned off)

        On failure, throws an exception or returns YCellular.AIRPLANEMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.AIRPLANEMODE_INVALID
        res = self._airplaneMode
        return res

    def set_airplaneMode(self, newval):
        """
        Changes the activation state of airplane mode (radio turned off).

        @param newval : either YCellular.AIRPLANEMODE_OFF or YCellular.AIRPLANEMODE_ON, according to the
        activation state of airplane mode (radio turned off)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("airplaneMode", rest_val)

    def get_enableData(self):
        """
        Returns the condition for enabling IP data services (GPRS).
        When data services are disabled, SMS are the only mean of communication.

        @return a value among YCellular.ENABLEDATA_HOMENETWORK, YCellular.ENABLEDATA_ROAMING,
        YCellular.ENABLEDATA_NEVER and YCellular.ENABLEDATA_NEUTRALITY corresponding to the condition for
        enabling IP data services (GPRS)

        On failure, throws an exception or returns YCellular.ENABLEDATA_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.ENABLEDATA_INVALID
        res = self._enableData
        return res

    def set_enableData(self, newval):
        """
        Changes the condition for enabling IP data services (GPRS).
        The service can be either fully deactivated, or limited to the SIM home network,
        or enabled for all partner networks (roaming). Caution: enabling data services
        on roaming networks may cause prohibitive communication costs !

        When data services are disabled, SMS are the only mean of communication.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a value among YCellular.ENABLEDATA_HOMENETWORK, YCellular.ENABLEDATA_ROAMING,
        YCellular.ENABLEDATA_NEVER and YCellular.ENABLEDATA_NEUTRALITY corresponding to the condition for
        enabling IP data services (GPRS)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("enableData", rest_val)

    def get_apn(self):
        """
        Returns the Access Point Name (APN) to be used, if needed.
        When left blank, the APN suggested by the cell operator will be used.

        @return a string corresponding to the Access Point Name (APN) to be used, if needed

        On failure, throws an exception or returns YCellular.APN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.APN_INVALID
        res = self._apn
        return res

    def set_apn(self, newval):
        """
        Returns the Access Point Name (APN) to be used, if needed.
        When left blank, the APN suggested by the cell operator will be used.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("apn", rest_val)

    def get_apnSecret(self):
        """
        Returns an opaque string if APN authentication parameters have been configured
        in the device, or an empty string otherwise.
        To configure these parameters, use set_apnAuth().

        @return a string corresponding to an opaque string if APN authentication parameters have been configured
                in the device, or an empty string otherwise

        On failure, throws an exception or returns YCellular.APNSECRET_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.APNSECRET_INVALID
        res = self._apnSecret
        return res

    def set_apnSecret(self, newval):
        rest_val = newval
        return self._setAttr("apnSecret", rest_val)

    def get_pingInterval(self):
        """
        Returns the automated connectivity check interval, in seconds.

        @return an integer corresponding to the automated connectivity check interval, in seconds

        On failure, throws an exception or returns YCellular.PINGINTERVAL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.PINGINTERVAL_INVALID
        res = self._pingInterval
        return res

    def set_pingInterval(self, newval):
        """
        Changes the automated connectivity check interval, in seconds.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the automated connectivity check interval, in seconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("pingInterval", rest_val)

    def get_dataSent(self):
        """
        Returns the number of bytes sent so far.

        @return an integer corresponding to the number of bytes sent so far

        On failure, throws an exception or returns YCellular.DATASENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.DATASENT_INVALID
        res = self._dataSent
        return res

    def set_dataSent(self, newval):
        """
        Changes the value of the outgoing data counter.

        @param newval : an integer corresponding to the value of the outgoing data counter

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("dataSent", rest_val)

    def get_dataReceived(self):
        """
        Returns the number of bytes received so far.

        @return an integer corresponding to the number of bytes received so far

        On failure, throws an exception or returns YCellular.DATARECEIVED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.DATARECEIVED_INVALID
        res = self._dataReceived
        return res

    def set_dataReceived(self, newval):
        """
        Changes the value of the incoming data counter.

        @param newval : an integer corresponding to the value of the incoming data counter

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("dataReceived", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCellular.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindCellular(func):
        """
        Retrieves a cellular interface for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the cellular interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCellular.isOnline() to test if the cellular interface is
        indeed online at a given time. In case of ambiguity when looking for
        a cellular interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the cellular interface, for instance
                YHUBGSM1.cellular.

        @return a YCellular object allowing you to drive the cellular interface.
        """
        # obj
        obj = YFunction._FindFromCache("Cellular", func)
        if obj is None:
            obj = YCellular(func)
            YFunction._AddToCache("Cellular", func, obj)
        return obj

    def sendPUK(self, puk, newPin):
        """
        Sends a PUK code to unlock the SIM card after three failed PIN code attempts, and
        setup a new PIN into the SIM card. Only ten consecutive tentatives are permitted:
        after that, the SIM card will be blocked permanently without any mean of recovery
        to use it again. Note that after calling this method, you have usually to invoke
        method set_pin() to tell the YoctoHub which PIN to use in the future.

        @param puk : the SIM PUK code
        @param newPin : new PIN code to configure into the SIM card

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # gsmMsg
        gsmMsg = self.get_message()
        if not ((gsmMsg)[0: 0 + 13] == "Enter SIM PUK"):
            self._throw(YAPI.INVALID_ARGUMENT, "PUK not expected at this time")
            return YAPI.INVALID_ARGUMENT
        if newPin == "":
            return self.set_command("AT+CPIN=" + puk + ",0000;+CLCK=SC,0,0000")
        return self.set_command("AT+CPIN=" + puk + "," + newPin)

    def set_apnAuth(self, username, password):
        """
        Configure authentication parameters to connect to the APN. Both
        PAP and CHAP authentication are supported.

        @param username : APN username
        @param password : APN password

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_apnSecret("" + username + "," + password)

    def clearDataCounters(self):
        """
        Clear the transmitted data counters.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # retcode

        retcode = self.set_dataReceived(0)
        if retcode != YAPI.SUCCESS:
            return retcode
        retcode = self.set_dataSent(0)
        return retcode

    def _AT(self, cmd):
        """
        Sends an AT command to the GSM module and returns the command output.
        The command will only execute when the GSM module is in standard
        command state, and should leave it in the exact same state.
        Use this function with great care !

        @param cmd : the AT command to execute, like for instance: "+CCLK?".

        @return a string with the result of the commands. Empty lines are
                automatically removed from the output.
        """
        # chrPos
        # cmdLen
        # waitMore
        # res
        # buff
        # bufflen
        # buffstr
        # buffstrlen
        # idx
        # suffixlen
        # // quote dangerous characters used in AT commands
        cmdLen = len(cmd)
        chrPos = cmd.find("#")
        while chrPos >= 0:
            cmd = "" + (cmd)[0: 0 + chrPos] + "" + str(chr(37)) + "23" + (cmd)[chrPos+1: chrPos+1 + cmdLen-chrPos-1]
            cmdLen = cmdLen + 2
            chrPos = cmd.find("#")
        chrPos = cmd.find("+")
        while chrPos >= 0:
            cmd = "" + (cmd)[0: 0 + chrPos] + "" + str(chr(37)) + "2B" + (cmd)[chrPos+1: chrPos+1 + cmdLen-chrPos-1]
            cmdLen = cmdLen + 2
            chrPos = cmd.find("+")
        chrPos = cmd.find("=")
        while chrPos >= 0:
            cmd = "" + (cmd)[0: 0 + chrPos] + "" + str(chr(37)) + "3D" + (cmd)[chrPos+1: chrPos+1 + cmdLen-chrPos-1]
            cmdLen = cmdLen + 2
            chrPos = cmd.find("=")
        cmd = "at.txt?cmd=" + cmd
        res = ""
        # // max 2 minutes (each iteration may take up to 5 seconds if waiting)
        waitMore = 24
        while waitMore > 0:
            buff = self._download(cmd)
            bufflen = len(buff)
            buffstr = YByte2String(buff)
            buffstrlen = len(buffstr)
            idx = bufflen - 1
            while (idx > 0) and (YGetByte(buff, idx) != 64) and (YGetByte(buff, idx) != 10) and (YGetByte(buff, idx) != 13):
                idx = idx - 1
            if YGetByte(buff, idx) == 64:
                # // continuation detected
                suffixlen = bufflen - idx
                cmd = "at.txt?cmd=" + (buffstr)[buffstrlen - suffixlen: buffstrlen - suffixlen + suffixlen]
                buffstr = (buffstr)[0: 0 + buffstrlen - suffixlen]
                waitMore = waitMore - 1
            else:
                # // request complete
                waitMore = 0
            res = "" + res + "" + buffstr
        return res

    def get_availableOperators(self):
        """
        Returns the list detected cell operators in the neighborhood.
        This function will typically take between 30 seconds to 1 minute to
        return. Note that any SIM card can usually only connect to specific
        operators. All networks returned by this function might therefore
        not be available for connection.

        @return a list of string (cell operator names).
        """
        # cops
        # idx
        # slen
        res = []

        cops = self._AT("+COPS=?")
        slen = len(cops)
        del res[:]
        idx = cops.find("(")
        while idx >= 0:
            slen = slen - (idx+1)
            cops = (cops)[idx+1: idx+1 + slen]
            idx = cops.find("\"")
            if idx > 0:
                slen = slen - (idx+1)
                cops = (cops)[idx+1: idx+1 + slen]
                idx = cops.find("\"")
                if idx > 0:
                    res.append((cops)[0: 0 + idx])
            idx = cops.find("(")

        return res

    def quickCellSurvey(self):
        """
        Returns a list of nearby cellular antennas, as required for quick
        geolocation of the device. The first cell listed is the serving
        cell, and the next ones are the neighbor cells reported by the
        serving cell.

        @return a list of YCellRecords.
        """
        # moni
        recs = []
        # llen
        # mccs
        # mcc
        # mncs
        # mnc
        # lac
        # cellId
        # dbms
        # dbm
        # tads
        # tad
        # oper
        res = []

        moni = self._AT("+CCED=0;#MONI=7;#MONI")
        mccs = (moni)[7: 7 + 3]
        if (mccs)[0: 0 + 1] == "0":
            mccs = (mccs)[1: 1 + 2]
        if (mccs)[0: 0 + 1] == "0":
            mccs = (mccs)[1: 1 + 1]
        mcc = YAPI._atoi(mccs)
        mncs = (moni)[11: 11 + 3]
        if (mncs)[2: 2 + 1] == ",":
            mncs = (mncs)[0: 0 + 2]
        if (mncs)[0: 0 + 1] == "0":
            mncs = (mncs)[1: 1 + len(mncs)-1]
        mnc = YAPI._atoi(mncs)
        recs = (moni).split('#')
        # // process each line in turn
        del res[:]
        for y in recs:
            llen = len(y) - 2
            if llen >= 44:
                if (y)[41: 41 + 3] == "dbm":
                    lac = int((y)[16: 16 + 4], 16)
                    cellId = int((y)[23: 23 + 4], 16)
                    dbms = (y)[37: 37 + 4]
                    if (dbms)[0: 0 + 1] == " ":
                        dbms = (dbms)[1: 1 + 3]
                    dbm = YAPI._atoi(dbms)
                    if llen > 66:
                        tads = (y)[54: 54 + 2]
                        if (tads)[0: 0 + 1] == " ":
                            tads = (tads)[1: 1 + 3]
                        tad = YAPI._atoi(tads)
                        oper = (y)[66: 66 + llen-66]
                    else:
                        tad = -1
                        oper = ""
                    if lac < 65535:
                        res.append(YCellRecord(mcc, mnc, lac, cellId, dbm, tad, oper))
        return res

    def nextCellular(self):
        """
        Continues the enumeration of cellular interfaces started using yFirstCellular().
        Caution: You can't make any assumption about the returned cellular interfaces order.
        If you want to find a specific a cellular interface, use Cellular.findCellular()
        and a hardwareID or a logical name.

        @return a pointer to a YCellular object, corresponding to
                a cellular interface currently online, or a None pointer
                if there are no more cellular interfaces to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YCellular.FindCellular(hwidRef.value)

#--- (end of generated code: YCellular implementation)

#--- (generated code: YCellular functions)

    @staticmethod
    def FirstCellular():
        """
        Starts the enumeration of cellular interfaces currently accessible.
        Use the method YCellular.nextCellular() to iterate on
        next cellular interfaces.

        @return a pointer to a YCellular object, corresponding to
                the first cellular interface currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Cellular", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YCellular.FindCellular(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YCellular functions)
