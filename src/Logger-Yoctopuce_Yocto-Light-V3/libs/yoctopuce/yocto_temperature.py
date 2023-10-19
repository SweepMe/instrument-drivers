# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_temperature.py 39648 2020-03-12 13:56:10Z mvuilleu $
#
#  Implements yFindTemperature(), the high-level API for Temperature functions
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
import math
from yoctopuce.yocto_api import *


#--- (YTemperature class start)
#noinspection PyProtectedMember
class YTemperature(YSensor):
    """
    The YTemperature class allows you to read and configure Yoctopuce temperature sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the ability to configure some specific parameters
    for some sensors (connection type, temperature mapping table).

    """
    #--- (end of YTemperature class start)
    #--- (YTemperature return codes)
    #--- (end of YTemperature return codes)
    #--- (YTemperature dlldef)
    #--- (end of YTemperature dlldef)
    #--- (YTemperature yapiwrapper)
    #--- (end of YTemperature yapiwrapper)
    #--- (YTemperature definitions)
    SIGNALVALUE_INVALID = YAPI.INVALID_DOUBLE
    SIGNALUNIT_INVALID = YAPI.INVALID_STRING
    COMMAND_INVALID = YAPI.INVALID_STRING
    SENSORTYPE_DIGITAL = 0
    SENSORTYPE_TYPE_K = 1
    SENSORTYPE_TYPE_E = 2
    SENSORTYPE_TYPE_J = 3
    SENSORTYPE_TYPE_N = 4
    SENSORTYPE_TYPE_R = 5
    SENSORTYPE_TYPE_S = 6
    SENSORTYPE_TYPE_T = 7
    SENSORTYPE_PT100_4WIRES = 8
    SENSORTYPE_PT100_3WIRES = 9
    SENSORTYPE_PT100_2WIRES = 10
    SENSORTYPE_RES_OHM = 11
    SENSORTYPE_RES_NTC = 12
    SENSORTYPE_RES_LINEAR = 13
    SENSORTYPE_RES_INTERNAL = 14
    SENSORTYPE_IR = 15
    SENSORTYPE_RES_PT1000 = 16
    SENSORTYPE_CHANNEL_OFF = 17
    SENSORTYPE_INVALID = -1
    #--- (end of YTemperature definitions)

    def __init__(self, func):
        super(YTemperature, self).__init__(func)
        self._className = 'Temperature'
        #--- (YTemperature attributes)
        self._callback = None
        self._sensorType = YTemperature.SENSORTYPE_INVALID
        self._signalValue = YTemperature.SIGNALVALUE_INVALID
        self._signalUnit = YTemperature.SIGNALUNIT_INVALID
        self._command = YTemperature.COMMAND_INVALID
        #--- (end of YTemperature attributes)

    #--- (YTemperature implementation)
    def _parseAttr(self, json_val):
        if json_val.has("sensorType"):
            self._sensorType = json_val.getInt("sensorType")
        if json_val.has("signalValue"):
            self._signalValue = round(json_val.getDouble("signalValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("signalUnit"):
            self._signalUnit = json_val.getString("signalUnit")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YTemperature, self)._parseAttr(json_val)

    def set_unit(self, newval):
        """
        Changes the measuring unit for the measured temperature. That unit is a string.
        If that strings end with the letter F all temperatures values will returned in
        Fahrenheit degrees. If that String ends with the letter K all values will be
        returned in Kelvin degrees. If that string ends with the letter C all values will be
        returned in Celsius degrees.  If the string ends with any other character the
        change will be ignored. Remember to call the
        saveToFlash() method of the module if the modification must be kept.
        WARNING: if a specific calibration is defined for the temperature function, a
        unit system change will probably break it.

        @param newval : a string corresponding to the measuring unit for the measured temperature

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("unit", rest_val)

    def get_sensorType(self):
        """
        Returns the temperature sensor type.

        @return a value among YTemperature.SENSORTYPE_DIGITAL, YTemperature.SENSORTYPE_TYPE_K,
        YTemperature.SENSORTYPE_TYPE_E, YTemperature.SENSORTYPE_TYPE_J, YTemperature.SENSORTYPE_TYPE_N,
        YTemperature.SENSORTYPE_TYPE_R, YTemperature.SENSORTYPE_TYPE_S, YTemperature.SENSORTYPE_TYPE_T,
        YTemperature.SENSORTYPE_PT100_4WIRES, YTemperature.SENSORTYPE_PT100_3WIRES,
        YTemperature.SENSORTYPE_PT100_2WIRES, YTemperature.SENSORTYPE_RES_OHM,
        YTemperature.SENSORTYPE_RES_NTC, YTemperature.SENSORTYPE_RES_LINEAR,
        YTemperature.SENSORTYPE_RES_INTERNAL, YTemperature.SENSORTYPE_IR,
        YTemperature.SENSORTYPE_RES_PT1000 and YTemperature.SENSORTYPE_CHANNEL_OFF corresponding to the
        temperature sensor type

        On failure, throws an exception or returns YTemperature.SENSORTYPE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YTemperature.SENSORTYPE_INVALID
        res = self._sensorType
        return res

    def set_sensorType(self, newval):
        """
        Changes the temperature sensor type.  This function is used
        to define the type of thermocouple (K,E...) used with the device.
        It has no effect if module is using a digital sensor or a thermistor.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YTemperature.SENSORTYPE_DIGITAL, YTemperature.SENSORTYPE_TYPE_K,
        YTemperature.SENSORTYPE_TYPE_E, YTemperature.SENSORTYPE_TYPE_J, YTemperature.SENSORTYPE_TYPE_N,
        YTemperature.SENSORTYPE_TYPE_R, YTemperature.SENSORTYPE_TYPE_S, YTemperature.SENSORTYPE_TYPE_T,
        YTemperature.SENSORTYPE_PT100_4WIRES, YTemperature.SENSORTYPE_PT100_3WIRES,
        YTemperature.SENSORTYPE_PT100_2WIRES, YTemperature.SENSORTYPE_RES_OHM,
        YTemperature.SENSORTYPE_RES_NTC, YTemperature.SENSORTYPE_RES_LINEAR,
        YTemperature.SENSORTYPE_RES_INTERNAL, YTemperature.SENSORTYPE_IR,
        YTemperature.SENSORTYPE_RES_PT1000 and YTemperature.SENSORTYPE_CHANNEL_OFF corresponding to the
        temperature sensor type

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("sensorType", rest_val)

    def get_signalValue(self):
        """
        Returns the current value of the electrical signal measured by the sensor.

        @return a floating point number corresponding to the current value of the electrical signal
        measured by the sensor

        On failure, throws an exception or returns YTemperature.SIGNALVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YTemperature.SIGNALVALUE_INVALID
        res = round(self._signalValue * 1000) / 1000
        return res

    def get_signalUnit(self):
        """
        Returns the measuring unit of the electrical signal used by the sensor.

        @return a string corresponding to the measuring unit of the electrical signal used by the sensor

        On failure, throws an exception or returns YTemperature.SIGNALUNIT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YTemperature.SIGNALUNIT_INVALID
        res = self._signalUnit
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YTemperature.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindTemperature(func):
        """
        Retrieves a temperature sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the temperature sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YTemperature.isOnline() to test if the temperature sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a temperature sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the temperature sensor, for instance
                METEOMK2.temperature.

        @return a YTemperature object allowing you to drive the temperature sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Temperature", func)
        if obj is None:
            obj = YTemperature(func)
            YFunction._AddToCache("Temperature", func, obj)
        return obj

    def set_ntcParameters(self, res25, beta):
        """
        Configures NTC thermistor parameters in order to properly compute the temperature from
        the measured resistance. For increased precision, you can enter a complete mapping
        table using set_thermistorResponseTable. This function can only be used with a
        temperature sensor based on thermistors.

        @param res25 : thermistor resistance at 25 degrees Celsius
        @param beta : Beta value

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # t0
        # t1
        # res100
        tempValues = []
        resValues = []
        t0 = 25.0+275.15
        t1 = 100.0+275.15
        res100 = res25 * math.exp(beta*(1.0/t1 - 1.0/t0))
        del tempValues[:]
        del resValues[:]
        tempValues.append(25.0)
        resValues.append(res25)
        tempValues.append(100.0)
        resValues.append(res100)


        return self.set_thermistorResponseTable(tempValues, resValues)

    def set_thermistorResponseTable(self, tempValues, resValues):
        """
        Records a thermistor response table, in order to interpolate the temperature from
        the measured resistance. This function can only be used with a temperature
        sensor based on thermistors.

        @param tempValues : array of floating point numbers, corresponding to all
                temperatures (in degrees Celsius) for which the resistance of the
                thermistor is specified.
        @param resValues : array of floating point numbers, corresponding to the resistance
                values (in Ohms) for each of the temperature included in the first
                argument, index by index.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # siz
        # res
        # idx
        # found
        # prev
        # curr
        # currTemp
        # idxres
        siz = len(tempValues)
        if not (siz >= 2):
            self._throw(YAPI.INVALID_ARGUMENT, "thermistor response table must have at least two points")
            return YAPI.INVALID_ARGUMENT
        if not (siz == len(resValues)):
            self._throw(YAPI.INVALID_ARGUMENT, "table sizes mismatch")
            return YAPI.INVALID_ARGUMENT

        res = self.set_command("Z")
        if not (res==YAPI.SUCCESS):
            self._throw(YAPI.IO_ERROR, "unable to reset thermistor parameters")
            return YAPI.IO_ERROR
        # // add records in growing resistance value
        found = 1
        prev = 0.0
        while found > 0:
            found = 0
            curr = 99999999.0
            currTemp = -999999.0
            idx = 0
            while idx < siz:
                idxres = resValues[idx]
                if (idxres > prev) and (idxres < curr):
                    curr = idxres
                    currTemp = tempValues[idx]
                    found = 1
                idx = idx + 1
            if found > 0:
                res = self.set_command("m" + str(int(round(1000*curr))) + ":" + str(int(round(1000*currTemp))))
                if not (res==YAPI.SUCCESS):
                    self._throw(YAPI.IO_ERROR, "unable to reset thermistor parameters")
                    return YAPI.IO_ERROR
                prev = curr
        return YAPI.SUCCESS

    def loadThermistorResponseTable(self, tempValues, resValues):
        """
        Retrieves the thermistor response table previously configured using the
        set_thermistorResponseTable function. This function can only be used with a
        temperature sensor based on thermistors.

        @param tempValues : array of floating point numbers, that is filled by the function
                with all temperatures (in degrees Celsius) for which the resistance
                of the thermistor is specified.
        @param resValues : array of floating point numbers, that is filled by the function
                with the value (in Ohms) for each of the temperature included in the
                first argument, index by index.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # id
        # bin_json
        paramlist = []
        templist = []
        # siz
        # idx
        # temp
        # found
        # prev
        # curr
        # currRes
        del tempValues[:]
        del resValues[:]

        id = self.get_functionId()
        id = (id)[11: 11 + len(id) - 11]
        if id == "":
            id = "1"
        bin_json = self._download("extra.json?page=" + id)
        paramlist = self._json_get_array(bin_json)
        # // first convert all temperatures to float
        siz = ((len(paramlist)) >> (1))
        del templist[:]
        idx = 0
        while idx < siz:
            temp = float(paramlist[2*idx+1])/1000.0
            templist.append(temp)
            idx = idx + 1
        # // then add records in growing temperature value
        del tempValues[:]
        del resValues[:]
        found = 1
        prev = -999999.0
        while found > 0:
            found = 0
            curr = 999999.0
            currRes = -999999.0
            idx = 0
            while idx < siz:
                temp = templist[idx]
                if (temp > prev) and (temp < curr):
                    curr = temp
                    currRes = float(paramlist[2*idx])/1000.0
                    found = 1
                idx = idx + 1
            if found > 0:
                tempValues.append(curr)
                resValues.append(currRes)
                prev = curr


        return YAPI.SUCCESS

    def nextTemperature(self):
        """
        Continues the enumeration of temperature sensors started using yFirstTemperature().
        Caution: You can't make any assumption about the returned temperature sensors order.
        If you want to find a specific a temperature sensor, use Temperature.findTemperature()
        and a hardwareID or a logical name.

        @return a pointer to a YTemperature object, corresponding to
                a temperature sensor currently online, or a None pointer
                if there are no more temperature sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YTemperature.FindTemperature(hwidRef.value)

#--- (end of YTemperature implementation)

#--- (YTemperature functions)

    @staticmethod
    def FirstTemperature():
        """
        Starts the enumeration of temperature sensors currently accessible.
        Use the method YTemperature.nextTemperature() to iterate on
        next temperature sensors.

        @return a pointer to a YTemperature object, corresponding to
                the first temperature sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Temperature", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YTemperature.FindTemperature(serialRef.value + "." + funcIdRef.value)

#--- (end of YTemperature functions)
