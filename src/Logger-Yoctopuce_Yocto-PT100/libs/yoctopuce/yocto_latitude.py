# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_latitude.py 39658 2020-03-12 15:36:29Z seb $
#
#  Implements yFindLatitude(), the high-level API for Latitude functions
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


#--- (YLatitude class start)
#noinspection PyProtectedMember
class YLatitude(YSensor):
    """
    The YLatitude class allows you to read and configure Yoctopuce latitude sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YLatitude class start)
    #--- (YLatitude return codes)
    #--- (end of YLatitude return codes)
    #--- (YLatitude dlldef)
    #--- (end of YLatitude dlldef)
    #--- (YLatitude yapiwrapper)
    #--- (end of YLatitude yapiwrapper)
    #--- (YLatitude definitions)
    #--- (end of YLatitude definitions)

    def __init__(self, func):
        super(YLatitude, self).__init__(func)
        self._className = 'Latitude'
        #--- (YLatitude attributes)
        self._callback = None
        #--- (end of YLatitude attributes)

    #--- (YLatitude implementation)
    def _parseAttr(self, json_val):
        super(YLatitude, self)._parseAttr(json_val)

    @staticmethod
    def FindLatitude(func):
        """
        Retrieves a latitude sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the latitude sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YLatitude.isOnline() to test if the latitude sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a latitude sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the latitude sensor, for instance
                YGNSSMK2.latitude.

        @return a YLatitude object allowing you to drive the latitude sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Latitude", func)
        if obj is None:
            obj = YLatitude(func)
            YFunction._AddToCache("Latitude", func, obj)
        return obj

    def nextLatitude(self):
        """
        Continues the enumeration of latitude sensors started using yFirstLatitude().
        Caution: You can't make any assumption about the returned latitude sensors order.
        If you want to find a specific a latitude sensor, use Latitude.findLatitude()
        and a hardwareID or a logical name.

        @return a pointer to a YLatitude object, corresponding to
                a latitude sensor currently online, or a None pointer
                if there are no more latitude sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YLatitude.FindLatitude(hwidRef.value)

#--- (end of YLatitude implementation)

#--- (YLatitude functions)

    @staticmethod
    def FirstLatitude():
        """
        Starts the enumeration of latitude sensors currently accessible.
        Use the method YLatitude.nextLatitude() to iterate on
        next latitude sensors.

        @return a pointer to a YLatitude object, corresponding to
                the first latitude sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Latitude", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YLatitude.FindLatitude(serialRef.value + "." + funcIdRef.value)

#--- (end of YLatitude functions)
