# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_realtimeclock.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindRealTimeClock(), the high-level API for RealTimeClock functions
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


#--- (YRealTimeClock class start)
#noinspection PyProtectedMember
class YRealTimeClock(YFunction):
    """
    The YRealTimeClock class provide access to the embedded real-time clock available on some Yoctopuce
    devices. It can provide current date and time, even after a power outage
    lasting several days. It is the base for automated wake-up functions provided by the WakeUpScheduler.
    The current time may represent a local time as well as an UTC time, but no automatic time change
    will occur to account for daylight saving time.

    """
    #--- (end of YRealTimeClock class start)
    #--- (YRealTimeClock return codes)
    #--- (end of YRealTimeClock return codes)
    #--- (YRealTimeClock dlldef)
    #--- (end of YRealTimeClock dlldef)
    #--- (YRealTimeClock yapiwrapper)
    #--- (end of YRealTimeClock yapiwrapper)
    #--- (YRealTimeClock definitions)
    UNIXTIME_INVALID = YAPI.INVALID_LONG
    DATETIME_INVALID = YAPI.INVALID_STRING
    UTCOFFSET_INVALID = YAPI.INVALID_INT
    TIMESET_FALSE = 0
    TIMESET_TRUE = 1
    TIMESET_INVALID = -1
    #--- (end of YRealTimeClock definitions)

    def __init__(self, func):
        super(YRealTimeClock, self).__init__(func)
        self._className = 'RealTimeClock'
        #--- (YRealTimeClock attributes)
        self._callback = None
        self._unixTime = YRealTimeClock.UNIXTIME_INVALID
        self._dateTime = YRealTimeClock.DATETIME_INVALID
        self._utcOffset = YRealTimeClock.UTCOFFSET_INVALID
        self._timeSet = YRealTimeClock.TIMESET_INVALID
        #--- (end of YRealTimeClock attributes)

    #--- (YRealTimeClock implementation)
    def _parseAttr(self, json_val):
        if json_val.has("unixTime"):
            self._unixTime = json_val.getLong("unixTime")
        if json_val.has("dateTime"):
            self._dateTime = json_val.getString("dateTime")
        if json_val.has("utcOffset"):
            self._utcOffset = json_val.getInt("utcOffset")
        if json_val.has("timeSet"):
            self._timeSet = (json_val.getInt("timeSet") > 0 if 1 else 0)
        super(YRealTimeClock, self)._parseAttr(json_val)

    def get_unixTime(self):
        """
        Returns the current time in Unix format (number of elapsed seconds since Jan 1st, 1970).

        @return an integer corresponding to the current time in Unix format (number of elapsed seconds
        since Jan 1st, 1970)

        On failure, throws an exception or returns YRealTimeClock.UNIXTIME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRealTimeClock.UNIXTIME_INVALID
        res = self._unixTime
        return res

    def set_unixTime(self, newval):
        """
        Changes the current time. Time is specifid in Unix format (number of elapsed seconds since Jan 1st, 1970).

        @param newval : an integer corresponding to the current time

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("unixTime", rest_val)

    def get_dateTime(self):
        """
        Returns the current time in the form "YYYY/MM/DD hh:mm:ss".

        @return a string corresponding to the current time in the form "YYYY/MM/DD hh:mm:ss"

        On failure, throws an exception or returns YRealTimeClock.DATETIME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRealTimeClock.DATETIME_INVALID
        res = self._dateTime
        return res

    def get_utcOffset(self):
        """
        Returns the number of seconds between current time and UTC time (time zone).

        @return an integer corresponding to the number of seconds between current time and UTC time (time zone)

        On failure, throws an exception or returns YRealTimeClock.UTCOFFSET_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRealTimeClock.UTCOFFSET_INVALID
        res = self._utcOffset
        return res

    def set_utcOffset(self, newval):
        """
        Changes the number of seconds between current time and UTC time (time zone).
        The timezone is automatically rounded to the nearest multiple of 15 minutes.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the number of seconds between current time and UTC time (time zone)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("utcOffset", rest_val)

    def get_timeSet(self):
        """
        Returns true if the clock has been set, and false otherwise.

        @return either YRealTimeClock.TIMESET_FALSE or YRealTimeClock.TIMESET_TRUE, according to true if
        the clock has been set, and false otherwise

        On failure, throws an exception or returns YRealTimeClock.TIMESET_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YRealTimeClock.TIMESET_INVALID
        res = self._timeSet
        return res

    @staticmethod
    def FindRealTimeClock(func):
        """
        Retrieves a real-time clock for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the real-time clock is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YRealTimeClock.isOnline() to test if the real-time clock is
        indeed online at a given time. In case of ambiguity when looking for
        a real-time clock by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the real-time clock, for instance
                YHUBGSM3.realTimeClock.

        @return a YRealTimeClock object allowing you to drive the real-time clock.
        """
        # obj
        obj = YFunction._FindFromCache("RealTimeClock", func)
        if obj is None:
            obj = YRealTimeClock(func)
            YFunction._AddToCache("RealTimeClock", func, obj)
        return obj

    def nextRealTimeClock(self):
        """
        Continues the enumeration of real-time clocks started using yFirstRealTimeClock().
        Caution: You can't make any assumption about the returned real-time clocks order.
        If you want to find a specific a real-time clock, use RealTimeClock.findRealTimeClock()
        and a hardwareID or a logical name.

        @return a pointer to a YRealTimeClock object, corresponding to
                a real-time clock currently online, or a None pointer
                if there are no more real-time clocks to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YRealTimeClock.FindRealTimeClock(hwidRef.value)

#--- (end of YRealTimeClock implementation)

#--- (YRealTimeClock functions)

    @staticmethod
    def FirstRealTimeClock():
        """
        Starts the enumeration of real-time clocks currently accessible.
        Use the method YRealTimeClock.nextRealTimeClock() to iterate on
        next real-time clocks.

        @return a pointer to a YRealTimeClock object, corresponding to
                the first real-time clock currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("RealTimeClock", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YRealTimeClock.FindRealTimeClock(serialRef.value + "." + funcIdRef.value)

#--- (end of YRealTimeClock functions)
