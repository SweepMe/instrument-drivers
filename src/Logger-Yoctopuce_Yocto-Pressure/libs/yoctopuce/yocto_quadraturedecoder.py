# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_quadraturedecoder.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindQuadratureDecoder(), the high-level API for QuadratureDecoder functions
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


#--- (YQuadratureDecoder class start)
#noinspection PyProtectedMember
class YQuadratureDecoder(YSensor):
    """
    The YQuadratureDecoder class allows you to read and configure Yoctopuce quadrature decoders.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YQuadratureDecoder class start)
    #--- (YQuadratureDecoder return codes)
    #--- (end of YQuadratureDecoder return codes)
    #--- (YQuadratureDecoder dlldef)
    #--- (end of YQuadratureDecoder dlldef)
    #--- (YQuadratureDecoder yapiwrapper)
    #--- (end of YQuadratureDecoder yapiwrapper)
    #--- (YQuadratureDecoder definitions)
    SPEED_INVALID = YAPI.INVALID_DOUBLE
    DECODING_OFF = 0
    DECODING_ON = 1
    DECODING_INVALID = -1
    #--- (end of YQuadratureDecoder definitions)

    def __init__(self, func):
        super(YQuadratureDecoder, self).__init__(func)
        self._className = 'QuadratureDecoder'
        #--- (YQuadratureDecoder attributes)
        self._callback = None
        self._speed = YQuadratureDecoder.SPEED_INVALID
        self._decoding = YQuadratureDecoder.DECODING_INVALID
        #--- (end of YQuadratureDecoder attributes)

    #--- (YQuadratureDecoder implementation)
    def _parseAttr(self, json_val):
        if json_val.has("speed"):
            self._speed = round(json_val.getDouble("speed") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("decoding"):
            self._decoding = (json_val.getInt("decoding") > 0 if 1 else 0)
        super(YQuadratureDecoder, self)._parseAttr(json_val)

    def set_currentValue(self, newval):
        """
        Changes the current expected position of the quadrature decoder.
        Invoking this function implicitly activates the quadrature decoder.

        @param newval : a floating point number corresponding to the current expected position of the quadrature decoder

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("currentValue", rest_val)

    def get_speed(self):
        """
        Returns the increments frequency, in Hz.

        @return a floating point number corresponding to the increments frequency, in Hz

        On failure, throws an exception or returns YQuadratureDecoder.SPEED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YQuadratureDecoder.SPEED_INVALID
        res = self._speed
        return res

    def get_decoding(self):
        """
        Returns the current activation state of the quadrature decoder.

        @return either YQuadratureDecoder.DECODING_OFF or YQuadratureDecoder.DECODING_ON, according to the
        current activation state of the quadrature decoder

        On failure, throws an exception or returns YQuadratureDecoder.DECODING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YQuadratureDecoder.DECODING_INVALID
        res = self._decoding
        return res

    def set_decoding(self, newval):
        """
        Changes the activation state of the quadrature decoder.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : either YQuadratureDecoder.DECODING_OFF or YQuadratureDecoder.DECODING_ON, according
        to the activation state of the quadrature decoder

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("decoding", rest_val)

    @staticmethod
    def FindQuadratureDecoder(func):
        """
        Retrieves a quadrature decoder for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the quadrature decoder is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YQuadratureDecoder.isOnline() to test if the quadrature decoder is
        indeed online at a given time. In case of ambiguity when looking for
        a quadrature decoder by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the quadrature decoder, for instance
                YPWMRX01.quadratureDecoder.

        @return a YQuadratureDecoder object allowing you to drive the quadrature decoder.
        """
        # obj
        obj = YFunction._FindFromCache("QuadratureDecoder", func)
        if obj is None:
            obj = YQuadratureDecoder(func)
            YFunction._AddToCache("QuadratureDecoder", func, obj)
        return obj

    def nextQuadratureDecoder(self):
        """
        Continues the enumeration of quadrature decoders started using yFirstQuadratureDecoder().
        Caution: You can't make any assumption about the returned quadrature decoders order.
        If you want to find a specific a quadrature decoder, use QuadratureDecoder.findQuadratureDecoder()
        and a hardwareID or a logical name.

        @return a pointer to a YQuadratureDecoder object, corresponding to
                a quadrature decoder currently online, or a None pointer
                if there are no more quadrature decoders to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YQuadratureDecoder.FindQuadratureDecoder(hwidRef.value)

#--- (end of YQuadratureDecoder implementation)

#--- (YQuadratureDecoder functions)

    @staticmethod
    def FirstQuadratureDecoder():
        """
        Starts the enumeration of quadrature decoders currently accessible.
        Use the method YQuadratureDecoder.nextQuadratureDecoder() to iterate on
        next quadrature decoders.

        @return a pointer to a YQuadratureDecoder object, corresponding to
                the first quadrature decoder currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("QuadratureDecoder", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YQuadratureDecoder.FindQuadratureDecoder(serialRef.value + "." + funcIdRef.value)

#--- (end of YQuadratureDecoder functions)
