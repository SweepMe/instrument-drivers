# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_carbondioxide.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindCarbonDioxide(), the high-level API for CarbonDioxide functions
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


#--- (YCarbonDioxide class start)
#noinspection PyProtectedMember
class YCarbonDioxide(YSensor):
    """
    The YCarbonDioxide class allows you to read and configure Yoctopuce CO2 sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the ability to perform manual calibration if required.

    """
    #--- (end of YCarbonDioxide class start)
    #--- (YCarbonDioxide return codes)
    #--- (end of YCarbonDioxide return codes)
    #--- (YCarbonDioxide dlldef)
    #--- (end of YCarbonDioxide dlldef)
    #--- (YCarbonDioxide yapiwrapper)
    #--- (end of YCarbonDioxide yapiwrapper)
    #--- (YCarbonDioxide definitions)
    ABCPERIOD_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    #--- (end of YCarbonDioxide definitions)

    def __init__(self, func):
        super(YCarbonDioxide, self).__init__(func)
        self._className = 'CarbonDioxide'
        #--- (YCarbonDioxide attributes)
        self._callback = None
        self._abcPeriod = YCarbonDioxide.ABCPERIOD_INVALID
        self._command = YCarbonDioxide.COMMAND_INVALID
        #--- (end of YCarbonDioxide attributes)

    #--- (YCarbonDioxide implementation)
    def _parseAttr(self, json_val):
        if json_val.has("abcPeriod"):
            self._abcPeriod = json_val.getInt("abcPeriod")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YCarbonDioxide, self)._parseAttr(json_val)

    def get_abcPeriod(self):
        """
        Returns the Automatic Baseline Calibration period, in hours. A negative value
        means that automatic baseline calibration is disabled.

        @return an integer corresponding to the Automatic Baseline Calibration period, in hours

        On failure, throws an exception or returns YCarbonDioxide.ABCPERIOD_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCarbonDioxide.ABCPERIOD_INVALID
        res = self._abcPeriod
        return res

    def set_abcPeriod(self, newval):
        """
        Changes Automatic Baseline Calibration period, in hours. If you need
        to disable automatic baseline calibration (for instance when using the
        sensor in an environment that is constantly above 400 ppm CO2), set the
        period to -1. Remember to call the saveToFlash() method of the
        module if the modification must be kept.

        @param newval : an integer corresponding to Automatic Baseline Calibration period, in hours

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("abcPeriod", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCarbonDioxide.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindCarbonDioxide(func):
        """
        Retrieves a CO2 sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the CO2 sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCarbonDioxide.isOnline() to test if the CO2 sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a CO2 sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the CO2 sensor, for instance
                YCO2MK02.carbonDioxide.

        @return a YCarbonDioxide object allowing you to drive the CO2 sensor.
        """
        # obj
        obj = YFunction._FindFromCache("CarbonDioxide", func)
        if obj is None:
            obj = YCarbonDioxide(func)
            YFunction._AddToCache("CarbonDioxide", func, obj)
        return obj

    def triggerBaselineCalibration(self):
        """
        Triggers a baseline calibration at standard CO2 ambiant level (400ppm).
        It is normally not necessary to manually calibrate the sensor, because
        the built-in automatic baseline calibration procedure will automatically
        fix any long-term drift based on the lowest level of CO2 observed over the
        automatic calibration period. However, if you disable automatic baseline
        calibration, you may want to manually trigger a calibration from time to
        time. Before starting a baseline calibration, make sure to put the sensor
        in a standard environment (e.g. outside in fresh air) at around 400 ppm.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("BC")

    def triggetBaselineCalibration(self):
        return self.triggerBaselineCalibration()

    def triggerZeroCalibration(self):
        """
        Triggers a zero calibration of the sensor on carbon dioxide-free air.
        It is normally not necessary to manually calibrate the sensor, because
        the built-in automatic baseline calibration procedure will automatically
        fix any long-term drift based on the lowest level of CO2 observed over the
        automatic calibration period. However, if you disable automatic baseline
        calibration, you may want to manually trigger a calibration from time to
        time. Before starting a zero calibration, you should circulate carbon
        dioxide-free air within the sensor for a minute or two, using a small pipe
        connected to the sensor. Please contact support@yoctopuce.com for more details
        on the zero calibration procedure.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("ZC")

    def triggetZeroCalibration(self):
        return self.triggerZeroCalibration()

    def nextCarbonDioxide(self):
        """
        Continues the enumeration of CO2 sensors started using yFirstCarbonDioxide().
        Caution: You can't make any assumption about the returned CO2 sensors order.
        If you want to find a specific a CO2 sensor, use CarbonDioxide.findCarbonDioxide()
        and a hardwareID or a logical name.

        @return a pointer to a YCarbonDioxide object, corresponding to
                a CO2 sensor currently online, or a None pointer
                if there are no more CO2 sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YCarbonDioxide.FindCarbonDioxide(hwidRef.value)

#--- (end of YCarbonDioxide implementation)

#--- (YCarbonDioxide functions)

    @staticmethod
    def FirstCarbonDioxide():
        """
        Starts the enumeration of CO2 sensors currently accessible.
        Use the method YCarbonDioxide.nextCarbonDioxide() to iterate on
        next CO2 sensors.

        @return a pointer to a YCarbonDioxide object, corresponding to
                the first CO2 sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("CarbonDioxide", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YCarbonDioxide.FindCarbonDioxide(serialRef.value + "." + funcIdRef.value)

#--- (end of YCarbonDioxide functions)
