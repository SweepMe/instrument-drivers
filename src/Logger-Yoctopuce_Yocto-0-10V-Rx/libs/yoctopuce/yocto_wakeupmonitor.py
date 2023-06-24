# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_wakeupmonitor.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindWakeUpMonitor(), the high-level API for WakeUpMonitor functions
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


#--- (YWakeUpMonitor class start)
#noinspection PyProtectedMember
class YWakeUpMonitor(YFunction):
    """
    The YWakeUpMonitor class handles globally all wake-up sources, as well
    as automated sleep mode.

    """
    #--- (end of YWakeUpMonitor class start)
    #--- (YWakeUpMonitor return codes)
    #--- (end of YWakeUpMonitor return codes)
    #--- (YWakeUpMonitor dlldef)
    #--- (end of YWakeUpMonitor dlldef)
    #--- (YWakeUpMonitor yapiwrapper)
    #--- (end of YWakeUpMonitor yapiwrapper)
    #--- (YWakeUpMonitor definitions)
    POWERDURATION_INVALID = YAPI.INVALID_UINT
    SLEEPCOUNTDOWN_INVALID = YAPI.INVALID_UINT
    NEXTWAKEUP_INVALID = YAPI.INVALID_LONG
    RTCTIME_INVALID = YAPI.INVALID_LONG
    WAKEUPREASON_USBPOWER = 0
    WAKEUPREASON_EXTPOWER = 1
    WAKEUPREASON_ENDOFSLEEP = 2
    WAKEUPREASON_EXTSIG1 = 3
    WAKEUPREASON_SCHEDULE1 = 4
    WAKEUPREASON_SCHEDULE2 = 5
    WAKEUPREASON_INVALID = -1
    WAKEUPSTATE_SLEEPING = 0
    WAKEUPSTATE_AWAKE = 1
    WAKEUPSTATE_INVALID = -1
    #--- (end of YWakeUpMonitor definitions)

    def __init__(self, func):
        super(YWakeUpMonitor, self).__init__(func)
        self._className = 'WakeUpMonitor'
        #--- (YWakeUpMonitor attributes)
        self._callback = None
        self._powerDuration = YWakeUpMonitor.POWERDURATION_INVALID
        self._sleepCountdown = YWakeUpMonitor.SLEEPCOUNTDOWN_INVALID
        self._nextWakeUp = YWakeUpMonitor.NEXTWAKEUP_INVALID
        self._wakeUpReason = YWakeUpMonitor.WAKEUPREASON_INVALID
        self._wakeUpState = YWakeUpMonitor.WAKEUPSTATE_INVALID
        self._rtcTime = YWakeUpMonitor.RTCTIME_INVALID
        self._endOfTime = 2145960000
        #--- (end of YWakeUpMonitor attributes)

    #--- (YWakeUpMonitor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("powerDuration"):
            self._powerDuration = json_val.getInt("powerDuration")
        if json_val.has("sleepCountdown"):
            self._sleepCountdown = json_val.getInt("sleepCountdown")
        if json_val.has("nextWakeUp"):
            self._nextWakeUp = json_val.getLong("nextWakeUp")
        if json_val.has("wakeUpReason"):
            self._wakeUpReason = json_val.getInt("wakeUpReason")
        if json_val.has("wakeUpState"):
            self._wakeUpState = json_val.getInt("wakeUpState")
        if json_val.has("rtcTime"):
            self._rtcTime = json_val.getLong("rtcTime")
        super(YWakeUpMonitor, self)._parseAttr(json_val)

    def get_powerDuration(self):
        """
        Returns the maximal wake up time (in seconds) before automatically going to sleep.

        @return an integer corresponding to the maximal wake up time (in seconds) before automatically going to sleep

        On failure, throws an exception or returns YWakeUpMonitor.POWERDURATION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.POWERDURATION_INVALID
        res = self._powerDuration
        return res

    def set_powerDuration(self, newval):
        """
        Changes the maximal wake up time (seconds) before automatically going to sleep.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the maximal wake up time (seconds) before automatically
        going to sleep

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("powerDuration", rest_val)

    def get_sleepCountdown(self):
        """
        Returns the delay before the  next sleep period.

        @return an integer corresponding to the delay before the  next sleep period

        On failure, throws an exception or returns YWakeUpMonitor.SLEEPCOUNTDOWN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.SLEEPCOUNTDOWN_INVALID
        res = self._sleepCountdown
        return res

    def set_sleepCountdown(self, newval):
        """
        Changes the delay before the next sleep period.

        @param newval : an integer corresponding to the delay before the next sleep period

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("sleepCountdown", rest_val)

    def get_nextWakeUp(self):
        """
        Returns the next scheduled wake up date/time (UNIX format).

        @return an integer corresponding to the next scheduled wake up date/time (UNIX format)

        On failure, throws an exception or returns YWakeUpMonitor.NEXTWAKEUP_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.NEXTWAKEUP_INVALID
        res = self._nextWakeUp
        return res

    def set_nextWakeUp(self, newval):
        """
        Changes the days of the week when a wake up must take place.

        @param newval : an integer corresponding to the days of the week when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("nextWakeUp", rest_val)

    def get_wakeUpReason(self):
        """
        Returns the latest wake up reason.

        @return a value among YWakeUpMonitor.WAKEUPREASON_USBPOWER, YWakeUpMonitor.WAKEUPREASON_EXTPOWER,
        YWakeUpMonitor.WAKEUPREASON_ENDOFSLEEP, YWakeUpMonitor.WAKEUPREASON_EXTSIG1,
        YWakeUpMonitor.WAKEUPREASON_SCHEDULE1 and YWakeUpMonitor.WAKEUPREASON_SCHEDULE2 corresponding to
        the latest wake up reason

        On failure, throws an exception or returns YWakeUpMonitor.WAKEUPREASON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.WAKEUPREASON_INVALID
        res = self._wakeUpReason
        return res

    def get_wakeUpState(self):
        """
        Returns  the current state of the monitor.

        @return either YWakeUpMonitor.WAKEUPSTATE_SLEEPING or YWakeUpMonitor.WAKEUPSTATE_AWAKE, according
        to  the current state of the monitor

        On failure, throws an exception or returns YWakeUpMonitor.WAKEUPSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.WAKEUPSTATE_INVALID
        res = self._wakeUpState
        return res

    def set_wakeUpState(self, newval):
        rest_val = str(newval)
        return self._setAttr("wakeUpState", rest_val)

    def get_rtcTime(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpMonitor.RTCTIME_INVALID
        res = self._rtcTime
        return res

    @staticmethod
    def FindWakeUpMonitor(func):
        """
        Retrieves a wake-up monitor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the wake-up monitor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWakeUpMonitor.isOnline() to test if the wake-up monitor is
        indeed online at a given time. In case of ambiguity when looking for
        a wake-up monitor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the wake-up monitor, for instance
                YHUBGSM3.wakeUpMonitor.

        @return a YWakeUpMonitor object allowing you to drive the wake-up monitor.
        """
        # obj
        obj = YFunction._FindFromCache("WakeUpMonitor", func)
        if obj is None:
            obj = YWakeUpMonitor(func)
            YFunction._AddToCache("WakeUpMonitor", func, obj)
        return obj

    def wakeUp(self):
        """
        Forces a wake up.
        """
        return self.set_wakeUpState(YWakeUpMonitor.WAKEUPSTATE_AWAKE)

    def sleep(self, secBeforeSleep):
        """
        Goes to sleep until the next wake up condition is met,  the
        RTC time must have been set before calling this function.

        @param secBeforeSleep : number of seconds before going into sleep mode,

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # currTime
        currTime = self.get_rtcTime()
        if not (currTime != 0):
            self._throw(YAPI.RTC_NOT_READY, "RTC time not set")
            return YAPI.RTC_NOT_READY
        self.set_nextWakeUp(self._endOfTime)
        self.set_sleepCountdown(secBeforeSleep)
        return YAPI.SUCCESS

    def sleepFor(self, secUntilWakeUp, secBeforeSleep):
        """
        Goes to sleep for a specific duration or until the next wake up condition is met, the
        RTC time must have been set before calling this function. The count down before sleep
        can be canceled with resetSleepCountDown.

        @param secUntilWakeUp : number of seconds before next wake up
        @param secBeforeSleep : number of seconds before going into sleep mode

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # currTime
        currTime = self.get_rtcTime()
        if not (currTime != 0):
            self._throw(YAPI.RTC_NOT_READY, "RTC time not set")
            return YAPI.RTC_NOT_READY
        self.set_nextWakeUp(currTime+secUntilWakeUp)
        self.set_sleepCountdown(secBeforeSleep)
        return YAPI.SUCCESS

    def sleepUntil(self, wakeUpTime, secBeforeSleep):
        """
        Go to sleep until a specific date is reached or until the next wake up condition is met, the
        RTC time must have been set before calling this function. The count down before sleep
        can be canceled with resetSleepCountDown.

        @param wakeUpTime : wake-up datetime (UNIX format)
        @param secBeforeSleep : number of seconds before going into sleep mode

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # currTime
        currTime = self.get_rtcTime()
        if not (currTime != 0):
            self._throw(YAPI.RTC_NOT_READY, "RTC time not set")
            return YAPI.RTC_NOT_READY
        self.set_nextWakeUp(wakeUpTime)
        self.set_sleepCountdown(secBeforeSleep)
        return YAPI.SUCCESS

    def resetSleepCountDown(self):
        """
        Resets the sleep countdown.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        self.set_sleepCountdown(0)
        self.set_nextWakeUp(0)
        return YAPI.SUCCESS

    def nextWakeUpMonitor(self):
        """
        Continues the enumeration of wake-up monitors started using yFirstWakeUpMonitor().
        Caution: You can't make any assumption about the returned wake-up monitors order.
        If you want to find a specific a wake-up monitor, use WakeUpMonitor.findWakeUpMonitor()
        and a hardwareID or a logical name.

        @return a pointer to a YWakeUpMonitor object, corresponding to
                a wake-up monitor currently online, or a None pointer
                if there are no more wake-up monitors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YWakeUpMonitor.FindWakeUpMonitor(hwidRef.value)

#--- (end of YWakeUpMonitor implementation)

#--- (YWakeUpMonitor functions)

    @staticmethod
    def FirstWakeUpMonitor():
        """
        Starts the enumeration of wake-up monitors currently accessible.
        Use the method YWakeUpMonitor.nextWakeUpMonitor() to iterate on
        next wake-up monitors.

        @return a pointer to a YWakeUpMonitor object, corresponding to
                the first wake-up monitor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("WakeUpMonitor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YWakeUpMonitor.FindWakeUpMonitor(serialRef.value + "." + funcIdRef.value)

#--- (end of YWakeUpMonitor functions)
