# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_accelerometer.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindAccelerometer(), the high-level API for Accelerometer functions
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


#--- (YAccelerometer class start)
#noinspection PyProtectedMember
class YAccelerometer(YSensor):
    """
    The YAccelerometer class allows you to read and configure Yoctopuce accelerometers.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the possibility to access x, y and z components of the acceleration
    vector separately.

    """
    #--- (end of YAccelerometer class start)
    #--- (YAccelerometer return codes)
    #--- (end of YAccelerometer return codes)
    #--- (YAccelerometer dlldef)
    #--- (end of YAccelerometer dlldef)
    #--- (YAccelerometer yapiwrapper)
    #--- (end of YAccelerometer yapiwrapper)
    #--- (YAccelerometer definitions)
    BANDWIDTH_INVALID = YAPI.INVALID_UINT
    XVALUE_INVALID = YAPI.INVALID_DOUBLE
    YVALUE_INVALID = YAPI.INVALID_DOUBLE
    ZVALUE_INVALID = YAPI.INVALID_DOUBLE
    GRAVITYCANCELLATION_OFF = 0
    GRAVITYCANCELLATION_ON = 1
    GRAVITYCANCELLATION_INVALID = -1
    #--- (end of YAccelerometer definitions)

    def __init__(self, func):
        super(YAccelerometer, self).__init__(func)
        self._className = 'Accelerometer'
        #--- (YAccelerometer attributes)
        self._callback = None
        self._bandwidth = YAccelerometer.BANDWIDTH_INVALID
        self._xValue = YAccelerometer.XVALUE_INVALID
        self._yValue = YAccelerometer.YVALUE_INVALID
        self._zValue = YAccelerometer.ZVALUE_INVALID
        self._gravityCancellation = YAccelerometer.GRAVITYCANCELLATION_INVALID
        #--- (end of YAccelerometer attributes)

    #--- (YAccelerometer implementation)
    def _parseAttr(self, json_val):
        if json_val.has("bandwidth"):
            self._bandwidth = json_val.getInt("bandwidth")
        if json_val.has("xValue"):
            self._xValue = round(json_val.getDouble("xValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("yValue"):
            self._yValue = round(json_val.getDouble("yValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("zValue"):
            self._zValue = round(json_val.getDouble("zValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("gravityCancellation"):
            self._gravityCancellation = (json_val.getInt("gravityCancellation") > 0 if 1 else 0)
        super(YAccelerometer, self)._parseAttr(json_val)

    def get_bandwidth(self):
        """
        Returns the measure update frequency, measured in Hz (Yocto-3D-V2 only).

        @return an integer corresponding to the measure update frequency, measured in Hz (Yocto-3D-V2 only)

        On failure, throws an exception or returns YAccelerometer.BANDWIDTH_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAccelerometer.BANDWIDTH_INVALID
        res = self._bandwidth
        return res

    def set_bandwidth(self, newval):
        """
        Changes the measure update frequency, measured in Hz (Yocto-3D-V2 only). When the
        frequency is lower, the device performs averaging.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the measure update frequency, measured in Hz (Yocto-3D-V2 only)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("bandwidth", rest_val)

    def get_xValue(self):
        """
        Returns the X component of the acceleration, as a floating point number.

        @return a floating point number corresponding to the X component of the acceleration, as a floating point number

        On failure, throws an exception or returns YAccelerometer.XVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAccelerometer.XVALUE_INVALID
        res = self._xValue
        return res

    def get_yValue(self):
        """
        Returns the Y component of the acceleration, as a floating point number.

        @return a floating point number corresponding to the Y component of the acceleration, as a floating point number

        On failure, throws an exception or returns YAccelerometer.YVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAccelerometer.YVALUE_INVALID
        res = self._yValue
        return res

    def get_zValue(self):
        """
        Returns the Z component of the acceleration, as a floating point number.

        @return a floating point number corresponding to the Z component of the acceleration, as a floating point number

        On failure, throws an exception or returns YAccelerometer.ZVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAccelerometer.ZVALUE_INVALID
        res = self._zValue
        return res

    def get_gravityCancellation(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAccelerometer.GRAVITYCANCELLATION_INVALID
        res = self._gravityCancellation
        return res

    def set_gravityCancellation(self, newval):
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("gravityCancellation", rest_val)

    @staticmethod
    def FindAccelerometer(func):
        """
        Retrieves an accelerometer for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the accelerometer is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAccelerometer.isOnline() to test if the accelerometer is
        indeed online at a given time. In case of ambiguity when looking for
        an accelerometer by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the accelerometer, for instance
                Y3DMK002.accelerometer.

        @return a YAccelerometer object allowing you to drive the accelerometer.
        """
        # obj
        obj = YFunction._FindFromCache("Accelerometer", func)
        if obj is None:
            obj = YAccelerometer(func)
            YFunction._AddToCache("Accelerometer", func, obj)
        return obj

    def nextAccelerometer(self):
        """
        Continues the enumeration of accelerometers started using yFirstAccelerometer().
        Caution: You can't make any assumption about the returned accelerometers order.
        If you want to find a specific an accelerometer, use Accelerometer.findAccelerometer()
        and a hardwareID or a logical name.

        @return a pointer to a YAccelerometer object, corresponding to
                an accelerometer currently online, or a None pointer
                if there are no more accelerometers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YAccelerometer.FindAccelerometer(hwidRef.value)

#--- (end of YAccelerometer implementation)

#--- (YAccelerometer functions)

    @staticmethod
    def FirstAccelerometer():
        """
        Starts the enumeration of accelerometers currently accessible.
        Use the method YAccelerometer.nextAccelerometer() to iterate on
        next accelerometers.

        @return a pointer to a YAccelerometer object, corresponding to
                the first accelerometer currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Accelerometer", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YAccelerometer.FindAccelerometer(serialRef.value + "." + funcIdRef.value)

#--- (end of YAccelerometer functions)
