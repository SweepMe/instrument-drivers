# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_dualpower.py 38913 2019-12-20 18:59:49Z mvuilleu $
#
#  Implements yFindDualPower(), the high-level API for DualPower functions
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


#--- (YDualPower class start)
#noinspection PyProtectedMember
class YDualPower(YFunction):
    """
    The YDualPower class allows you to control
    the power source to use for module functions that require high current.
    The module can also automatically disconnect the external power
    when a voltage drop is observed on the external power source
    (external battery running out of power).

    """
    #--- (end of YDualPower class start)
    #--- (YDualPower return codes)
    #--- (end of YDualPower return codes)
    #--- (YDualPower dlldef)
    #--- (end of YDualPower dlldef)
    #--- (YDualPower yapiwrapper)
    #--- (end of YDualPower yapiwrapper)
    #--- (YDualPower definitions)
    EXTVOLTAGE_INVALID = YAPI.INVALID_UINT
    POWERSTATE_OFF = 0
    POWERSTATE_FROM_USB = 1
    POWERSTATE_FROM_EXT = 2
    POWERSTATE_INVALID = -1
    POWERCONTROL_AUTO = 0
    POWERCONTROL_FROM_USB = 1
    POWERCONTROL_FROM_EXT = 2
    POWERCONTROL_OFF = 3
    POWERCONTROL_INVALID = -1
    #--- (end of YDualPower definitions)

    def __init__(self, func):
        super(YDualPower, self).__init__(func)
        self._className = 'DualPower'
        #--- (YDualPower attributes)
        self._callback = None
        self._powerState = YDualPower.POWERSTATE_INVALID
        self._powerControl = YDualPower.POWERCONTROL_INVALID
        self._extVoltage = YDualPower.EXTVOLTAGE_INVALID
        #--- (end of YDualPower attributes)

    #--- (YDualPower implementation)
    def _parseAttr(self, json_val):
        if json_val.has("powerState"):
            self._powerState = json_val.getInt("powerState")
        if json_val.has("powerControl"):
            self._powerControl = json_val.getInt("powerControl")
        if json_val.has("extVoltage"):
            self._extVoltage = json_val.getInt("extVoltage")
        super(YDualPower, self)._parseAttr(json_val)

    def get_powerState(self):
        """
        Returns the current power source for module functions that require lots of current.

        @return a value among YDualPower.POWERSTATE_OFF, YDualPower.POWERSTATE_FROM_USB and
        YDualPower.POWERSTATE_FROM_EXT corresponding to the current power source for module functions that
        require lots of current

        On failure, throws an exception or returns YDualPower.POWERSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.POWERSTATE_INVALID
        res = self._powerState
        return res

    def get_powerControl(self):
        """
        Returns the selected power source for module functions that require lots of current.

        @return a value among YDualPower.POWERCONTROL_AUTO, YDualPower.POWERCONTROL_FROM_USB,
        YDualPower.POWERCONTROL_FROM_EXT and YDualPower.POWERCONTROL_OFF corresponding to the selected
        power source for module functions that require lots of current

        On failure, throws an exception or returns YDualPower.POWERCONTROL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.POWERCONTROL_INVALID
        res = self._powerControl
        return res

    def set_powerControl(self, newval):
        """
        Changes the selected power source for module functions that require lots of current.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a value among YDualPower.POWERCONTROL_AUTO, YDualPower.POWERCONTROL_FROM_USB,
        YDualPower.POWERCONTROL_FROM_EXT and YDualPower.POWERCONTROL_OFF corresponding to the selected
        power source for module functions that require lots of current

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("powerControl", rest_val)

    def get_extVoltage(self):
        """
        Returns the measured voltage on the external power source, in millivolts.

        @return an integer corresponding to the measured voltage on the external power source, in millivolts

        On failure, throws an exception or returns YDualPower.EXTVOLTAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDualPower.EXTVOLTAGE_INVALID
        res = self._extVoltage
        return res

    @staticmethod
    def FindDualPower(func):
        """
        Retrieves a dual power switch for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the dual power switch is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDualPower.isOnline() to test if the dual power switch is
        indeed online at a given time. In case of ambiguity when looking for
        a dual power switch by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the dual power switch, for instance
                SERVORC1.dualPower.

        @return a YDualPower object allowing you to drive the dual power switch.
        """
        # obj
        obj = YFunction._FindFromCache("DualPower", func)
        if obj is None:
            obj = YDualPower(func)
            YFunction._AddToCache("DualPower", func, obj)
        return obj

    def nextDualPower(self):
        """
        Continues the enumeration of dual power switches started using yFirstDualPower().
        Caution: You can't make any assumption about the returned dual power switches order.
        If you want to find a specific a dual power switch, use DualPower.findDualPower()
        and a hardwareID or a logical name.

        @return a pointer to a YDualPower object, corresponding to
                a dual power switch currently online, or a None pointer
                if there are no more dual power switches to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YDualPower.FindDualPower(hwidRef.value)

#--- (end of YDualPower implementation)

#--- (YDualPower functions)

    @staticmethod
    def FirstDualPower():
        """
        Starts the enumeration of dual power switches currently accessible.
        Use the method YDualPower.nextDualPower() to iterate on
        next dual power switches.

        @return a pointer to a YDualPower object, corresponding to
                the first dual power switch currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("DualPower", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YDualPower.FindDualPower(serialRef.value + "." + funcIdRef.value)

#--- (end of YDualPower functions)
