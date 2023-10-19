# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_watchdog.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindWatchdog(), the high-level API for Watchdog functions
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


#--- (YWatchdog class start)
#noinspection PyProtectedMember
class YWatchdog(YFunction):
    """
    The YWatchdog class allows you to drive a Yoctopuce watchdog.
    A watchdog works like a relay, with an extra timer that can automatically
    trigger a brief power cycle to an appliance after a preset delay, to force this
    appliance to reset if a problem occurs. During normal use, the watchdog timer
    is reset periodically by the application to prevent the automated power cycle.
    Whenever the application dies, the watchdog will automatically trigger the power cycle.
    The watchdog can also be driven directly with pulse and delayedPulse
    methods to switch off an appliance for a given duration.

    """
    #--- (end of YWatchdog class start)
    #--- (YWatchdog return codes)
    #--- (end of YWatchdog return codes)
    #--- (YWatchdog dlldef)
    #--- (end of YWatchdog dlldef)
    #--- (YWatchdog yapiwrapper)
    #--- (end of YWatchdog yapiwrapper)
    #--- (YWatchdog definitions)
    MAXTIMEONSTATEA_INVALID = YAPI.INVALID_LONG
    MAXTIMEONSTATEB_INVALID = YAPI.INVALID_LONG
    PULSETIMER_INVALID = YAPI.INVALID_LONG
    DELAYEDPULSETIMER_INVALID = None
    COUNTDOWN_INVALID = YAPI.INVALID_LONG
    TRIGGERDELAY_INVALID = YAPI.INVALID_LONG
    TRIGGERDURATION_INVALID = YAPI.INVALID_LONG
    STATE_A = 0
    STATE_B = 1
    STATE_INVALID = -1
    STATEATPOWERON_UNCHANGED = 0
    STATEATPOWERON_A = 1
    STATEATPOWERON_B = 2
    STATEATPOWERON_INVALID = -1
    OUTPUT_OFF = 0
    OUTPUT_ON = 1
    OUTPUT_INVALID = -1
    AUTOSTART_OFF = 0
    AUTOSTART_ON = 1
    AUTOSTART_INVALID = -1
    RUNNING_OFF = 0
    RUNNING_ON = 1
    RUNNING_INVALID = -1
    #--- (end of YWatchdog definitions)

    def __init__(self, func):
        super(YWatchdog, self).__init__(func)
        self._className = 'Watchdog'
        #--- (YWatchdog attributes)
        self._callback = None
        self._state = YWatchdog.STATE_INVALID
        self._stateAtPowerOn = YWatchdog.STATEATPOWERON_INVALID
        self._maxTimeOnStateA = YWatchdog.MAXTIMEONSTATEA_INVALID
        self._maxTimeOnStateB = YWatchdog.MAXTIMEONSTATEB_INVALID
        self._output = YWatchdog.OUTPUT_INVALID
        self._pulseTimer = YWatchdog.PULSETIMER_INVALID
        self._delayedPulseTimer = YWatchdog.DELAYEDPULSETIMER_INVALID
        self._countdown = YWatchdog.COUNTDOWN_INVALID
        self._autoStart = YWatchdog.AUTOSTART_INVALID
        self._running = YWatchdog.RUNNING_INVALID
        self._triggerDelay = YWatchdog.TRIGGERDELAY_INVALID
        self._triggerDuration = YWatchdog.TRIGGERDURATION_INVALID
        self._firm = 0
        #--- (end of YWatchdog attributes)

    #--- (YWatchdog implementation)
    def _parseAttr(self, json_val):
        if json_val.has("state"):
            self._state = (json_val.getInt("state") > 0 if 1 else 0)
        if json_val.has("stateAtPowerOn"):
            self._stateAtPowerOn = json_val.getInt("stateAtPowerOn")
        if json_val.has("maxTimeOnStateA"):
            self._maxTimeOnStateA = json_val.getLong("maxTimeOnStateA")
        if json_val.has("maxTimeOnStateB"):
            self._maxTimeOnStateB = json_val.getLong("maxTimeOnStateB")
        if json_val.has("output"):
            self._output = (json_val.getInt("output") > 0 if 1 else 0)
        if json_val.has("pulseTimer"):
            self._pulseTimer = json_val.getLong("pulseTimer")
        if json_val.has("delayedPulseTimer"):
            subjson = json_val.getYJSONObject("delayedPulseTimer");
            self._delayedPulseTimer = {"moving": None, "target": None, "ms": None}
            if subjson.has("moving"):
                self._delayedPulseTimer["moving"] = subjson.getInt("moving")
            if subjson.has("target"):
                self._delayedPulseTimer["target"] = subjson.getInt("target")
            if subjson.has("ms"):
                self._delayedPulseTimer["ms"] = subjson.getInt("ms")
        if json_val.has("countdown"):
            self._countdown = json_val.getLong("countdown")
        if json_val.has("autoStart"):
            self._autoStart = (json_val.getInt("autoStart") > 0 if 1 else 0)
        if json_val.has("running"):
            self._running = (json_val.getInt("running") > 0 if 1 else 0)
        if json_val.has("triggerDelay"):
            self._triggerDelay = json_val.getLong("triggerDelay")
        if json_val.has("triggerDuration"):
            self._triggerDuration = json_val.getLong("triggerDuration")
        super(YWatchdog, self)._parseAttr(json_val)

    def get_state(self):
        """
        Returns the state of the watchdog (A for the idle position, B for the active position).

        @return either YWatchdog.STATE_A or YWatchdog.STATE_B, according to the state of the watchdog (A
        for the idle position, B for the active position)

        On failure, throws an exception or returns YWatchdog.STATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.STATE_INVALID
        res = self._state
        return res

    def set_state(self, newval):
        """
        Changes the state of the watchdog (A for the idle position, B for the active position).

        @param newval : either YWatchdog.STATE_A or YWatchdog.STATE_B, according to the state of the
        watchdog (A for the idle position, B for the active position)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("state", rest_val)

    def get_stateAtPowerOn(self):
        """
        Returns the state of the watchdog at device startup (A for the idle position,
        B for the active position, UNCHANGED to leave the relay state as is).

        @return a value among YWatchdog.STATEATPOWERON_UNCHANGED, YWatchdog.STATEATPOWERON_A and
        YWatchdog.STATEATPOWERON_B corresponding to the state of the watchdog at device startup (A for the
        idle position,
                B for the active position, UNCHANGED to leave the relay state as is)

        On failure, throws an exception or returns YWatchdog.STATEATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.STATEATPOWERON_INVALID
        res = self._stateAtPowerOn
        return res

    def set_stateAtPowerOn(self, newval):
        """
        Changes the state of the watchdog at device startup (A for the idle position,
        B for the active position, UNCHANGED to leave the relay state as is).
        Remember to call the matching module saveToFlash()
        method, otherwise this call will have no effect.

        @param newval : a value among YWatchdog.STATEATPOWERON_UNCHANGED, YWatchdog.STATEATPOWERON_A and
        YWatchdog.STATEATPOWERON_B corresponding to the state of the watchdog at device startup (A for the
        idle position,
                B for the active position, UNCHANGED to leave the relay state as is)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("stateAtPowerOn", rest_val)

    def get_maxTimeOnStateA(self):
        """
        Returns the maximum time (ms) allowed for the watchdog to stay in state
        A before automatically switching back in to B state. Zero means no time limit.

        @return an integer corresponding to the maximum time (ms) allowed for the watchdog to stay in state
                A before automatically switching back in to B state

        On failure, throws an exception or returns YWatchdog.MAXTIMEONSTATEA_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.MAXTIMEONSTATEA_INVALID
        res = self._maxTimeOnStateA
        return res

    def set_maxTimeOnStateA(self, newval):
        """
        Changes the maximum time (ms) allowed for the watchdog to stay in state A
        before automatically switching back in to B state. Use zero for no time limit.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the maximum time (ms) allowed for the watchdog to stay in state A
                before automatically switching back in to B state

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("maxTimeOnStateA", rest_val)

    def get_maxTimeOnStateB(self):
        """
        Retourne the maximum time (ms) allowed for the watchdog to stay in state B
        before automatically switching back in to A state. Zero means no time limit.

        @return an integer

        On failure, throws an exception or returns YWatchdog.MAXTIMEONSTATEB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.MAXTIMEONSTATEB_INVALID
        res = self._maxTimeOnStateB
        return res

    def set_maxTimeOnStateB(self, newval):
        """
        Changes the maximum time (ms) allowed for the watchdog to stay in state B before
        automatically switching back in to A state. Use zero for no time limit.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the maximum time (ms) allowed for the watchdog to stay
        in state B before
                automatically switching back in to A state

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("maxTimeOnStateB", rest_val)

    def get_output(self):
        """
        Returns the output state of the watchdog, when used as a simple switch (single throw).

        @return either YWatchdog.OUTPUT_OFF or YWatchdog.OUTPUT_ON, according to the output state of the
        watchdog, when used as a simple switch (single throw)

        On failure, throws an exception or returns YWatchdog.OUTPUT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.OUTPUT_INVALID
        res = self._output
        return res

    def set_output(self, newval):
        """
        Changes the output state of the watchdog, when used as a simple switch (single throw).

        @param newval : either YWatchdog.OUTPUT_OFF or YWatchdog.OUTPUT_ON, according to the output state
        of the watchdog, when used as a simple switch (single throw)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("output", rest_val)

    def get_pulseTimer(self):
        """
        Returns the number of milliseconds remaining before the watchdog is returned to idle position
        (state A), during a measured pulse generation. When there is no ongoing pulse, returns zero.

        @return an integer corresponding to the number of milliseconds remaining before the watchdog is
        returned to idle position
                (state A), during a measured pulse generation

        On failure, throws an exception or returns YWatchdog.PULSETIMER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.PULSETIMER_INVALID
        res = self._pulseTimer
        return res

    def set_pulseTimer(self, newval):
        rest_val = str(newval)
        return self._setAttr("pulseTimer", rest_val)

    def pulse(self, ms_duration):
        """
        Sets the relay to output B (active) for a specified duration, then brings it
        automatically back to output A (idle state).

        @param ms_duration : pulse duration, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(ms_duration)
        return self._setAttr("pulseTimer", rest_val)

    def get_delayedPulseTimer(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.DELAYEDPULSETIMER_INVALID
        res = self._delayedPulseTimer
        return res

    def set_delayedPulseTimer(self, newval):
        rest_val = str(newval.target) + ":" + str(newval.ms)
        return self._setAttr("delayedPulseTimer", rest_val)

    def delayedPulse(self, ms_delay, ms_duration):
        """
        Schedules a pulse.

        @param ms_delay : waiting time before the pulse, in milliseconds
        @param ms_duration : pulse duration, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(ms_delay) + ":" + str(ms_duration)
        return self._setAttr("delayedPulseTimer", rest_val)

    def get_countdown(self):
        """
        Returns the number of milliseconds remaining before a pulse (delayedPulse() call)
        When there is no scheduled pulse, returns zero.

        @return an integer corresponding to the number of milliseconds remaining before a pulse (delayedPulse() call)
                When there is no scheduled pulse, returns zero

        On failure, throws an exception or returns YWatchdog.COUNTDOWN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.COUNTDOWN_INVALID
        res = self._countdown
        return res

    def get_autoStart(self):
        """
        Returns the watchdog running state at module power on.

        @return either YWatchdog.AUTOSTART_OFF or YWatchdog.AUTOSTART_ON, according to the watchdog running
        state at module power on

        On failure, throws an exception or returns YWatchdog.AUTOSTART_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.AUTOSTART_INVALID
        res = self._autoStart
        return res

    def set_autoStart(self, newval):
        """
        Changes the watchdog running state at module power on. Remember to call the
        saveToFlash() method and then to reboot the module to apply this setting.

        @param newval : either YWatchdog.AUTOSTART_OFF or YWatchdog.AUTOSTART_ON, according to the watchdog
        running state at module power on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("autoStart", rest_val)

    def get_running(self):
        """
        Returns the watchdog running state.

        @return either YWatchdog.RUNNING_OFF or YWatchdog.RUNNING_ON, according to the watchdog running state

        On failure, throws an exception or returns YWatchdog.RUNNING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.RUNNING_INVALID
        res = self._running
        return res

    def set_running(self, newval):
        """
        Changes the running state of the watchdog.

        @param newval : either YWatchdog.RUNNING_OFF or YWatchdog.RUNNING_ON, according to the running
        state of the watchdog

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("running", rest_val)

    def resetWatchdog(self):
        """
        Resets the watchdog. When the watchdog is running, this function
        must be called on a regular basis to prevent the watchdog to
        trigger

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1"
        return self._setAttr("running", rest_val)

    def get_triggerDelay(self):
        """
        Returns  the waiting duration before a reset is automatically triggered by the watchdog, in milliseconds.

        @return an integer corresponding to  the waiting duration before a reset is automatically triggered
        by the watchdog, in milliseconds

        On failure, throws an exception or returns YWatchdog.TRIGGERDELAY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.TRIGGERDELAY_INVALID
        res = self._triggerDelay
        return res

    def set_triggerDelay(self, newval):
        """
        Changes the waiting delay before a reset is triggered by the watchdog,
        in milliseconds. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the waiting delay before a reset is triggered by the watchdog,
                in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("triggerDelay", rest_val)

    def get_triggerDuration(self):
        """
        Returns the duration of resets caused by the watchdog, in milliseconds.

        @return an integer corresponding to the duration of resets caused by the watchdog, in milliseconds

        On failure, throws an exception or returns YWatchdog.TRIGGERDURATION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWatchdog.TRIGGERDURATION_INVALID
        res = self._triggerDuration
        return res

    def set_triggerDuration(self, newval):
        """
        Changes the duration of resets caused by the watchdog, in milliseconds.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the duration of resets caused by the watchdog, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("triggerDuration", rest_val)

    @staticmethod
    def FindWatchdog(func):
        """
        Retrieves a watchdog for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the watchdog is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWatchdog.isOnline() to test if the watchdog is
        indeed online at a given time. In case of ambiguity when looking for
        a watchdog by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the watchdog, for instance
                WDOGDC01.watchdog1.

        @return a YWatchdog object allowing you to drive the watchdog.
        """
        # obj
        obj = YFunction._FindFromCache("Watchdog", func)
        if obj is None:
            obj = YWatchdog(func)
            YFunction._AddToCache("Watchdog", func, obj)
        return obj

    def toggle(self):
        """
        Switch the relay to the opposite state.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # sta
        # fw
        # mo
        if self._firm == 0:
            mo = self.get_module()
            fw = mo.get_firmwareRelease()
            if fw == YModule.FIRMWARERELEASE_INVALID:
                return YWatchdog.STATE_INVALID
            self._firm = YAPI._atoi(fw)
        if self._firm < 34921:
            sta = self.get_state()
            if sta == YWatchdog.STATE_INVALID:
                return YWatchdog.STATE_INVALID
            if sta == YWatchdog.STATE_B:
                self.set_state(YWatchdog.STATE_A)
            else:
                self.set_state(YWatchdog.STATE_B)
            return YAPI.SUCCESS
        else:
            return self._setAttr("state","X")

    def nextWatchdog(self):
        """
        Continues the enumeration of watchdog started using yFirstWatchdog().
        Caution: You can't make any assumption about the returned watchdog order.
        If you want to find a specific a watchdog, use Watchdog.findWatchdog()
        and a hardwareID or a logical name.

        @return a pointer to a YWatchdog object, corresponding to
                a watchdog currently online, or a None pointer
                if there are no more watchdog to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YWatchdog.FindWatchdog(hwidRef.value)

#--- (end of YWatchdog implementation)

#--- (YWatchdog functions)

    @staticmethod
    def FirstWatchdog():
        """
        Starts the enumeration of watchdog currently accessible.
        Use the method YWatchdog.nextWatchdog() to iterate on
        next watchdog.

        @return a pointer to a YWatchdog object, corresponding to
                the first watchdog currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Watchdog", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YWatchdog.FindWatchdog(serialRef.value + "." + funcIdRef.value)

#--- (end of YWatchdog functions)
