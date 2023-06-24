# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_arithmeticsensor.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindArithmeticSensor(), the high-level API for ArithmeticSensor functions
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


#--- (YArithmeticSensor class start)
#noinspection PyProtectedMember
class YArithmeticSensor(YSensor):
    """
    The YArithmeticSensor class allows some Yoctopuce devices to compute in real-time
    values based on an arithmetic formula involving one or more measured signals as
    well as the temperature. As for any physical sensor, the computed values can be
    read by callback and stored in the built-in datalogger.

    """
    #--- (end of YArithmeticSensor class start)
    #--- (YArithmeticSensor return codes)
    #--- (end of YArithmeticSensor return codes)
    #--- (YArithmeticSensor dlldef)
    #--- (end of YArithmeticSensor dlldef)
    #--- (YArithmeticSensor yapiwrapper)
    #--- (end of YArithmeticSensor yapiwrapper)
    #--- (YArithmeticSensor definitions)
    DESCRIPTION_INVALID = YAPI.INVALID_STRING
    COMMAND_INVALID = YAPI.INVALID_STRING
    #--- (end of YArithmeticSensor definitions)

    def __init__(self, func):
        super(YArithmeticSensor, self).__init__(func)
        self._className = 'ArithmeticSensor'
        #--- (YArithmeticSensor attributes)
        self._callback = None
        self._description = YArithmeticSensor.DESCRIPTION_INVALID
        self._command = YArithmeticSensor.COMMAND_INVALID
        #--- (end of YArithmeticSensor attributes)

    #--- (YArithmeticSensor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("description"):
            self._description = json_val.getString("description")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YArithmeticSensor, self)._parseAttr(json_val)

    def set_unit(self, newval):
        """
        Changes the measuring unit for the arithmetic sensor.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the measuring unit for the arithmetic sensor

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("unit", rest_val)

    def get_description(self):
        """
        Returns a short informative description of the formula.

        @return a string corresponding to a short informative description of the formula

        On failure, throws an exception or returns YArithmeticSensor.DESCRIPTION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YArithmeticSensor.DESCRIPTION_INVALID
        res = self._description
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YArithmeticSensor.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindArithmeticSensor(func):
        """
        Retrieves an arithmetic sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the arithmetic sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YArithmeticSensor.isOnline() to test if the arithmetic sensor is
        indeed online at a given time. In case of ambiguity when looking for
        an arithmetic sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the arithmetic sensor, for instance
                RXUVOLT1.arithmeticSensor1.

        @return a YArithmeticSensor object allowing you to drive the arithmetic sensor.
        """
        # obj
        obj = YFunction._FindFromCache("ArithmeticSensor", func)
        if obj is None:
            obj = YArithmeticSensor(func)
            YFunction._AddToCache("ArithmeticSensor", func, obj)
        return obj

    def defineExpression(self, expr, descr):
        """
        Defines the arithmetic function by means of an algebraic expression. The expression
        may include references to device sensors, by their physical or logical name, to
        usual math functions and to auxiliary functions defined separately.

        @param expr : the algebraic expression defining the function.
        @param descr : short informative description of the expression.

        @return the current expression value if the call succeeds.

        On failure, throws an exception or returns YAPI.INVALID_DOUBLE.
        """
        # id
        # fname
        # content
        # data
        # diags
        # resval
        id = self.get_functionId()
        id = (id)[16: 16 + len(id) - 16]
        fname = "arithmExpr" + id + ".txt"

        content = "// " + descr + "\n" + expr
        data = self._uploadEx(fname, YString2Byte(content))
        diags = YByte2String(data)
        if not ((diags)[0: 0 + 8] == "Result: "):
            self._throw(YAPI.INVALID_ARGUMENT, diags)
            return YAPI.INVALID_DOUBLE
        resval = float((diags)[8: 8 + len(diags)-8])
        return resval

    def loadExpression(self):
        """
        Retrieves the algebraic expression defining the arithmetic function, as previously
        configured using the defineExpression function.

        @return a string containing the mathematical expression.

        On failure, throws an exception or returns a negative error code.
        """
        # id
        # fname
        # content
        # idx
        id = self.get_functionId()
        id = (id)[16: 16 + len(id) - 16]
        fname = "arithmExpr" + id + ".txt"

        content = YByte2String(self._download(fname))
        idx = content.find("\n")
        if idx > 0:
            content = (content)[idx+1: idx+1 + len(content)-(idx+1)]
        return content

    def defineAuxiliaryFunction(self, name, inputValues, outputValues):
        """
        Defines a auxiliary function by means of a table of reference points. Intermediate values
        will be interpolated between specified reference points. The reference points are given
        as pairs of floating point numbers.
        The auxiliary function will be available for use by all ArithmeticSensor objects of the
        device. Up to nine auxiliary function can be defined in a device, each containing up to
        96 reference points.

        @param name : auxiliary function name, up to 16 characters.
        @param inputValues : array of floating point numbers, corresponding to the function input value.
        @param outputValues : array of floating point numbers, corresponding to the output value
                desired for each of the input value, index by index.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # siz
        # defstr
        # idx
        # inputVal
        # outputVal
        # fname
        siz = len(inputValues)
        if not (siz > 1):
            self._throw(YAPI.INVALID_ARGUMENT, "auxiliary function must be defined by at least two points")
            return YAPI.INVALID_ARGUMENT
        if not (siz == len(outputValues)):
            self._throw(YAPI.INVALID_ARGUMENT, "table sizes mismatch")
            return YAPI.INVALID_ARGUMENT
        defstr = ""
        idx = 0
        while idx < siz:
            inputVal = inputValues[idx]
            outputVal = outputValues[idx]
            defstr = "" + defstr + "" + str(inputVal) + ":" + str(outputVal) + "\n"
            idx = idx + 1
        fname = "userMap" + name + ".txt"

        return self._upload(fname, YString2Byte(defstr))

    def loadAuxiliaryFunction(self, name, inputValues, outputValues):
        """
        Retrieves the reference points table defining an auxiliary function previously
        configured using the defineAuxiliaryFunction function.

        @param name : auxiliary function name, up to 16 characters.
        @param inputValues : array of floating point numbers, that is filled by the function
                with all the function reference input value.
        @param outputValues : array of floating point numbers, that is filled by the function
                output value for each of the input value, index by index.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # fname
        # defbin
        # siz

        fname = "userMap" + name + ".txt"
        defbin = self._download(fname)
        siz = len(defbin)
        if not (siz > 0):
            self._throw(YAPI.INVALID_ARGUMENT, "auxiliary function does not exist")
            return YAPI.INVALID_ARGUMENT
        del inputValues[:]
        del outputValues[:]
        # // FIXME: decode line by line
        return YAPI.SUCCESS

    def nextArithmeticSensor(self):
        """
        Continues the enumeration of arithmetic sensors started using yFirstArithmeticSensor().
        Caution: You can't make any assumption about the returned arithmetic sensors order.
        If you want to find a specific an arithmetic sensor, use ArithmeticSensor.findArithmeticSensor()
        and a hardwareID or a logical name.

        @return a pointer to a YArithmeticSensor object, corresponding to
                an arithmetic sensor currently online, or a None pointer
                if there are no more arithmetic sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YArithmeticSensor.FindArithmeticSensor(hwidRef.value)

#--- (end of YArithmeticSensor implementation)

#--- (YArithmeticSensor functions)

    @staticmethod
    def FirstArithmeticSensor():
        """
        Starts the enumeration of arithmetic sensors currently accessible.
        Use the method YArithmeticSensor.nextArithmeticSensor() to iterate on
        next arithmetic sensors.

        @return a pointer to a YArithmeticSensor object, corresponding to
                the first arithmetic sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("ArithmeticSensor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YArithmeticSensor.FindArithmeticSensor(serialRef.value + "." + funcIdRef.value)

#--- (end of YArithmeticSensor functions)
