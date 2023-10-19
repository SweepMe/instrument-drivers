# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_genericsensor.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindGenericSensor(), the high-level API for GenericSensor functions
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


#--- (YGenericSensor class start)
#noinspection PyProtectedMember
class YGenericSensor(YSensor):
    """
    The YGenericSensor class allows you to read and configure Yoctopuce signal
    transducers. It inherits from YSensor class the core functions to read measurements,
    to register callback functions, to access the autonomous datalogger.
    This class adds the ability to configure the automatic conversion between the
    measured signal and the corresponding engineering unit.

    """
    #--- (end of YGenericSensor class start)
    #--- (YGenericSensor return codes)
    #--- (end of YGenericSensor return codes)
    #--- (YGenericSensor dlldef)
    #--- (end of YGenericSensor dlldef)
    #--- (YGenericSensor yapiwrapper)
    #--- (end of YGenericSensor yapiwrapper)
    #--- (YGenericSensor definitions)
    SIGNALVALUE_INVALID = YAPI.INVALID_DOUBLE
    SIGNALUNIT_INVALID = YAPI.INVALID_STRING
    SIGNALRANGE_INVALID = YAPI.INVALID_STRING
    VALUERANGE_INVALID = YAPI.INVALID_STRING
    SIGNALBIAS_INVALID = YAPI.INVALID_DOUBLE
    SIGNALSAMPLING_HIGH_RATE = 0
    SIGNALSAMPLING_HIGH_RATE_FILTERED = 1
    SIGNALSAMPLING_LOW_NOISE = 2
    SIGNALSAMPLING_LOW_NOISE_FILTERED = 3
    SIGNALSAMPLING_HIGHEST_RATE = 4
    SIGNALSAMPLING_INVALID = -1
    ENABLED_FALSE = 0
    ENABLED_TRUE = 1
    ENABLED_INVALID = -1
    #--- (end of YGenericSensor definitions)

    def __init__(self, func):
        super(YGenericSensor, self).__init__(func)
        self._className = 'GenericSensor'
        #--- (YGenericSensor attributes)
        self._callback = None
        self._signalValue = YGenericSensor.SIGNALVALUE_INVALID
        self._signalUnit = YGenericSensor.SIGNALUNIT_INVALID
        self._signalRange = YGenericSensor.SIGNALRANGE_INVALID
        self._valueRange = YGenericSensor.VALUERANGE_INVALID
        self._signalBias = YGenericSensor.SIGNALBIAS_INVALID
        self._signalSampling = YGenericSensor.SIGNALSAMPLING_INVALID
        self._enabled = YGenericSensor.ENABLED_INVALID
        #--- (end of YGenericSensor attributes)

    #--- (YGenericSensor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("signalValue"):
            self._signalValue = round(json_val.getDouble("signalValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("signalUnit"):
            self._signalUnit = json_val.getString("signalUnit")
        if json_val.has("signalRange"):
            self._signalRange = json_val.getString("signalRange")
        if json_val.has("valueRange"):
            self._valueRange = json_val.getString("valueRange")
        if json_val.has("signalBias"):
            self._signalBias = round(json_val.getDouble("signalBias") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("signalSampling"):
            self._signalSampling = json_val.getInt("signalSampling")
        if json_val.has("enabled"):
            self._enabled = (json_val.getInt("enabled") > 0 if 1 else 0)
        super(YGenericSensor, self)._parseAttr(json_val)

    def set_unit(self, newval):
        """
        Changes the measuring unit for the measured value.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the measuring unit for the measured value

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("unit", rest_val)

    def get_signalValue(self):
        """
        Returns the current value of the electrical signal measured by the sensor.

        @return a floating point number corresponding to the current value of the electrical signal
        measured by the sensor

        On failure, throws an exception or returns YGenericSensor.SIGNALVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.SIGNALVALUE_INVALID
        res = round(self._signalValue * 1000) / 1000
        return res

    def get_signalUnit(self):
        """
        Returns the measuring unit of the electrical signal used by the sensor.

        @return a string corresponding to the measuring unit of the electrical signal used by the sensor

        On failure, throws an exception or returns YGenericSensor.SIGNALUNIT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.SIGNALUNIT_INVALID
        res = self._signalUnit
        return res

    def get_signalRange(self):
        """
        Returns the input signal range used by the sensor.

        @return a string corresponding to the input signal range used by the sensor

        On failure, throws an exception or returns YGenericSensor.SIGNALRANGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.SIGNALRANGE_INVALID
        res = self._signalRange
        return res

    def set_signalRange(self, newval):
        """
        Changes the input signal range used by the sensor.
        When the input signal gets out of the planned range, the output value
        will be set to an arbitrary large value, whose sign indicates the direction
        of the range overrun.

        For a 4-20mA sensor, the default input signal range is "4...20".
        For a 0-10V sensor, the default input signal range is "0.1...10".
        For numeric communication interfaces, the default input signal range is
        "-999999.999...999999.999".

        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the input signal range used by the sensor

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("signalRange", rest_val)

    def get_valueRange(self):
        """
        Returns the physical value range measured by the sensor.

        @return a string corresponding to the physical value range measured by the sensor

        On failure, throws an exception or returns YGenericSensor.VALUERANGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.VALUERANGE_INVALID
        res = self._valueRange
        return res

    def set_valueRange(self, newval):
        """
        Changes the output value range, corresponding to the physical value measured
        by the sensor. The default output value range is the same as the input signal
        range (1:1 mapping), but you can change it so that the function automatically
        computes the physical value encoded by the input signal. Be aware that, as a
        side effect, the range modification may automatically modify the display resolution.

        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a string corresponding to the output value range, corresponding to the physical value measured
                by the sensor

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("valueRange", rest_val)

    def set_signalBias(self, newval):
        """
        Changes the electric signal bias for zero shift adjustment.
        If your electric signal reads positive when it should be zero, setup
        a positive signalBias of the same value to fix the zero shift.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a floating point number corresponding to the electric signal bias for zero shift adjustment

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("signalBias", rest_val)

    def get_signalBias(self):
        """
        Returns the electric signal bias for zero shift adjustment.
        A positive bias means that the signal is over-reporting the measure,
        while a negative bias means that the signal is under-reporting the measure.

        @return a floating point number corresponding to the electric signal bias for zero shift adjustment

        On failure, throws an exception or returns YGenericSensor.SIGNALBIAS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.SIGNALBIAS_INVALID
        res = self._signalBias
        return res

    def get_signalSampling(self):
        """
        Returns the electric signal sampling method to use.
        The HIGH_RATE method uses the highest sampling frequency, without any filtering.
        The HIGH_RATE_FILTERED method adds a windowed 7-sample median filter.
        The LOW_NOISE method uses a reduced acquisition frequency to reduce noise.
        The LOW_NOISE_FILTERED method combines a reduced frequency with the median filter
        to get measures as stable as possible when working on a noisy signal.

        @return a value among YGenericSensor.SIGNALSAMPLING_HIGH_RATE,
        YGenericSensor.SIGNALSAMPLING_HIGH_RATE_FILTERED, YGenericSensor.SIGNALSAMPLING_LOW_NOISE,
        YGenericSensor.SIGNALSAMPLING_LOW_NOISE_FILTERED and YGenericSensor.SIGNALSAMPLING_HIGHEST_RATE
        corresponding to the electric signal sampling method to use

        On failure, throws an exception or returns YGenericSensor.SIGNALSAMPLING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.SIGNALSAMPLING_INVALID
        res = self._signalSampling
        return res

    def set_signalSampling(self, newval):
        """
        Changes the electric signal sampling method to use.
        The HIGH_RATE method uses the highest sampling frequency, without any filtering.
        The HIGH_RATE_FILTERED method adds a windowed 7-sample median filter.
        The LOW_NOISE method uses a reduced acquisition frequency to reduce noise.
        The LOW_NOISE_FILTERED method combines a reduced frequency with the median filter
        to get measures as stable as possible when working on a noisy signal.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a value among YGenericSensor.SIGNALSAMPLING_HIGH_RATE,
        YGenericSensor.SIGNALSAMPLING_HIGH_RATE_FILTERED, YGenericSensor.SIGNALSAMPLING_LOW_NOISE,
        YGenericSensor.SIGNALSAMPLING_LOW_NOISE_FILTERED and YGenericSensor.SIGNALSAMPLING_HIGHEST_RATE
        corresponding to the electric signal sampling method to use

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("signalSampling", rest_val)

    def get_enabled(self):
        """
        Returns the activation state of this input.

        @return either YGenericSensor.ENABLED_FALSE or YGenericSensor.ENABLED_TRUE, according to the
        activation state of this input

        On failure, throws an exception or returns YGenericSensor.ENABLED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGenericSensor.ENABLED_INVALID
        res = self._enabled
        return res

    def set_enabled(self, newval):
        """
        Changes the activation state of this input. When an input is disabled,
        its value is no more updated. On some devices, disabling an input can
        improve the refresh rate of the other active inputs.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : either YGenericSensor.ENABLED_FALSE or YGenericSensor.ENABLED_TRUE, according to
        the activation state of this input

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabled", rest_val)

    @staticmethod
    def FindGenericSensor(func):
        """
        Retrieves a generic sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the generic sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YGenericSensor.isOnline() to test if the generic sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a generic sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the generic sensor, for instance
                RX010V01.genericSensor1.

        @return a YGenericSensor object allowing you to drive the generic sensor.
        """
        # obj
        obj = YFunction._FindFromCache("GenericSensor", func)
        if obj is None:
            obj = YGenericSensor(func)
            YFunction._AddToCache("GenericSensor", func, obj)
        return obj

    def zeroAdjust(self):
        """
        Adjusts the signal bias so that the current signal value is need
        precisely as zero. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # currSignal
        # currBias
        currSignal = self.get_signalValue()
        currBias = self.get_signalBias()
        return self.set_signalBias(currSignal + currBias)

    def nextGenericSensor(self):
        """
        Continues the enumeration of generic sensors started using yFirstGenericSensor().
        Caution: You can't make any assumption about the returned generic sensors order.
        If you want to find a specific a generic sensor, use GenericSensor.findGenericSensor()
        and a hardwareID or a logical name.

        @return a pointer to a YGenericSensor object, corresponding to
                a generic sensor currently online, or a None pointer
                if there are no more generic sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YGenericSensor.FindGenericSensor(hwidRef.value)

#--- (end of YGenericSensor implementation)

#--- (YGenericSensor functions)

    @staticmethod
    def FirstGenericSensor():
        """
        Starts the enumeration of generic sensors currently accessible.
        Use the method YGenericSensor.nextGenericSensor() to iterate on
        next generic sensors.

        @return a pointer to a YGenericSensor object, corresponding to
                the first generic sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("GenericSensor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YGenericSensor.FindGenericSensor(serialRef.value + "." + funcIdRef.value)

#--- (end of YGenericSensor functions)
