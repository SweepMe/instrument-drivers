# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_lightsensor.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindLightSensor(), the high-level API for LightSensor functions
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


#--- (YLightSensor class start)
#noinspection PyProtectedMember
class YLightSensor(YSensor):
    """
    The YLightSensor class allows you to read and configure Yoctopuce light sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the ability to easily perform a one-point linear calibration
    to compensate the effect of a glass or filter placed in front of the sensor.
    For some light sensors with several working modes, this class can select the
    desired working mode.

    """
    #--- (end of YLightSensor class start)
    #--- (YLightSensor return codes)
    #--- (end of YLightSensor return codes)
    #--- (YLightSensor dlldef)
    #--- (end of YLightSensor dlldef)
    #--- (YLightSensor yapiwrapper)
    #--- (end of YLightSensor yapiwrapper)
    #--- (YLightSensor definitions)
    MEASURETYPE_HUMAN_EYE = 0
    MEASURETYPE_WIDE_SPECTRUM = 1
    MEASURETYPE_INFRARED = 2
    MEASURETYPE_HIGH_RATE = 3
    MEASURETYPE_HIGH_ENERGY = 4
    MEASURETYPE_INVALID = -1
    #--- (end of YLightSensor definitions)

    def __init__(self, func):
        super(YLightSensor, self).__init__(func)
        self._className = 'LightSensor'
        #--- (YLightSensor attributes)
        self._callback = None
        self._measureType = YLightSensor.MEASURETYPE_INVALID
        #--- (end of YLightSensor attributes)

    #--- (YLightSensor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("measureType"):
            self._measureType = json_val.getInt("measureType")
        super(YLightSensor, self)._parseAttr(json_val)

    def set_currentValue(self, newval):
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("currentValue", rest_val)

    def calibrate(self, calibratedVal):
        """
        Changes the sensor-specific calibration parameter so that the current value
        matches a desired target (linear scaling).

        @param calibratedVal : the desired target value.

        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(calibratedVal * 65536.0, 1)))
        return self._setAttr("currentValue", rest_val)

    def get_measureType(self):
        """
        Returns the type of light measure.

        @return a value among YLightSensor.MEASURETYPE_HUMAN_EYE, YLightSensor.MEASURETYPE_WIDE_SPECTRUM,
        YLightSensor.MEASURETYPE_INFRARED, YLightSensor.MEASURETYPE_HIGH_RATE and
        YLightSensor.MEASURETYPE_HIGH_ENERGY corresponding to the type of light measure

        On failure, throws an exception or returns YLightSensor.MEASURETYPE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YLightSensor.MEASURETYPE_INVALID
        res = self._measureType
        return res

    def set_measureType(self, newval):
        """
        Changes the light sensor type used in the device. The measure can either
        approximate the response of the human eye, focus on a specific light
        spectrum, depending on the capabilities of the light-sensitive cell.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YLightSensor.MEASURETYPE_HUMAN_EYE,
        YLightSensor.MEASURETYPE_WIDE_SPECTRUM, YLightSensor.MEASURETYPE_INFRARED,
        YLightSensor.MEASURETYPE_HIGH_RATE and YLightSensor.MEASURETYPE_HIGH_ENERGY corresponding to the
        light sensor type used in the device

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("measureType", rest_val)

    @staticmethod
    def FindLightSensor(func):
        """
        Retrieves a light sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the light sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YLightSensor.isOnline() to test if the light sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a light sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the light sensor, for instance
                LIGHTMK3.lightSensor.

        @return a YLightSensor object allowing you to drive the light sensor.
        """
        # obj
        obj = YFunction._FindFromCache("LightSensor", func)
        if obj is None:
            obj = YLightSensor(func)
            YFunction._AddToCache("LightSensor", func, obj)
        return obj

    def nextLightSensor(self):
        """
        Continues the enumeration of light sensors started using yFirstLightSensor().
        Caution: You can't make any assumption about the returned light sensors order.
        If you want to find a specific a light sensor, use LightSensor.findLightSensor()
        and a hardwareID or a logical name.

        @return a pointer to a YLightSensor object, corresponding to
                a light sensor currently online, or a None pointer
                if there are no more light sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YLightSensor.FindLightSensor(hwidRef.value)

#--- (end of YLightSensor implementation)

#--- (YLightSensor functions)

    @staticmethod
    def FirstLightSensor():
        """
        Starts the enumeration of light sensors currently accessible.
        Use the method YLightSensor.nextLightSensor() to iterate on
        next light sensors.

        @return a pointer to a YLightSensor object, corresponding to
                the first light sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("LightSensor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YLightSensor.FindLightSensor(serialRef.value + "." + funcIdRef.value)

#--- (end of YLightSensor functions)
