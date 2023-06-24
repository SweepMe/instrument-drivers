# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_daisychain.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindDaisyChain(), the high-level API for DaisyChain functions
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


#--- (YDaisyChain class start)
#noinspection PyProtectedMember
class YDaisyChain(YFunction):
    """
    The YDaisyChain class can be used to verify that devices that
    are daisy-chained directly from device to device, without a hub,
    are detected properly.

    """
    #--- (end of YDaisyChain class start)
    #--- (YDaisyChain return codes)
    #--- (end of YDaisyChain return codes)
    #--- (YDaisyChain dlldef)
    #--- (end of YDaisyChain dlldef)
    #--- (YDaisyChain yapiwrapper)
    #--- (end of YDaisyChain yapiwrapper)
    #--- (YDaisyChain definitions)
    CHILDCOUNT_INVALID = YAPI.INVALID_UINT
    REQUIREDCHILDCOUNT_INVALID = YAPI.INVALID_UINT
    DAISYSTATE_READY = 0
    DAISYSTATE_IS_CHILD = 1
    DAISYSTATE_FIRMWARE_MISMATCH = 2
    DAISYSTATE_CHILD_MISSING = 3
    DAISYSTATE_CHILD_LOST = 4
    DAISYSTATE_INVALID = -1
    #--- (end of YDaisyChain definitions)

    def __init__(self, func):
        super(YDaisyChain, self).__init__(func)
        self._className = 'DaisyChain'
        #--- (YDaisyChain attributes)
        self._callback = None
        self._daisyState = YDaisyChain.DAISYSTATE_INVALID
        self._childCount = YDaisyChain.CHILDCOUNT_INVALID
        self._requiredChildCount = YDaisyChain.REQUIREDCHILDCOUNT_INVALID
        #--- (end of YDaisyChain attributes)

    #--- (YDaisyChain implementation)
    def _parseAttr(self, json_val):
        if json_val.has("daisyState"):
            self._daisyState = json_val.getInt("daisyState")
        if json_val.has("childCount"):
            self._childCount = json_val.getInt("childCount")
        if json_val.has("requiredChildCount"):
            self._requiredChildCount = json_val.getInt("requiredChildCount")
        super(YDaisyChain, self)._parseAttr(json_val)

    def get_daisyState(self):
        """
        Returns the state of the daisy-link between modules.

        @return a value among YDaisyChain.DAISYSTATE_READY, YDaisyChain.DAISYSTATE_IS_CHILD,
        YDaisyChain.DAISYSTATE_FIRMWARE_MISMATCH, YDaisyChain.DAISYSTATE_CHILD_MISSING and
        YDaisyChain.DAISYSTATE_CHILD_LOST corresponding to the state of the daisy-link between modules

        On failure, throws an exception or returns YDaisyChain.DAISYSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDaisyChain.DAISYSTATE_INVALID
        res = self._daisyState
        return res

    def get_childCount(self):
        """
        Returns the number of child nodes currently detected.

        @return an integer corresponding to the number of child nodes currently detected

        On failure, throws an exception or returns YDaisyChain.CHILDCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDaisyChain.CHILDCOUNT_INVALID
        res = self._childCount
        return res

    def get_requiredChildCount(self):
        """
        Returns the number of child nodes expected in normal conditions.

        @return an integer corresponding to the number of child nodes expected in normal conditions

        On failure, throws an exception or returns YDaisyChain.REQUIREDCHILDCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDaisyChain.REQUIREDCHILDCOUNT_INVALID
        res = self._requiredChildCount
        return res

    def set_requiredChildCount(self, newval):
        """
        Changes the number of child nodes expected in normal conditions.
        If the value is zero, no check is performed. If it is non-zero, the number
        child nodes is checked on startup and the status will change to error if
        the count does not match. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the number of child nodes expected in normal conditions

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("requiredChildCount", rest_val)

    @staticmethod
    def FindDaisyChain(func):
        """
        Retrieves a module chain for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the module chain is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDaisyChain.isOnline() to test if the module chain is
        indeed online at a given time. In case of ambiguity when looking for
        a module chain by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the module chain, for instance
                MyDevice.daisyChain.

        @return a YDaisyChain object allowing you to drive the module chain.
        """
        # obj
        obj = YFunction._FindFromCache("DaisyChain", func)
        if obj is None:
            obj = YDaisyChain(func)
            YFunction._AddToCache("DaisyChain", func, obj)
        return obj

    def nextDaisyChain(self):
        """
        Continues the enumeration of module chains started using yFirstDaisyChain().
        Caution: You can't make any assumption about the returned module chains order.
        If you want to find a specific a module chain, use DaisyChain.findDaisyChain()
        and a hardwareID or a logical name.

        @return a pointer to a YDaisyChain object, corresponding to
                a module chain currently online, or a None pointer
                if there are no more module chains to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YDaisyChain.FindDaisyChain(hwidRef.value)

#--- (end of YDaisyChain implementation)

#--- (YDaisyChain functions)

    @staticmethod
    def FirstDaisyChain():
        """
        Starts the enumeration of module chains currently accessible.
        Use the method YDaisyChain.nextDaisyChain() to iterate on
        next module chains.

        @return a pointer to a YDaisyChain object, corresponding to
                the first module chain currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("DaisyChain", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YDaisyChain.FindDaisyChain(serialRef.value + "." + funcIdRef.value)

#--- (end of YDaisyChain functions)
