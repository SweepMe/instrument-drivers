# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_humidity.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindHumidity(), the high-level API for Humidity functions
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


#--- (YHumidity class start)
#noinspection PyProtectedMember
class YHumidity(YSensor):
    """
    The YHumidity class allows you to read and configure Yoctopuce humidity sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YHumidity class start)
    #--- (YHumidity return codes)
    #--- (end of YHumidity return codes)
    #--- (YHumidity dlldef)
    #--- (end of YHumidity dlldef)
    #--- (YHumidity yapiwrapper)
    #--- (end of YHumidity yapiwrapper)
    #--- (YHumidity definitions)
    RELHUM_INVALID = YAPI.INVALID_DOUBLE
    ABSHUM_INVALID = YAPI.INVALID_DOUBLE
    #--- (end of YHumidity definitions)

    def __init__(self, func):
        super(YHumidity, self).__init__(func)
        self._className = 'Humidity'
        #--- (YHumidity attributes)
        self._callback = None
        self._relHum = YHumidity.RELHUM_INVALID
        self._absHum = YHumidity.ABSHUM_INVALID
        #--- (end of YHumidity attributes)

    #--- (YHumidity implementation)
    def _parseAttr(self, json_val):
        if json_val.has("relHum"):
            self._relHum = round(json_val.getDouble("relHum") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("absHum"):
            self._absHum = round(json_val.getDouble("absHum") * 1000.0 / 65536.0) / 1000.0
        super(YHumidity, self)._parseAttr(json_val)

    def set_unit(self, newval):
        """
        Changes the primary unit for measuring humidity. That unit is a string.
        If that strings starts with the letter 'g', the primary measured value is the absolute
        humidity, in g/m3. Otherwise, the primary measured value will be the relative humidity
        (RH), in per cents.

        Remember to call the saveToFlash() method of the module if the modification
        must be kept.

        @param newval : a string corresponding to the primary unit for measuring humidity

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("unit", rest_val)

    def get_relHum(self):
        """
        Returns the current relative humidity, in per cents.

        @return a floating point number corresponding to the current relative humidity, in per cents

        On failure, throws an exception or returns YHumidity.RELHUM_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YHumidity.RELHUM_INVALID
        res = self._relHum
        return res

    def get_absHum(self):
        """
        Returns the current absolute humidity, in grams per cubic meter of air.

        @return a floating point number corresponding to the current absolute humidity, in grams per cubic meter of air

        On failure, throws an exception or returns YHumidity.ABSHUM_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YHumidity.ABSHUM_INVALID
        res = self._absHum
        return res

    @staticmethod
    def FindHumidity(func):
        """
        Retrieves a humidity sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the humidity sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YHumidity.isOnline() to test if the humidity sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a humidity sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the humidity sensor, for instance
                YCO2MK02.humidity.

        @return a YHumidity object allowing you to drive the humidity sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Humidity", func)
        if obj is None:
            obj = YHumidity(func)
            YFunction._AddToCache("Humidity", func, obj)
        return obj

    def nextHumidity(self):
        """
        Continues the enumeration of humidity sensors started using yFirstHumidity().
        Caution: You can't make any assumption about the returned humidity sensors order.
        If you want to find a specific a humidity sensor, use Humidity.findHumidity()
        and a hardwareID or a logical name.

        @return a pointer to a YHumidity object, corresponding to
                a humidity sensor currently online, or a None pointer
                if there are no more humidity sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YHumidity.FindHumidity(hwidRef.value)

#--- (end of YHumidity implementation)

#--- (YHumidity functions)

    @staticmethod
    def FirstHumidity():
        """
        Starts the enumeration of humidity sensors currently accessible.
        Use the method YHumidity.nextHumidity() to iterate on
        next humidity sensors.

        @return a pointer to a YHumidity object, corresponding to
                the first humidity sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Humidity", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YHumidity.FindHumidity(serialRef.value + "." + funcIdRef.value)

#--- (end of YHumidity functions)
