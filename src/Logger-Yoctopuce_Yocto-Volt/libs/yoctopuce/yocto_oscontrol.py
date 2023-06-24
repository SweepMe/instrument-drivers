# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_oscontrol.py 37827 2019-10-25 13:07:48Z mvuilleu $
#
#  Implements yFindOsControl(), the high-level API for OsControl functions
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


#--- (YOsControl class start)
#noinspection PyProtectedMember
class YOsControl(YFunction):
    """
    The YOScontrol class provides some control over the operating system running a VirtualHub.
    YOsControl is available on VirtualHub software only. This feature must be activated at the VirtualHub
    start up with -o option.

    """
    #--- (end of YOsControl class start)
    #--- (YOsControl return codes)
    #--- (end of YOsControl return codes)
    #--- (YOsControl dlldef)
    #--- (end of YOsControl dlldef)
    #--- (YOsControl yapiwrapper)
    #--- (end of YOsControl yapiwrapper)
    #--- (YOsControl definitions)
    SHUTDOWNCOUNTDOWN_INVALID = YAPI.INVALID_UINT
    #--- (end of YOsControl definitions)

    def __init__(self, func):
        super(YOsControl, self).__init__(func)
        self._className = 'OsControl'
        #--- (YOsControl attributes)
        self._callback = None
        self._shutdownCountdown = YOsControl.SHUTDOWNCOUNTDOWN_INVALID
        #--- (end of YOsControl attributes)

    #--- (YOsControl implementation)
    def _parseAttr(self, json_val):
        if json_val.has("shutdownCountdown"):
            self._shutdownCountdown = json_val.getInt("shutdownCountdown")
        super(YOsControl, self)._parseAttr(json_val)

    def get_shutdownCountdown(self):
        """
        Returns the remaining number of seconds before the OS shutdown, or zero when no
        shutdown has been scheduled.

        @return an integer corresponding to the remaining number of seconds before the OS shutdown, or zero when no
                shutdown has been scheduled

        On failure, throws an exception or returns YOsControl.SHUTDOWNCOUNTDOWN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YOsControl.SHUTDOWNCOUNTDOWN_INVALID
        res = self._shutdownCountdown
        return res

    def set_shutdownCountdown(self, newval):
        rest_val = str(newval)
        return self._setAttr("shutdownCountdown", rest_val)

    @staticmethod
    def FindOsControl(func):
        """
        Retrieves OS control for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the OS control is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YOsControl.isOnline() to test if the OS control is
        indeed online at a given time. In case of ambiguity when looking for
        OS control by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the OS control, for instance
                MyDevice.osControl.

        @return a YOsControl object allowing you to drive the OS control.
        """
        # obj
        obj = YFunction._FindFromCache("OsControl", func)
        if obj is None:
            obj = YOsControl(func)
            YFunction._AddToCache("OsControl", func, obj)
        return obj

    def shutdown(self, secBeforeShutDown):
        """
        Schedules an OS shutdown after a given number of seconds.

        @param secBeforeShutDown : number of seconds before shutdown

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_shutdownCountdown(secBeforeShutDown)

    def nextOsControl(self):
        """
        Continues the enumeration of OS control started using yFirstOsControl().
        Caution: You can't make any assumption about the returned OS control order.
        If you want to find a specific OS control, use OsControl.findOsControl()
        and a hardwareID or a logical name.

        @return a pointer to a YOsControl object, corresponding to
                OS control currently online, or a None pointer
                if there are no more OS control to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YOsControl.FindOsControl(hwidRef.value)

#--- (end of YOsControl implementation)

#--- (YOsControl functions)

    @staticmethod
    def FirstOsControl():
        """
        Starts the enumeration of OS control currently accessible.
        Use the method YOsControl.nextOsControl() to iterate on
        next OS control.

        @return a pointer to a YOsControl object, corresponding to
                the first OS control currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("OsControl", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YOsControl.FindOsControl(serialRef.value + "." + funcIdRef.value)

#--- (end of YOsControl functions)
