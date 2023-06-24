# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_wakeupschedule.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindWakeUpSchedule(), the high-level API for WakeUpSchedule functions
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


#--- (YWakeUpSchedule class start)
#noinspection PyProtectedMember
class YWakeUpSchedule(YFunction):
    """
    The YWakeUpSchedule class implements a wake up condition. The wake up time is
    specified as a set of months and/or days and/or hours and/or minutes when the
    wake up should happen.

    """
    #--- (end of YWakeUpSchedule class start)
    #--- (YWakeUpSchedule return codes)
    #--- (end of YWakeUpSchedule return codes)
    #--- (YWakeUpSchedule dlldef)
    #--- (end of YWakeUpSchedule dlldef)
    #--- (YWakeUpSchedule yapiwrapper)
    #--- (end of YWakeUpSchedule yapiwrapper)
    #--- (YWakeUpSchedule definitions)
    MINUTESA_INVALID = YAPI.INVALID_UINT
    MINUTESB_INVALID = YAPI.INVALID_UINT
    HOURS_INVALID = YAPI.INVALID_UINT
    WEEKDAYS_INVALID = YAPI.INVALID_UINT
    MONTHDAYS_INVALID = YAPI.INVALID_UINT
    MONTHS_INVALID = YAPI.INVALID_UINT
    NEXTOCCURENCE_INVALID = YAPI.INVALID_LONG
    #--- (end of YWakeUpSchedule definitions)

    def __init__(self, func):
        super(YWakeUpSchedule, self).__init__(func)
        self._className = 'WakeUpSchedule'
        #--- (YWakeUpSchedule attributes)
        self._callback = None
        self._minutesA = YWakeUpSchedule.MINUTESA_INVALID
        self._minutesB = YWakeUpSchedule.MINUTESB_INVALID
        self._hours = YWakeUpSchedule.HOURS_INVALID
        self._weekDays = YWakeUpSchedule.WEEKDAYS_INVALID
        self._monthDays = YWakeUpSchedule.MONTHDAYS_INVALID
        self._months = YWakeUpSchedule.MONTHS_INVALID
        self._nextOccurence = YWakeUpSchedule.NEXTOCCURENCE_INVALID
        #--- (end of YWakeUpSchedule attributes)

    #--- (YWakeUpSchedule implementation)
    def _parseAttr(self, json_val):
        if json_val.has("minutesA"):
            self._minutesA = json_val.getInt("minutesA")
        if json_val.has("minutesB"):
            self._minutesB = json_val.getInt("minutesB")
        if json_val.has("hours"):
            self._hours = json_val.getInt("hours")
        if json_val.has("weekDays"):
            self._weekDays = json_val.getInt("weekDays")
        if json_val.has("monthDays"):
            self._monthDays = json_val.getInt("monthDays")
        if json_val.has("months"):
            self._months = json_val.getInt("months")
        if json_val.has("nextOccurence"):
            self._nextOccurence = json_val.getLong("nextOccurence")
        super(YWakeUpSchedule, self)._parseAttr(json_val)

    def get_minutesA(self):
        """
        Returns the minutes in the 00-29 interval of each hour scheduled for wake up.

        @return an integer corresponding to the minutes in the 00-29 interval of each hour scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MINUTESA_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MINUTESA_INVALID
        res = self._minutesA
        return res

    def set_minutesA(self, newval):
        """
        Changes the minutes in the 00-29 interval when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the minutes in the 00-29 interval when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("minutesA", rest_val)

    def get_minutesB(self):
        """
        Returns the minutes in the 30-59 interval of each hour scheduled for wake up.

        @return an integer corresponding to the minutes in the 30-59 interval of each hour scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MINUTESB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MINUTESB_INVALID
        res = self._minutesB
        return res

    def set_minutesB(self, newval):
        """
        Changes the minutes in the 30-59 interval when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the minutes in the 30-59 interval when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("minutesB", rest_val)

    def get_hours(self):
        """
        Returns the hours scheduled for wake up.

        @return an integer corresponding to the hours scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.HOURS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.HOURS_INVALID
        res = self._hours
        return res

    def set_hours(self, newval):
        """
        Changes the hours when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the hours when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("hours", rest_val)

    def get_weekDays(self):
        """
        Returns the days of the week scheduled for wake up.

        @return an integer corresponding to the days of the week scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.WEEKDAYS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.WEEKDAYS_INVALID
        res = self._weekDays
        return res

    def set_weekDays(self, newval):
        """
        Changes the days of the week when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the days of the week when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("weekDays", rest_val)

    def get_monthDays(self):
        """
        Returns the days of the month scheduled for wake up.

        @return an integer corresponding to the days of the month scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MONTHDAYS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MONTHDAYS_INVALID
        res = self._monthDays
        return res

    def set_monthDays(self, newval):
        """
        Changes the days of the month when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the days of the month when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("monthDays", rest_val)

    def get_months(self):
        """
        Returns the months scheduled for wake up.

        @return an integer corresponding to the months scheduled for wake up

        On failure, throws an exception or returns YWakeUpSchedule.MONTHS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.MONTHS_INVALID
        res = self._months
        return res

    def set_months(self, newval):
        """
        Changes the months when a wake up must take place.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the months when a wake up must take place

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("months", rest_val)

    def get_nextOccurence(self):
        """
        Returns the date/time (seconds) of the next wake up occurrence.

        @return an integer corresponding to the date/time (seconds) of the next wake up occurrence

        On failure, throws an exception or returns YWakeUpSchedule.NEXTOCCURENCE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YWakeUpSchedule.NEXTOCCURENCE_INVALID
        res = self._nextOccurence
        return res

    @staticmethod
    def FindWakeUpSchedule(func):
        """
        Retrieves a wake up schedule for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the wake up schedule is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YWakeUpSchedule.isOnline() to test if the wake up schedule is
        indeed online at a given time. In case of ambiguity when looking for
        a wake up schedule by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the wake up schedule, for instance
                YHUBGSM3.wakeUpSchedule1.

        @return a YWakeUpSchedule object allowing you to drive the wake up schedule.
        """
        # obj
        obj = YFunction._FindFromCache("WakeUpSchedule", func)
        if obj is None:
            obj = YWakeUpSchedule(func)
            YFunction._AddToCache("WakeUpSchedule", func, obj)
        return obj

    def get_minutes(self):
        """
        Returns all the minutes of each hour that are scheduled for wake up.
        """
        # res

        res = self.get_minutesB()
        res = ((res) << (30))
        res = res + self.get_minutesA()
        return res

    def set_minutes(self, bitmap):
        """
        Changes all the minutes where a wake up must take place.

        @param bitmap : Minutes 00-59 of each hour scheduled for wake up.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.set_minutesA(((bitmap) & (0x3fffffff)))
        bitmap = ((bitmap) >> (30))
        return self.set_minutesB(((bitmap) & (0x3fffffff)))

    def nextWakeUpSchedule(self):
        """
        Continues the enumeration of wake up schedules started using yFirstWakeUpSchedule().
        Caution: You can't make any assumption about the returned wake up schedules order.
        If you want to find a specific a wake up schedule, use WakeUpSchedule.findWakeUpSchedule()
        and a hardwareID or a logical name.

        @return a pointer to a YWakeUpSchedule object, corresponding to
                a wake up schedule currently online, or a None pointer
                if there are no more wake up schedules to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YWakeUpSchedule.FindWakeUpSchedule(hwidRef.value)

#--- (end of YWakeUpSchedule implementation)

#--- (YWakeUpSchedule functions)

    @staticmethod
    def FirstWakeUpSchedule():
        """
        Starts the enumeration of wake up schedules currently accessible.
        Use the method YWakeUpSchedule.nextWakeUpSchedule() to iterate on
        next wake up schedules.

        @return a pointer to a YWakeUpSchedule object, corresponding to
                the first wake up schedule currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("WakeUpSchedule", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YWakeUpSchedule.FindWakeUpSchedule(serialRef.value + "." + funcIdRef.value)

#--- (end of YWakeUpSchedule functions)
