# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_relay.py 39434 2020-02-25 08:53:55Z seb $
#
#  Implements yFindRelay(), the high-level API for Relay functions
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


#--- (YRelay class start)
#noinspection PyProtectedMember
class YRelay(YFunction):
    """
    The YRelay class allows you to drive a Yoctopuce relay or optocoupled output.
    It can be used to simply switch the output on or off, but also to automatically generate short
    pulses of determined duration.
    On devices with two output for each relay (double throw), the two outputs are named A and B,
    with output A corresponding to the idle position (normally closed) and the output B corresponding to the
    active state (normally open).

    """
    #--- (end of YRelay class start)
    #--- (YRelay return codes)
    #--- (end of YRelay return codes)
    #--- (YRelay dlldef)
    #--- (end of YRelay dlldef)
    #--- (YRelay yapiwrapper)
    #--- (end of YRelay yapiwrapper)
    #--- (YRelay definitions)
    MAXTIMEONSTATEA_INVALID = YAPI.INVALID_LONG
    MAXTIMEONSTATEB_INVALID = YAPI.INVALID_LONG
    PULSETIMER_INVALID = YAPI.INVALID_LONG
    DELAYEDPULSETIMER_INVALID = None
    COUNTDOWN_INVALID = YAPI.INVALID_LONG
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
    #--- (end of YRelay definitions)

    def __init__(self, func):
        super(YRelay, self).__init__(func)
        self._className = 'Relay'
        #--- (YRelay attributes)
        self._callback = None
        self._state = YRelay.STATE_INVALID
        self._stateAtPowerOn = YRelay.STATEATPOWERON_INVALID
        self._maxTimeOnStateA = YRelay.MAXTIMEONSTATEA_INVALID
        self._maxTimeOnStateB = YRelay.MAXTIMEONSTATEB_INVALID
        self._output = YRelay.OUTPUT_INVALID
        self._pulseTimer = YRelay.PULSETIMER_INVALID
        self._delayedPulseTimer = YRelay.DELAYEDPULSETIMER_INVALID
        self._countdown = YRelay.COUNTDOWN_INVALID
        self._firm = 0
        #--- (end of YRelay attributes)

    #--- (YRelay implementation)
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
        super(YRelay, self)._parseAttr(json_val)

    def get_state(self):
        """
        Returns the state of the relays (A for the idle position, B for the active position).

        @return either YRelay.STATE_A or YRelay.STATE_B, according to the state of the relays (A for the
        idle position, B for the active position)

        On failure, throws an exception or returns YRelay.STATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.STATE_INVALID
        res = self._state
        return res

    def set_state(self, newval):
        """
        Changes the state of the relays (A for the idle position, B for the active position).

        @param newval : either YRelay.STATE_A or YRelay.STATE_B, according to the state of the relays (A
        for the idle position, B for the active position)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("state", rest_val)

    def get_stateAtPowerOn(self):
        """
        Returns the state of the relays at device startup (A for the idle position,
        B for the active position, UNCHANGED to leave the relay state as is).

        @return a value among YRelay.STATEATPOWERON_UNCHANGED, YRelay.STATEATPOWERON_A and
        YRelay.STATEATPOWERON_B corresponding to the state of the relays at device startup (A for the idle position,
                B for the active position, UNCHANGED to leave the relay state as is)

        On failure, throws an exception or returns YRelay.STATEATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.STATEATPOWERON_INVALID
        res = self._stateAtPowerOn
        return res

    def set_stateAtPowerOn(self, newval):
        """
        Changes the state of the relays at device startup (A for the idle position,
        B for the active position, UNCHANGED to leave the relay state as is).
        Remember to call the matching module saveToFlash()
        method, otherwise this call will have no effect.

        @param newval : a value among YRelay.STATEATPOWERON_UNCHANGED, YRelay.STATEATPOWERON_A and
        YRelay.STATEATPOWERON_B corresponding to the state of the relays at device startup (A for the idle position,
                B for the active position, UNCHANGED to leave the relay state as is)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("stateAtPowerOn", rest_val)

    def get_maxTimeOnStateA(self):
        """
        Returns the maximum time (ms) allowed for the relay to stay in state
        A before automatically switching back in to B state. Zero means no time limit.

        @return an integer corresponding to the maximum time (ms) allowed for the relay to stay in state
                A before automatically switching back in to B state

        On failure, throws an exception or returns YRelay.MAXTIMEONSTATEA_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.MAXTIMEONSTATEA_INVALID
        res = self._maxTimeOnStateA
        return res

    def set_maxTimeOnStateA(self, newval):
        """
        Changes the maximum time (ms) allowed for the relay to stay in state A
        before automatically switching back in to B state. Use zero for no time limit.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the maximum time (ms) allowed for the relay to stay in state A
                before automatically switching back in to B state

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("maxTimeOnStateA", rest_val)

    def get_maxTimeOnStateB(self):
        """
        Retourne the maximum time (ms) allowed for the relay to stay in state B
        before automatically switching back in to A state. Zero means no time limit.

        @return an integer

        On failure, throws an exception or returns YRelay.MAXTIMEONSTATEB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.MAXTIMEONSTATEB_INVALID
        res = self._maxTimeOnStateB
        return res

    def set_maxTimeOnStateB(self, newval):
        """
        Changes the maximum time (ms) allowed for the relay to stay in state B before
        automatically switching back in to A state. Use zero for no time limit.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the maximum time (ms) allowed for the relay to stay in
        state B before
                automatically switching back in to A state

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("maxTimeOnStateB", rest_val)

    def get_output(self):
        """
        Returns the output state of the relays, when used as a simple switch (single throw).

        @return either YRelay.OUTPUT_OFF or YRelay.OUTPUT_ON, according to the output state of the relays,
        when used as a simple switch (single throw)

        On failure, throws an exception or returns YRelay.OUTPUT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.OUTPUT_INVALID
        res = self._output
        return res

    def set_output(self, newval):
        """
        Changes the output state of the relays, when used as a simple switch (single throw).

        @param newval : either YRelay.OUTPUT_OFF or YRelay.OUTPUT_ON, according to the output state of the
        relays, when used as a simple switch (single throw)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("output", rest_val)

    def get_pulseTimer(self):
        """
        Returns the number of milliseconds remaining before the relays is returned to idle position
        (state A), during a measured pulse generation. When there is no ongoing pulse, returns zero.

        @return an integer corresponding to the number of milliseconds remaining before the relays is
        returned to idle position
                (state A), during a measured pulse generation

        On failure, throws an exception or returns YRelay.PULSETIMER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.PULSETIMER_INVALID
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
                return YRelay.DELAYEDPULSETIMER_INVALID
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

        On failure, throws an exception or returns YRelay.COUNTDOWN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRelay.COUNTDOWN_INVALID
        res = self._countdown
        return res

    @staticmethod
    def FindRelay(func):
        """
        Retrieves a relay for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the relay is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YRelay.isOnline() to test if the relay is
        indeed online at a given time. In case of ambiguity when looking for
        a relay by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the relay, for instance
                MXCOUPL2.relay1.

        @return a YRelay object allowing you to drive the relay.
        """
        # obj
        obj = YFunction._FindFromCache("Relay", func)
        if obj is None:
            obj = YRelay(func)
            YFunction._AddToCache("Relay", func, obj)
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
                return YRelay.STATE_INVALID
            self._firm = YAPI._atoi(fw)
        if self._firm < 34921:
            sta = self.get_state()
            if sta == YRelay.STATE_INVALID:
                return YRelay.STATE_INVALID
            if sta == YRelay.STATE_B:
                self.set_state(YRelay.STATE_A)
            else:
                self.set_state(YRelay.STATE_B)
            return YAPI.SUCCESS
        else:
            return self._setAttr("state","X")

    def nextRelay(self):
        """
        Continues the enumeration of relays started using yFirstRelay().
        Caution: You can't make any assumption about the returned relays order.
        If you want to find a specific a relay, use Relay.findRelay()
        and a hardwareID or a logical name.

        @return a pointer to a YRelay object, corresponding to
                a relay currently online, or a None pointer
                if there are no more relays to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YRelay.FindRelay(hwidRef.value)

#--- (end of YRelay implementation)

#--- (YRelay functions)

    @staticmethod
    def FirstRelay():
        """
        Starts the enumeration of relays currently accessible.
        Use the method YRelay.nextRelay() to iterate on
        next relays.

        @return a pointer to a YRelay object, corresponding to
                the first relay currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Relay", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YRelay.FindRelay(serialRef.value + "." + funcIdRef.value)

#--- (end of YRelay functions)
