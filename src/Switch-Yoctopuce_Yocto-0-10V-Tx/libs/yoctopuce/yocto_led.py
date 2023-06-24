# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_led.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindLed(), the high-level API for Led functions
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


#--- (YLed class start)
#noinspection PyProtectedMember
class YLed(YFunction):
    """
    The YLed class allows you to drive a monocolor LED.
    You can not only to drive the intensity of the LED, but also to
    have it blink at various preset frequencies.

    """
    #--- (end of YLed class start)
    #--- (YLed return codes)
    #--- (end of YLed return codes)
    #--- (YLed dlldef)
    #--- (end of YLed dlldef)
    #--- (YLed yapiwrapper)
    #--- (end of YLed yapiwrapper)
    #--- (YLed definitions)
    LUMINOSITY_INVALID = YAPI.INVALID_UINT
    POWER_OFF = 0
    POWER_ON = 1
    POWER_INVALID = -1
    BLINKING_STILL = 0
    BLINKING_RELAX = 1
    BLINKING_AWARE = 2
    BLINKING_RUN = 3
    BLINKING_CALL = 4
    BLINKING_PANIC = 5
    BLINKING_INVALID = -1
    #--- (end of YLed definitions)

    def __init__(self, func):
        super(YLed, self).__init__(func)
        self._className = 'Led'
        #--- (YLed attributes)
        self._callback = None
        self._power = YLed.POWER_INVALID
        self._luminosity = YLed.LUMINOSITY_INVALID
        self._blinking = YLed.BLINKING_INVALID
        #--- (end of YLed attributes)

    #--- (YLed implementation)
    def _parseAttr(self, json_val):
        if json_val.has("power"):
            self._power = (json_val.getInt("power") > 0 if 1 else 0)
        if json_val.has("luminosity"):
            self._luminosity = json_val.getInt("luminosity")
        if json_val.has("blinking"):
            self._blinking = json_val.getInt("blinking")
        super(YLed, self)._parseAttr(json_val)

    def get_power(self):
        """
        Returns the current LED state.

        @return either YLed.POWER_OFF or YLed.POWER_ON, according to the current LED state

        On failure, throws an exception or returns YLed.POWER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YLed.POWER_INVALID
        res = self._power
        return res

    def set_power(self, newval):
        """
        Changes the state of the LED.

        @param newval : either YLed.POWER_OFF or YLed.POWER_ON, according to the state of the LED

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("power", rest_val)

    def get_luminosity(self):
        """
        Returns the current LED intensity (in per cent).

        @return an integer corresponding to the current LED intensity (in per cent)

        On failure, throws an exception or returns YLed.LUMINOSITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YLed.LUMINOSITY_INVALID
        res = self._luminosity
        return res

    def set_luminosity(self, newval):
        """
        Changes the current LED intensity (in per cent). Remember to call the
        saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the current LED intensity (in per cent)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("luminosity", rest_val)

    def get_blinking(self):
        """
        Returns the current LED signaling mode.

        @return a value among YLed.BLINKING_STILL, YLed.BLINKING_RELAX, YLed.BLINKING_AWARE,
        YLed.BLINKING_RUN, YLed.BLINKING_CALL and YLed.BLINKING_PANIC corresponding to the current LED signaling mode

        On failure, throws an exception or returns YLed.BLINKING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YLed.BLINKING_INVALID
        res = self._blinking
        return res

    def set_blinking(self, newval):
        """
        Changes the current LED signaling mode.

        @param newval : a value among YLed.BLINKING_STILL, YLed.BLINKING_RELAX, YLed.BLINKING_AWARE,
        YLed.BLINKING_RUN, YLed.BLINKING_CALL and YLed.BLINKING_PANIC corresponding to the current LED signaling mode

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("blinking", rest_val)

    @staticmethod
    def FindLed(func):
        """
        Retrieves a monochrome LED for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the monochrome LED is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YLed.isOnline() to test if the monochrome LED is
        indeed online at a given time. In case of ambiguity when looking for
        a monochrome LED by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the monochrome LED, for instance
                YBUZZER2.led1.

        @return a YLed object allowing you to drive the monochrome LED.
        """
        # obj
        obj = YFunction._FindFromCache("Led", func)
        if obj is None:
            obj = YLed(func)
            YFunction._AddToCache("Led", func, obj)
        return obj

    def nextLed(self):
        """
        Continues the enumeration of monochrome LEDs started using yFirstLed().
        Caution: You can't make any assumption about the returned monochrome LEDs order.
        If you want to find a specific a monochrome LED, use Led.findLed()
        and a hardwareID or a logical name.

        @return a pointer to a YLed object, corresponding to
                a monochrome LED currently online, or a None pointer
                if there are no more monochrome LEDs to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YLed.FindLed(hwidRef.value)

#--- (end of YLed implementation)

#--- (YLed functions)

    @staticmethod
    def FirstLed():
        """
        Starts the enumeration of monochrome LEDs currently accessible.
        Use the method YLed.nextLed() to iterate on
        next monochrome LEDs.

        @return a pointer to a YLed object, corresponding to
                the first monochrome LED currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Led", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YLed.FindLed(serialRef.value + "." + funcIdRef.value)

#--- (end of YLed functions)
