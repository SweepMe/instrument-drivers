# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_current.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindCurrent(), the high-level API for Current functions
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


#--- (YCurrent class start)
#noinspection PyProtectedMember
class YCurrent(YSensor):
    """
    The YCurrent class allows you to read and configure Yoctopuce current sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YCurrent class start)
    #--- (YCurrent return codes)
    #--- (end of YCurrent return codes)
    #--- (YCurrent dlldef)
    #--- (end of YCurrent dlldef)
    #--- (YCurrent yapiwrapper)
    #--- (end of YCurrent yapiwrapper)
    #--- (YCurrent definitions)
    ENABLED_FALSE = 0
    ENABLED_TRUE = 1
    ENABLED_INVALID = -1
    #--- (end of YCurrent definitions)

    def __init__(self, func):
        super(YCurrent, self).__init__(func)
        self._className = 'Current'
        #--- (YCurrent attributes)
        self._callback = None
        self._enabled = YCurrent.ENABLED_INVALID
        #--- (end of YCurrent attributes)

    #--- (YCurrent implementation)
    def _parseAttr(self, json_val):
        if json_val.has("enabled"):
            self._enabled = (json_val.getInt("enabled") > 0 if 1 else 0)
        super(YCurrent, self)._parseAttr(json_val)

    def get_enabled(self):
        """
        Returns the activation state of this input.

        @return either YCurrent.ENABLED_FALSE or YCurrent.ENABLED_TRUE, according to the activation state of this input

        On failure, throws an exception or returns YCurrent.ENABLED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrent.ENABLED_INVALID
        res = self._enabled
        return res

    def set_enabled(self, newval):
        """
        Changes the activation state of this voltage input. When AC measurements are disabled,
        the device will always assume a DC signal, and vice-versa. When both AC and DC measurements
        are active, the device switches between AC and DC mode based on the relative amplitude
        of variations compared to the average value.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : either YCurrent.ENABLED_FALSE or YCurrent.ENABLED_TRUE, according to the activation
        state of this voltage input

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabled", rest_val)

    @staticmethod
    def FindCurrent(func):
        """
        Retrieves a current sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the current sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCurrent.isOnline() to test if the current sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a current sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the current sensor, for instance
                YAMPMK01.current1.

        @return a YCurrent object allowing you to drive the current sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Current", func)
        if obj is None:
            obj = YCurrent(func)
            YFunction._AddToCache("Current", func, obj)
        return obj

    def nextCurrent(self):
        """
        Continues the enumeration of current sensors started using yFirstCurrent().
        Caution: You can't make any assumption about the returned current sensors order.
        If you want to find a specific a current sensor, use Current.findCurrent()
        and a hardwareID or a logical name.

        @return a pointer to a YCurrent object, corresponding to
                a current sensor currently online, or a None pointer
                if there are no more current sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YCurrent.FindCurrent(hwidRef.value)

#--- (end of YCurrent implementation)

#--- (YCurrent functions)

    @staticmethod
    def FirstCurrent():
        """
        Starts the enumeration of current sensors currently accessible.
        Use the method YCurrent.nextCurrent() to iterate on
        next current sensors.

        @return a pointer to a YCurrent object, corresponding to
                the first current sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Current", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YCurrent.FindCurrent(serialRef.value + "." + funcIdRef.value)

#--- (end of YCurrent functions)
