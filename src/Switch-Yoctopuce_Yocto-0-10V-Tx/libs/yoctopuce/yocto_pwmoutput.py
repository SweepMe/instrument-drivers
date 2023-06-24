# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_pwmoutput.py 38913 2019-12-20 18:59:49Z mvuilleu $
#
#  Implements yFindPwmOutput(), the high-level API for PwmOutput functions
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


#--- (YPwmOutput class start)
#noinspection PyProtectedMember
class YPwmOutput(YFunction):
    """
    The YPwmOutput class allows you to drive a pulse-width modulated output (PWM).
    You can configure the frequency as well as the duty cycle, and setup progressive
    transitions.

    """
    #--- (end of YPwmOutput class start)
    #--- (YPwmOutput return codes)
    #--- (end of YPwmOutput return codes)
    #--- (YPwmOutput dlldef)
    #--- (end of YPwmOutput dlldef)
    #--- (YPwmOutput yapiwrapper)
    #--- (end of YPwmOutput yapiwrapper)
    #--- (YPwmOutput definitions)
    FREQUENCY_INVALID = YAPI.INVALID_DOUBLE
    PERIOD_INVALID = YAPI.INVALID_DOUBLE
    DUTYCYCLE_INVALID = YAPI.INVALID_DOUBLE
    PULSEDURATION_INVALID = YAPI.INVALID_DOUBLE
    PWMTRANSITION_INVALID = YAPI.INVALID_STRING
    DUTYCYCLEATPOWERON_INVALID = YAPI.INVALID_DOUBLE
    ENABLED_FALSE = 0
    ENABLED_TRUE = 1
    ENABLED_INVALID = -1
    ENABLEDATPOWERON_FALSE = 0
    ENABLEDATPOWERON_TRUE = 1
    ENABLEDATPOWERON_INVALID = -1
    #--- (end of YPwmOutput definitions)

    def __init__(self, func):
        super(YPwmOutput, self).__init__(func)
        self._className = 'PwmOutput'
        #--- (YPwmOutput attributes)
        self._callback = None
        self._enabled = YPwmOutput.ENABLED_INVALID
        self._frequency = YPwmOutput.FREQUENCY_INVALID
        self._period = YPwmOutput.PERIOD_INVALID
        self._dutyCycle = YPwmOutput.DUTYCYCLE_INVALID
        self._pulseDuration = YPwmOutput.PULSEDURATION_INVALID
        self._pwmTransition = YPwmOutput.PWMTRANSITION_INVALID
        self._enabledAtPowerOn = YPwmOutput.ENABLEDATPOWERON_INVALID
        self._dutyCycleAtPowerOn = YPwmOutput.DUTYCYCLEATPOWERON_INVALID
        #--- (end of YPwmOutput attributes)

    #--- (YPwmOutput implementation)
    def _parseAttr(self, json_val):
        if json_val.has("enabled"):
            self._enabled = (json_val.getInt("enabled") > 0 if 1 else 0)
        if json_val.has("frequency"):
            self._frequency = round(json_val.getDouble("frequency") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("period"):
            self._period = round(json_val.getDouble("period") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("dutyCycle"):
            self._dutyCycle = round(json_val.getDouble("dutyCycle") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("pulseDuration"):
            self._pulseDuration = round(json_val.getDouble("pulseDuration") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("pwmTransition"):
            self._pwmTransition = json_val.getString("pwmTransition")
        if json_val.has("enabledAtPowerOn"):
            self._enabledAtPowerOn = (json_val.getInt("enabledAtPowerOn") > 0 if 1 else 0)
        if json_val.has("dutyCycleAtPowerOn"):
            self._dutyCycleAtPowerOn = round(json_val.getDouble("dutyCycleAtPowerOn") * 1000.0 / 65536.0) / 1000.0
        super(YPwmOutput, self)._parseAttr(json_val)

    def get_enabled(self):
        """
        Returns the state of the PWM generators.

        @return either YPwmOutput.ENABLED_FALSE or YPwmOutput.ENABLED_TRUE, according to the state of the PWM generators

        On failure, throws an exception or returns YPwmOutput.ENABLED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.ENABLED_INVALID
        res = self._enabled
        return res

    def set_enabled(self, newval):
        """
        Stops or starts the PWM.

        @param newval : either YPwmOutput.ENABLED_FALSE or YPwmOutput.ENABLED_TRUE

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabled", rest_val)

    def set_frequency(self, newval):
        """
        Changes the PWM frequency. The duty cycle is kept unchanged thanks to an
        automatic pulse width change, in other words, the change will not be applied
        before the end of the current period. This can significantly affect reaction
        time at low frequencies. If you call the matching module saveToFlash()
        method, the frequency will be kept after a device power cycle.
        To stop the PWM signal, do not set the frequency to zero, use the set_enabled()
        method instead.

        @param newval : a floating point number corresponding to the PWM frequency

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("frequency", rest_val)

    def get_frequency(self):
        """
        Returns the PWM frequency in Hz.

        @return a floating point number corresponding to the PWM frequency in Hz

        On failure, throws an exception or returns YPwmOutput.FREQUENCY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.FREQUENCY_INVALID
        res = self._frequency
        return res

    def set_period(self, newval):
        """
        Changes the PWM period in milliseconds. Caution: in order to avoid  random truncation of
        the current pulse, the change will not be applied
        before the end of the current period. This can significantly affect reaction
        time at low frequencies. If you call the matching module saveToFlash()
        method, the frequency will be kept after a device power cycle.

        @param newval : a floating point number corresponding to the PWM period in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("period", rest_val)

    def get_period(self):
        """
        Returns the PWM period in milliseconds.

        @return a floating point number corresponding to the PWM period in milliseconds

        On failure, throws an exception or returns YPwmOutput.PERIOD_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.PERIOD_INVALID
        res = self._period
        return res

    def set_dutyCycle(self, newval):
        """
        Changes the PWM duty cycle, in per cents.

        @param newval : a floating point number corresponding to the PWM duty cycle, in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("dutyCycle", rest_val)

    def get_dutyCycle(self):
        """
        Returns the PWM duty cycle, in per cents.

        @return a floating point number corresponding to the PWM duty cycle, in per cents

        On failure, throws an exception or returns YPwmOutput.DUTYCYCLE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.DUTYCYCLE_INVALID
        res = self._dutyCycle
        return res

    def set_pulseDuration(self, newval):
        """
        Changes the PWM pulse length, in milliseconds. A pulse length cannot be longer than period,
        otherwise it is truncated.

        @param newval : a floating point number corresponding to the PWM pulse length, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("pulseDuration", rest_val)

    def get_pulseDuration(self):
        """
        Returns the PWM pulse length in milliseconds, as a floating point number.

        @return a floating point number corresponding to the PWM pulse length in milliseconds, as a
        floating point number

        On failure, throws an exception or returns YPwmOutput.PULSEDURATION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.PULSEDURATION_INVALID
        res = self._pulseDuration
        return res

    def get_pwmTransition(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.PWMTRANSITION_INVALID
        res = self._pwmTransition
        return res

    def set_pwmTransition(self, newval):
        rest_val = newval
        return self._setAttr("pwmTransition", rest_val)

    def get_enabledAtPowerOn(self):
        """
        Returns the state of the PWM at device power on.

        @return either YPwmOutput.ENABLEDATPOWERON_FALSE or YPwmOutput.ENABLEDATPOWERON_TRUE, according to
        the state of the PWM at device power on

        On failure, throws an exception or returns YPwmOutput.ENABLEDATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.ENABLEDATPOWERON_INVALID
        res = self._enabledAtPowerOn
        return res

    def set_enabledAtPowerOn(self, newval):
        """
        Changes the state of the PWM at device power on. Remember to call the matching module saveToFlash()
        method, otherwise this call will have no effect.

        @param newval : either YPwmOutput.ENABLEDATPOWERON_FALSE or YPwmOutput.ENABLEDATPOWERON_TRUE,
        according to the state of the PWM at device power on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabledAtPowerOn", rest_val)

    def set_dutyCycleAtPowerOn(self, newval):
        """
        Changes the PWM duty cycle at device power on. Remember to call the matching
        module saveToFlash() method, otherwise this call will have no effect.

        @param newval : a floating point number corresponding to the PWM duty cycle at device power on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("dutyCycleAtPowerOn", rest_val)

    def get_dutyCycleAtPowerOn(self):
        """
        Returns the PWM generators duty cycle at device power on as a floating point number between 0 and 100.

        @return a floating point number corresponding to the PWM generators duty cycle at device power on
        as a floating point number between 0 and 100

        On failure, throws an exception or returns YPwmOutput.DUTYCYCLEATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPwmOutput.DUTYCYCLEATPOWERON_INVALID
        res = self._dutyCycleAtPowerOn
        return res

    @staticmethod
    def FindPwmOutput(func):
        """
        Retrieves a PWM generator for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the PWM generator is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPwmOutput.isOnline() to test if the PWM generator is
        indeed online at a given time. In case of ambiguity when looking for
        a PWM generator by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the PWM generator, for instance
                YPWMTX01.pwmOutput1.

        @return a YPwmOutput object allowing you to drive the PWM generator.
        """
        # obj
        obj = YFunction._FindFromCache("PwmOutput", func)
        if obj is None:
            obj = YPwmOutput(func)
            YFunction._AddToCache("PwmOutput", func, obj)
        return obj

    def pulseDurationMove(self, ms_target, ms_duration):
        """
        Performs a smooth transition of the pulse duration toward a given value.
        Any period, frequency, duty cycle or pulse width change will cancel any ongoing transition process.

        @param ms_target   : new pulse duration at the end of the transition
                (floating-point number, representing the pulse duration in milliseconds)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if ms_target < 0.0:
            ms_target = 0.0
        newval = "" + str(int(round(ms_target*65536))) + "ms:" + str(int(ms_duration))
        return self.set_pwmTransition(newval)

    def dutyCycleMove(self, target, ms_duration):
        """
        Performs a smooth change of the duty cycle toward a given value.
        Any period, frequency, duty cycle or pulse width change will cancel any ongoing transition process.

        @param target      : new duty cycle at the end of the transition
                (percentage, floating-point number between 0 and 100)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if target < 0.0:
            target = 0.0
        if target > 100.0:
            target = 100.0
        newval = "" + str(int(round(target*65536))) + ":" + str(int(ms_duration))
        return self.set_pwmTransition(newval)

    def frequencyMove(self, target, ms_duration):
        """
        Performs a smooth frequency change toward a given value.
        Any period, frequency, duty cycle or pulse width change will cancel any ongoing transition process.

        @param target      : new frequency at the end of the transition (floating-point number)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if target < 0.001:
            target = 0.001
        newval = "" + str(target) + "Hz:" + str(int(ms_duration))
        return self.set_pwmTransition(newval)

    def phaseMove(self, target, ms_duration):
        """
        Performs a smooth transition toward a specified value of the phase shift between this channel
        and the other channel. The phase shift is executed by slightly changing the frequency
        temporarily during the specified duration. This function only makes sense when both channels
        are running, either at the same frequency, or at a multiple of the channel frequency.
        Any period, frequency, duty cycle or pulse width change will cancel any ongoing transition process.

        @param target      : phase shift at the end of the transition, in milliseconds (floating-point number)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        newval = "" + str(target) + "ps:" + str(int(ms_duration))
        return self.set_pwmTransition(newval)

    def triggerPulsesByDuration(self, ms_target, n_pulses):
        """
        Trigger a given number of pulses of specified duration, at current frequency.
        At the end of the pulse train, revert to the original state of the PWM generator.

        @param ms_target : desired pulse duration
                (floating-point number, representing the pulse duration in milliseconds)
        @param n_pulses  : desired pulse count

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if ms_target < 0.0:
            ms_target = 0.0
        newval = "" + str(int(round(ms_target*65536))) + "ms*" + str(int(n_pulses))
        return self.set_pwmTransition(newval)

    def triggerPulsesByDutyCycle(self, target, n_pulses):
        """
        Trigger a given number of pulses of specified duration, at current frequency.
        At the end of the pulse train, revert to the original state of the PWM generator.

        @param target   : desired duty cycle for the generated pulses
                (percentage, floating-point number between 0 and 100)
        @param n_pulses : desired pulse count

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if target < 0.0:
            target = 0.0
        if target > 100.0:
            target = 100.0
        newval = "" + str(int(round(target*65536))) + "*" + str(int(n_pulses))
        return self.set_pwmTransition(newval)

    def triggerPulsesByFrequency(self, target, n_pulses):
        """
        Trigger a given number of pulses at the specified frequency, using current duty cycle.
        At the end of the pulse train, revert to the original state of the PWM generator.

        @param target   : desired frequency for the generated pulses (floating-point number)
        @param n_pulses : desired pulse count

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # newval
        if target < 0.001:
            target = 0.001
        newval = "" + str(target) + "Hz*" + str(int(n_pulses))
        return self.set_pwmTransition(newval)

    def markForRepeat(self):
        return self.set_pwmTransition(":")

    def repeatFromMark(self):
        return self.set_pwmTransition("R")

    def nextPwmOutput(self):
        """
        Continues the enumeration of PWM generators started using yFirstPwmOutput().
        Caution: You can't make any assumption about the returned PWM generators order.
        If you want to find a specific a PWM generator, use PwmOutput.findPwmOutput()
        and a hardwareID or a logical name.

        @return a pointer to a YPwmOutput object, corresponding to
                a PWM generator currently online, or a None pointer
                if there are no more PWM generators to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YPwmOutput.FindPwmOutput(hwidRef.value)

#--- (end of YPwmOutput implementation)

#--- (YPwmOutput functions)

    @staticmethod
    def FirstPwmOutput():
        """
        Starts the enumeration of PWM generators currently accessible.
        Use the method YPwmOutput.nextPwmOutput() to iterate on
        next PWM generators.

        @return a pointer to a YPwmOutput object, corresponding to
                the first PWM generator currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("PwmOutput", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YPwmOutput.FindPwmOutput(serialRef.value + "." + funcIdRef.value)

#--- (end of YPwmOutput functions)
