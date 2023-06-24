# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_longitude.py 39658 2020-03-12 15:36:29Z seb $
#
#  Implements yFindLongitude(), the high-level API for Longitude functions
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


#--- (YLongitude class start)
#noinspection PyProtectedMember
class YLongitude(YSensor):
    """
    The YLongitude class allows you to read and configure Yoctopuce longitude sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YLongitude class start)
    #--- (YLongitude return codes)
    #--- (end of YLongitude return codes)
    #--- (YLongitude dlldef)
    #--- (end of YLongitude dlldef)
    #--- (YLongitude yapiwrapper)
    #--- (end of YLongitude yapiwrapper)
    #--- (YLongitude definitions)
    #--- (end of YLongitude definitions)

    def __init__(self, func):
        super(YLongitude, self).__init__(func)
        self._className = 'Longitude'
        #--- (YLongitude attributes)
        self._callback = None
        #--- (end of YLongitude attributes)

    #--- (YLongitude implementation)
    def _parseAttr(self, json_val):
        super(YLongitude, self)._parseAttr(json_val)

    @staticmethod
    def FindLongitude(func):
        """
        Retrieves a longitude sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the longitude sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YLongitude.isOnline() to test if the longitude sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a longitude sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the longitude sensor, for instance
                YGNSSMK2.longitude.

        @return a YLongitude object allowing you to drive the longitude sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Longitude", func)
        if obj is None:
            obj = YLongitude(func)
            YFunction._AddToCache("Longitude", func, obj)
        return obj

    def nextLongitude(self):
        """
        Continues the enumeration of longitude sensors started using yFirstLongitude().
        Caution: You can't make any assumption about the returned longitude sensors order.
        If you want to find a specific a longitude sensor, use Longitude.findLongitude()
        and a hardwareID or a logical name.

        @return a pointer to a YLongitude object, corresponding to
                a longitude sensor currently online, or a None pointer
                if there are no more longitude sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YLongitude.FindLongitude(hwidRef.value)

#--- (end of YLongitude implementation)

#--- (YLongitude functions)

    @staticmethod
    def FirstLongitude():
        """
        Starts the enumeration of longitude sensors currently accessible.
        Use the method YLongitude.nextLongitude() to iterate on
        next longitude sensors.

        @return a pointer to a YLongitude object, corresponding to
                the first longitude sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Longitude", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YLongitude.FindLongitude(serialRef.value + "." + funcIdRef.value)

#--- (end of YLongitude functions)
