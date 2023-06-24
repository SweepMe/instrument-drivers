# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_segmenteddisplay.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindSegmentedDisplay(), the high-level API for SegmentedDisplay functions
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


#--- (YSegmentedDisplay class start)
#noinspection PyProtectedMember
class YSegmentedDisplay(YFunction):
    """
    The SegmentedDisplay class allows you to drive segmented displays.

    """
    #--- (end of YSegmentedDisplay class start)
    #--- (YSegmentedDisplay return codes)
    #--- (end of YSegmentedDisplay return codes)
    #--- (YSegmentedDisplay dlldef)
    #--- (end of YSegmentedDisplay dlldef)
    #--- (YSegmentedDisplay yapiwrapper)
    #--- (end of YSegmentedDisplay yapiwrapper)
    #--- (YSegmentedDisplay definitions)
    DISPLAYEDTEXT_INVALID = YAPI.INVALID_STRING
    DISPLAYMODE_DISCONNECTED = 0
    DISPLAYMODE_MANUAL = 1
    DISPLAYMODE_AUTO1 = 2
    DISPLAYMODE_AUTO60 = 3
    DISPLAYMODE_INVALID = -1
    #--- (end of YSegmentedDisplay definitions)

    def __init__(self, func):
        super(YSegmentedDisplay, self).__init__(func)
        self._className = 'SegmentedDisplay'
        #--- (YSegmentedDisplay attributes)
        self._callback = None
        self._displayedText = YSegmentedDisplay.DISPLAYEDTEXT_INVALID
        self._displayMode = YSegmentedDisplay.DISPLAYMODE_INVALID
        #--- (end of YSegmentedDisplay attributes)

    #--- (YSegmentedDisplay implementation)
    def _parseAttr(self, json_val):
        if json_val.has("displayedText"):
            self._displayedText = json_val.getString("displayedText")
        if json_val.has("displayMode"):
            self._displayMode = json_val.getInt("displayMode")
        super(YSegmentedDisplay, self)._parseAttr(json_val)

    def get_displayedText(self):
        """
        Returns the text currently displayed on the screen.

        @return a string corresponding to the text currently displayed on the screen

        On failure, throws an exception or returns YSegmentedDisplay.DISPLAYEDTEXT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSegmentedDisplay.DISPLAYEDTEXT_INVALID
        res = self._displayedText
        return res

    def set_displayedText(self, newval):
        """
        Changes the text currently displayed on the screen.

        @param newval : a string corresponding to the text currently displayed on the screen

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("displayedText", rest_val)

    def get_displayMode(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSegmentedDisplay.DISPLAYMODE_INVALID
        res = self._displayMode
        return res

    def set_displayMode(self, newval):
        rest_val = str(newval)
        return self._setAttr("displayMode", rest_val)

    @staticmethod
    def FindSegmentedDisplay(func):
        """
        Retrieves a segmented display for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the segmented display is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSegmentedDisplay.isOnline() to test if the segmented display is
        indeed online at a given time. In case of ambiguity when looking for
        a segmented display by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the segmented display, for instance
                MyDevice.segmentedDisplay.

        @return a YSegmentedDisplay object allowing you to drive the segmented display.
        """
        # obj
        obj = YFunction._FindFromCache("SegmentedDisplay", func)
        if obj is None:
            obj = YSegmentedDisplay(func)
            YFunction._AddToCache("SegmentedDisplay", func, obj)
        return obj

    def nextSegmentedDisplay(self):
        """
        Continues the enumeration of segmented displays started using yFirstSegmentedDisplay().
        Caution: You can't make any assumption about the returned segmented displays order.
        If you want to find a specific a segmented display, use SegmentedDisplay.findSegmentedDisplay()
        and a hardwareID or a logical name.

        @return a pointer to a YSegmentedDisplay object, corresponding to
                a segmented display currently online, or a None pointer
                if there are no more segmented displays to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YSegmentedDisplay.FindSegmentedDisplay(hwidRef.value)

#--- (end of YSegmentedDisplay implementation)

#--- (YSegmentedDisplay functions)

    @staticmethod
    def FirstSegmentedDisplay():
        """
        Starts the enumeration of segmented displays currently accessible.
        Use the method YSegmentedDisplay.nextSegmentedDisplay() to iterate on
        next segmented displays.

        @return a pointer to a YSegmentedDisplay object, corresponding to
                the first segmented display currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("SegmentedDisplay", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YSegmentedDisplay.FindSegmentedDisplay(serialRef.value + "." + funcIdRef.value)

#--- (end of YSegmentedDisplay functions)
