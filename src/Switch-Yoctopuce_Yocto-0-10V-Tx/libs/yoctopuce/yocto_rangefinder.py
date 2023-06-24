# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_rangefinder.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindRangeFinder(), the high-level API for RangeFinder functions
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


#--- (YRangeFinder class start)
#noinspection PyProtectedMember
class YRangeFinder(YSensor):
    """
    The YRangeFinder class allows you to read and configure Yoctopuce range finders.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the ability to easily perform a one-point linear calibration
    to compensate the effect of a glass or filter placed in front of the sensor.

    """
    #--- (end of YRangeFinder class start)
    #--- (YRangeFinder return codes)
    #--- (end of YRangeFinder return codes)
    #--- (YRangeFinder dlldef)
    #--- (end of YRangeFinder dlldef)
    #--- (YRangeFinder yapiwrapper)
    #--- (end of YRangeFinder yapiwrapper)
    #--- (YRangeFinder definitions)
    TIMEFRAME_INVALID = YAPI.INVALID_LONG
    QUALITY_INVALID = YAPI.INVALID_UINT
    HARDWARECALIBRATION_INVALID = YAPI.INVALID_STRING
    CURRENTTEMPERATURE_INVALID = YAPI.INVALID_DOUBLE
    COMMAND_INVALID = YAPI.INVALID_STRING
    RANGEFINDERMODE_DEFAULT = 0
    RANGEFINDERMODE_LONG_RANGE = 1
    RANGEFINDERMODE_HIGH_ACCURACY = 2
    RANGEFINDERMODE_HIGH_SPEED = 3
    RANGEFINDERMODE_INVALID = -1
    #--- (end of YRangeFinder definitions)

    def __init__(self, func):
        super(YRangeFinder, self).__init__(func)
        self._className = 'RangeFinder'
        #--- (YRangeFinder attributes)
        self._callback = None
        self._rangeFinderMode = YRangeFinder.RANGEFINDERMODE_INVALID
        self._timeFrame = YRangeFinder.TIMEFRAME_INVALID
        self._quality = YRangeFinder.QUALITY_INVALID
        self._hardwareCalibration = YRangeFinder.HARDWARECALIBRATION_INVALID
        self._currentTemperature = YRangeFinder.CURRENTTEMPERATURE_INVALID
        self._command = YRangeFinder.COMMAND_INVALID
        #--- (end of YRangeFinder attributes)

    #--- (YRangeFinder implementation)
    def _parseAttr(self, json_val):
        if json_val.has("rangeFinderMode"):
            self._rangeFinderMode = json_val.getInt("rangeFinderMode")
        if json_val.has("timeFrame"):
            self._timeFrame = json_val.getLong("timeFrame")
        if json_val.has("quality"):
            self._quality = json_val.getInt("quality")
        if json_val.has("hardwareCalibration"):
            self._hardwareCalibration = json_val.getString("hardwareCalibration")
        if json_val.has("currentTemperature"):
            self._currentTemperature = round(json_val.getDouble("currentTemperature") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YRangeFinder, self)._parseAttr(json_val)

    def set_unit(self, newval):
        """
        Changes the measuring unit for the measured range. That unit is a string.
        String value can be " or mm. Any other value is ignored.
        Remember to call the saveToFlash() method of the module if the modification must be kept.
        WARNING: if a specific calibration is defined for the rangeFinder function, a
        unit system change will probably break it.

        @param newval : a string corresponding to the measuring unit for the measured range

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("unit", rest_val)

    def get_rangeFinderMode(self):
        """
        Returns the range finder running mode. The rangefinder running mode
        allows you to put priority on precision, speed or maximum range.

        @return a value among YRangeFinder.RANGEFINDERMODE_DEFAULT, YRangeFinder.RANGEFINDERMODE_LONG_RANGE,
        YRangeFinder.RANGEFINDERMODE_HIGH_ACCURACY and YRangeFinder.RANGEFINDERMODE_HIGH_SPEED
        corresponding to the range finder running mode

        On failure, throws an exception or returns YRangeFinder.RANGEFINDERMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.RANGEFINDERMODE_INVALID
        res = self._rangeFinderMode
        return res

    def set_rangeFinderMode(self, newval):
        """
        Changes the rangefinder running mode, allowing you to put priority on
        precision, speed or maximum range.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a value among YRangeFinder.RANGEFINDERMODE_DEFAULT,
        YRangeFinder.RANGEFINDERMODE_LONG_RANGE, YRangeFinder.RANGEFINDERMODE_HIGH_ACCURACY and
        YRangeFinder.RANGEFINDERMODE_HIGH_SPEED corresponding to the rangefinder running mode, allowing you
        to put priority on
                precision, speed or maximum range

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("rangeFinderMode", rest_val)

    def get_timeFrame(self):
        """
        Returns the time frame used to measure the distance and estimate the measure
        reliability. The time frame is expressed in milliseconds.

        @return an integer corresponding to the time frame used to measure the distance and estimate the measure
                reliability

        On failure, throws an exception or returns YRangeFinder.TIMEFRAME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.TIMEFRAME_INVALID
        res = self._timeFrame
        return res

    def set_timeFrame(self, newval):
        """
        Changes the time frame used to measure the distance and estimate the measure
        reliability. The time frame is expressed in milliseconds. A larger timeframe
        improves stability and reliability, at the cost of higher latency, but prevents
        the detection of events shorter than the time frame.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the time frame used to measure the distance and estimate the measure
                reliability

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("timeFrame", rest_val)

    def get_quality(self):
        """
        Returns a measure quality estimate, based on measured dispersion.

        @return an integer corresponding to a measure quality estimate, based on measured dispersion

        On failure, throws an exception or returns YRangeFinder.QUALITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.QUALITY_INVALID
        res = self._quality
        return res

    def get_hardwareCalibration(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.HARDWARECALIBRATION_INVALID
        res = self._hardwareCalibration
        return res

    def set_hardwareCalibration(self, newval):
        rest_val = newval
        return self._setAttr("hardwareCalibration", rest_val)

    def get_currentTemperature(self):
        """
        Returns the current sensor temperature, as a floating point number.

        @return a floating point number corresponding to the current sensor temperature, as a floating point number

        On failure, throws an exception or returns YRangeFinder.CURRENTTEMPERATURE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.CURRENTTEMPERATURE_INVALID
        res = self._currentTemperature
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRangeFinder.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindRangeFinder(func):
        """
        Retrieves a range finder for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the range finder is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YRangeFinder.isOnline() to test if the range finder is
        indeed online at a given time. In case of ambiguity when looking for
        a range finder by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the range finder, for instance
                YRNGFND1.rangeFinder1.

        @return a YRangeFinder object allowing you to drive the range finder.
        """
        # obj
        obj = YFunction._FindFromCache("RangeFinder", func)
        if obj is None:
            obj = YRangeFinder(func)
            YFunction._AddToCache("RangeFinder", func, obj)
        return obj

    def get_hardwareCalibrationTemperature(self):
        """
        Returns the temperature at the time when the latest calibration was performed.
        This function can be used to determine if a new calibration for ambient temperature
        is required.

        @return a temperature, as a floating point number.
                On failure, throws an exception or return YAPI.INVALID_DOUBLE.
        """
        # hwcal
        hwcal = self.get_hardwareCalibration()
        if not ((hwcal)[0: 0 + 1] == "@"):
            return YAPI.INVALID_DOUBLE
        return YAPI._atoi((hwcal)[1: 1 + len(hwcal)])

    def triggerTemperatureCalibration(self):
        """
        Triggers a sensor calibration according to the current ambient temperature. That
        calibration process needs no physical interaction with the sensor. It is performed
        automatically at device startup, but it is recommended to start it again when the
        temperature delta since the latest calibration exceeds 8°C.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("T")

    def triggerSpadCalibration(self):
        """
        Triggers the photon detector hardware calibration.
        This function is part of the calibration procedure to compensate for the the effect
        of a cover glass. Make sure to read the chapter about hardware calibration for details
        on the calibration procedure for proper results.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("S")

    def triggerOffsetCalibration(self, targetDist):
        """
        Triggers the hardware offset calibration of the distance sensor.
        This function is part of the calibration procedure to compensate for the the effect
        of a cover glass. Make sure to read the chapter about hardware calibration for details
        on the calibration procedure for proper results.

        @param targetDist : true distance of the calibration target, in mm or inches, depending
                on the unit selected in the device

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # distmm
        if self.get_unit() == "\"":
            distmm = int(round(targetDist * 25.4))
        else:
            distmm = int(round(targetDist))
        return self.set_command("O" + str(int(distmm)))

    def triggerXTalkCalibration(self, targetDist):
        """
        Triggers the hardware cross-talk calibration of the distance sensor.
        This function is part of the calibration procedure to compensate for the the effect
        of a cover glass. Make sure to read the chapter about hardware calibration for details
        on the calibration procedure for proper results.

        @param targetDist : true distance of the calibration target, in mm or inches, depending
                on the unit selected in the device

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # distmm
        if self.get_unit() == "\"":
            distmm = int(round(targetDist * 25.4))
        else:
            distmm = int(round(targetDist))
        return self.set_command("X" + str(int(distmm)))

    def cancelCoverGlassCalibrations(self):
        """
        Cancels the effect of previous hardware calibration procedures to compensate
        for cover glass, and restores factory settings.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_hardwareCalibration("")

    def nextRangeFinder(self):
        """
        Continues the enumeration of range finders started using yFirstRangeFinder().
        Caution: You can't make any assumption about the returned range finders order.
        If you want to find a specific a range finder, use RangeFinder.findRangeFinder()
        and a hardwareID or a logical name.

        @return a pointer to a YRangeFinder object, corresponding to
                a range finder currently online, or a None pointer
                if there are no more range finders to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YRangeFinder.FindRangeFinder(hwidRef.value)

#--- (end of YRangeFinder implementation)

#--- (YRangeFinder functions)

    @staticmethod
    def FirstRangeFinder():
        """
        Starts the enumeration of range finders currently accessible.
        Use the method YRangeFinder.nextRangeFinder() to iterate on
        next range finders.

        @return a pointer to a YRangeFinder object, corresponding to
                the first range finder currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("RangeFinder", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YRangeFinder.FindRangeFinder(serialRef.value + "." + funcIdRef.value)

#--- (end of YRangeFinder functions)
