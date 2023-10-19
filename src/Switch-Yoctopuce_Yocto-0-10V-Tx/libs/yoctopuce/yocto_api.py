# -*- coding: utf-8 -*-
# *********************************************************************
# *
# * $Id: yocto_api.py 38914 2019-12-20 19:14:33Z mvuilleu $
# *
# * High-level programming interface, common to all modules
# *
# * - - - - - - - - - License information: - - - - - - - - -
# *
# *  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
# *
# *  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
# *  non-exclusive license to use, modify, copy and integrate this
# *  file into your software for the sole purpose of interfacing
# *  with Yoctopuce products.
# *
# *  You may reproduce and distribute copies of this file in
# *  source or object form, as long as the sole purpose of this
# *  code is to interface with Yoctopuce products. You must retain
# *  this notice in the distributed source file.
# *
# *  You should refer to Yoctopuce General Terms and Conditions
# *  for additional information regarding your rights and
# *  obligations.
# *
# *  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
# *  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
# *  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
# *  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
# *  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
# *  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
# *  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
# *  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
# *  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
# *  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
# *  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
# *  WARRANTY, OR OTHERWISE.
# *
# *********************************************************************/
from __future__ import division

__docformat__ = 'restructuredtext en'

import datetime
import ctypes
import platform
# import abc  (not supported in 2.5.x)
import random
import sys
import os
import time
import array
import binascii
from ctypes import *


#
#  PYTHON 2.x VS PYTHON 3.x compatibility check
#
def YByte2StringPython2x(binBuffer):
    return binBuffer.decode("latin-1")


def YString2BytePython2x(strBuffer):
    return strBuffer.encode("latin-1")


def YGetBytePython2x(binBuffer, idx):
    item = binBuffer[idx]
    if type(item) is int:
        return item
    return ord(item)


def YAddBytePython2x(binBuffer, b):
    return binBuffer + chr(b)


def YRelTickCountPython2x(dt):
    td = dt - datetime.datetime(1970, 1, 1)
    return int(round((td.seconds + td.days * 24 * 3600 * 1000) + td.microseconds / 1000))


def YByte2StringPython3x(binBuffer):
    return binBuffer.decode("latin-1")


def YString2BytePython3x(strBuffer):
    return strBuffer.encode("latin-1")


def YGetBytePython3x(binBuffer, l):
    return binBuffer[l]


def YAddBytePython3x(binBuffer, b):
    return binBuffer + bytes([b])


def YRelTickCountPython3x(dt):
    td = dt - datetime.datetime(1970, 1, 1)
    return int(round(td.total_seconds() * 1000.0))


YByte2String = None
YString2Byte = None
YGetByte = None
YAddByte = None
if sys.version_info < (3, 0):
    YByte2String = YByte2StringPython2x
    YString2Byte = YString2BytePython2x
    YGetByte = YGetBytePython2x
    YAddByte = YAddBytePython2x
    YRelTickCount = YRelTickCountPython2x
else:
    YByte2String = YByte2StringPython3x
    YString2Byte = YString2BytePython3x
    YGetByte = YGetBytePython3x
    YAddByte = YAddBytePython3x
    YRelTickCount = YRelTickCountPython3x

# Ugly global var for Python 2 compatibility
yLogFct = None
yDeviceLogFct = None
yArrivalFct = None
yRemovalFct = None
yChangeFct = None
yHubDiscoveryCallback = None


# This class is used to mimic "ByReference" parameter in function calls
class YRefParam:
    def __init__(self, initialValue=None):
        self.value = initialValue

    def __str__(self):
        return str(self.value)


class YAPI_Exception(Exception):
    def __init__(self, errType, errMsg):
        super(YAPI_Exception, self).__init__(errMsg)
        self.errorType = errType
        self.errorMessage = errMsg


# noinspection PyClassHasNoInit
class YJSONType:
    STRING, NUMBER, ARRAY, OBJECT = range(4)


# noinspection PyClassHasNoInit
class Tjstate:
    JSTART, JWAITFORNAME, JWAITFORENDOFNAME, JWAITFORCOLON, JWAITFORDATA, JWAITFORNEXTSTRUCTMEMBER, JWAITFORNEXTARRAYITEM, \
        JWAITFORSTRINGVALUE, JWAITFORSTRINGVALUE_ESC, JWAITFORINTVALUE, JWAITFORBOOLVALUE = range(11)


class YJSONContent(object):
    @staticmethod
    def ParseJson(data, start, stop):
        cur_pos = YJSONContent.SkipGarbage(data, start, stop)
        c = data[cur_pos]
        if c == '[':
            res = YJSONArray(data, start, stop)
        elif c == '{':
            res = YJSONObject(data, start, stop)
        elif c == '"':
            res = YJSONString(data, start, stop)
        else:
            res = YJSONNumber(data, start, stop)
        res.parse()
        return res

    def __init__(self, data, start, stop, typ):
        self._data = data
        self._data_start = start
        self._data_len = start
        self._data_boundary = stop
        self._type = typ

    def getJSONType(self):
        return self._type

    def parse(self):
        raise Exception("abstract methode")

    @staticmethod
    def SkipGarbage(data, start, stop):
        if stop <= start:
            return start
        while start < stop:
            sti = data[start]
            if sti != ' ' and sti != '\n' and sti != '\r':
                break
            start += 1
        return start

    def formatError(self, errmsg, cur_pos):
        ststart = cur_pos - 10
        stend = cur_pos + 10
        if ststart < 0:
            ststart = 0
        if stend > self._data_boundary:
            stend = self._data_boundary
        if self._data is not None:
            return errmsg + " near " + self._data[ststart: stend]
        return errmsg


class YJSONString(YJSONContent):
    def __init__(self, data, start, stop):
        super(YJSONString, self).__init__(data, start, stop, YJSONType.STRING)
        self._stringValue = None

    def parse(self):
        value = ""
        cur_pos = YJSONContent.SkipGarbage(self._data, self._data_start, self._data_boundary)

        if cur_pos >= self._data_boundary or self._data[cur_pos] != '"':
            raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("double quote was expected", cur_pos))
        cur_pos += 1
        str_start = cur_pos
        state = Tjstate.JWAITFORSTRINGVALUE
        while cur_pos < self._data_boundary:
            sti = self._data[cur_pos]
            if state == Tjstate.JWAITFORSTRINGVALUE:
                if sti == '\\':
                    value += self._data[str_start: cur_pos]
                    str_start = cur_pos
                    state = Tjstate.JWAITFORSTRINGVALUE_ESC
                elif sti == '"':
                    value += self._data[str_start: cur_pos]
                    self._stringValue = value
                    self._data_len = (cur_pos + 1) - self._data_start
                    return self._data_len
                elif sti < ' ':
                    raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                              self.formatError("invalid char: was expecting string value", cur_pos))
            elif state == Tjstate.JWAITFORSTRINGVALUE_ESC:
                value += sti
                state = Tjstate.JWAITFORSTRINGVALUE
                str_start = cur_pos + 1
            else:
                raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                          self.formatError("invalid state for YJSONObject", cur_pos))

            cur_pos += 1

        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("unexpected end of data", cur_pos))

    def toJSON(self):
        res = '"'
        le = len(self._stringValue)
        for i in range(0, le):
            c = self._stringValue[i]
            if c == '"':
                res += "\\\""
            elif c == '\\':
                res += "\\\\"
            elif c == '/':
                res += "\\/"
            elif c == '\b':
                res += "\\b"
            elif c == '\f':
                res += "\\f"
            elif c == '\n':
                res += "\\n"
            elif c == '\r':
                res += "\\r"
            elif c == '\t':
                res += "\\t"
            else:
                res += c
        res += '"'
        return res

    def getString(self):
        return self._stringValue

    def toString(self):
        return self._stringValue

    def setContent(self, value):
        self._stringValue = value


class YJSONNumber(YJSONContent):
    def __init__(self, data, start, stop):
        super(YJSONNumber, self).__init__(data, start, stop, YJSONType.NUMBER)
        self._intValue = 0
        self._doubleValue = 0
        self._isFloat = False

    def parse(self):
        neg = False
        cur_pos = YJSONContent.SkipGarbage(self._data, self._data_start, self._data_boundary)
        if cur_pos >= self._data_boundary or self._data is None:
            raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, "no data")
        sti = self._data[cur_pos]
        if sti == '-':
            neg = True
            cur_pos += 1
        start = cur_pos
        while cur_pos < self._data_boundary:
            sti = self._data[cur_pos]
            if sti == '.' and not self._isFloat:
                int_part = self._data[start: cur_pos]
                self._intValue = int(int_part)
                self._isFloat = True
            elif sti < '0' or sti > '9':
                numberpart = self._data[start: cur_pos]
                if self._isFloat:
                    self._doubleValue = float(numberpart)
                else:
                    self._intValue = int(numberpart)

                if neg:
                    self._doubleValue = 0 - self._doubleValue
                    self._intValue = 0 - self._intValue

                return cur_pos - self._data_start
            cur_pos += 1
        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("unexpected end of data", cur_pos))

    def toJSON(self):
        if self._isFloat:
            return str(self._doubleValue)
        else:
            return str(self._intValue)

    def getLong(self):
        if self._isFloat:
            return self._doubleValue
        else:
            return self._intValue

    def getInt(self):
        if self._isFloat:
            return self._doubleValue
        else:
            return self._intValue

    def getDouble(self):
        if self._isFloat:
            return self._doubleValue
        else:
            return self._intValue

    def toString(self):
        if self._isFloat:
            return str(self._doubleValue)
        else:
            return str(self._intValue)


class YJSONArray(YJSONContent):
    def __init__(self, data, start, stop):
        super(YJSONArray, self).__init__(data, start, stop, YJSONType.ARRAY)
        self._arrayValue = []

    def length(self):
        return len(self._arrayValue)

    def parse(self):
        cur_pos = YJSONContent.SkipGarbage(self._data, self._data_start, self._data_boundary)
        if cur_pos >= self._data_boundary or self._data[cur_pos] != '[':
            raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("Opening braces was expected", cur_pos))
        cur_pos += 1
        state = Tjstate.JWAITFORDATA

        while cur_pos < self._data_boundary:
            sti = self._data[cur_pos]
            if state == Tjstate.JWAITFORDATA:
                if sti == '{':
                    jobj = YJSONObject(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._arrayValue.append(jobj)
                    state = Tjstate.JWAITFORNEXTARRAYITEM
                    # cur_pos is already incremented
                    continue
                elif sti == '[':
                    jobj = YJSONArray(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._arrayValue.append(jobj)
                    state = Tjstate.JWAITFORNEXTARRAYITEM
                    # cur_pos is already incremented
                    continue
                elif sti == '"':
                    jobj = YJSONString(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._arrayValue.append(jobj)
                    state = Tjstate.JWAITFORNEXTARRAYITEM
                    # #cur_pos is already incremented
                    continue
                elif sti == '-' or ('0' <= sti <= '9'):
                    jobj = YJSONNumber(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._arrayValue.append(jobj)
                    state = Tjstate.JWAITFORNEXTARRAYITEM
                    # cur_pos is already incremented
                    continue
                elif sti == ']':
                    self._data_len = cur_pos + 1 - self._data_start
                    return self._data_len
                elif sti != ' ' and sti != '\n' and sti != '\r':
                    raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                              self.formatError("invalid char: was expecting  \",0..9,t or f", cur_pos))

            elif state == Tjstate.JWAITFORNEXTARRAYITEM:
                if sti == ',':
                    state = Tjstate.JWAITFORDATA
                elif sti == ']':
                    self._data_len = cur_pos + 1 - self._data_start
                    return self._data_len
                else:
                    if sti != ' ' and sti != '\n' and sti != '\r':
                        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                                  self.formatError("invalid char: was expecting ,", cur_pos))
            else:
                raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                          self.formatError("invalid state for YJSONObject", cur_pos))
            cur_pos += 1
        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("unexpected end of data", cur_pos))

    def getYJSONObject(self, i):
        if i >= len(self._arrayValue):
            return None
        return self._arrayValue[i]

    def getString(self, i):
        if i >= len(self._arrayValue):
            return None
        ystr = self._arrayValue[i]
        return ystr.getString()

    def get(self, i):
        if i >= len(self._arrayValue):
            return None
        return self._arrayValue[i]

    def getYJSONArray(self, i):
        if i >= len(self._arrayValue):
            return None
        return self._arrayValue[i]

    def getInt(self, i):
        if i >= len(self._arrayValue):
            return None
        ystr = self._arrayValue[i]
        return ystr.getInt()

    def getLong(self, i):
        if i >= len(self._arrayValue):
            return None
        ystr = self._arrayValue[i]
        return ystr.getLong()

    def getDouble(self, i):
        if i >= len(self._arrayValue):
            return None
        ystr = self._arrayValue[i]
        return ystr.getDouble()

    def put(self, flatAttr):
        strobj = YJSONString(None, 0, 0)
        strobj.setContent(flatAttr)
        self._arrayValue.append(strobj)

    def toJSON(self):
        res = '['
        sep = ""
        for yjsonContent in self._arrayValue:
            subres = yjsonContent.toJSON()
            res += sep
            res += subres
            sep = ","

        res += ']'
        return res

    def toString(self):
        res = '['
        sep = ""
        for yjsonContent in self._arrayValue:
            subres = yjsonContent.toString()
            res += sep
            res += subres
            sep = ","

        res += ']'
        return res


class YJSONObject(YJSONContent):
    def __init__(self, data, start, stop):
        super(YJSONObject, self).__init__(data, start, stop, YJSONType.OBJECT)
        self._parsed = {}
        self._keys = []

    def parse(self):
        current_name = ""
        name_start = self._data_start
        cur_pos = YJSONContent.SkipGarbage(self._data, self._data_start, self._data_boundary)
        if len(self._data) <= cur_pos or cur_pos >= self._data_boundary or self._data[cur_pos] != '{':
            raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("Opening braces was expected", cur_pos))

        cur_pos += 1
        state = Tjstate.JWAITFORNAME
        while cur_pos < self._data_boundary:
            sti = self._data[cur_pos]
            if state == Tjstate.JWAITFORNAME:
                if sti == '"':
                    state = Tjstate.JWAITFORENDOFNAME
                    name_start = cur_pos + 1
                elif sti == '}':
                    self._data_len = cur_pos + 1 - self._data_start
                    return self._data_len
                else:
                    if sti != ' ' and sti != '\n' and sti != '\r':
                        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                                  self.formatError("invalid char: was expecting \"", cur_pos))
            elif state == Tjstate.JWAITFORENDOFNAME:
                if sti == '"':
                    current_name = self._data[name_start: cur_pos]
                    state = Tjstate.JWAITFORCOLON
                else:
                    if sti < ' ':
                        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                                  self.formatError(
                                                      "invalid char: was expecting an identifier compliant char",
                                                      cur_pos))
            elif state == Tjstate.JWAITFORCOLON:
                if sti == ':':
                    state = Tjstate.JWAITFORDATA
                else:
                    if sti != ' ' and sti != '\n' and sti != '\r':
                        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                                  self.formatError("invalid char: was expecting \"", cur_pos))
            elif state == Tjstate.JWAITFORDATA:
                if sti == '{':
                    jobj = YJSONObject(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    self._parsed[current_name] = jobj
                    self._keys.append(current_name)
                    cur_pos += length
                    state = Tjstate.JWAITFORNEXTSTRUCTMEMBER
                    continue
                elif sti == '[':
                    jobj = YJSONArray(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._parsed[current_name] = jobj
                    self._keys.append(current_name)
                    state = Tjstate.JWAITFORNEXTSTRUCTMEMBER
                    continue
                elif sti == '"':
                    jobj = YJSONString(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._parsed[current_name] = jobj
                    self._keys.append(current_name)
                    state = Tjstate.JWAITFORNEXTSTRUCTMEMBER
                    continue
                elif sti == '-' or ('0' <= sti <= '9'):
                    jobj = YJSONNumber(self._data, cur_pos, self._data_boundary)
                    length = jobj.parse()
                    cur_pos += length
                    self._parsed[current_name] = jobj
                    self._keys.append(current_name)
                    state = Tjstate.JWAITFORNEXTSTRUCTMEMBER
                    continue
                elif sti != ' ' and sti != '\n' and sti != '\r':
                    raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                              self.formatError("invalid char: was expecting  \",0..9,t or f", cur_pos))

            elif state == Tjstate.JWAITFORNEXTSTRUCTMEMBER:
                if sti == ',':
                    state = Tjstate.JWAITFORNAME
                    name_start = cur_pos + 1
                elif sti == '}':
                    self._data_len = cur_pos + 1 - self._data_start
                    return self._data_len
                else:
                    if sti != ' ' and sti != '\n' and sti != '\r':
                        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                                  self.formatError("invalid char: was expecting ,", cur_pos))
            elif state == Tjstate.JWAITFORNEXTARRAYITEM or state == Tjstate.JWAITFORSTRINGVALUE or state == Tjstate.JWAITFORINTVALUE or state == Tjstate.JWAITFORBOOLVALUE:
                raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT,
                                          self.formatError("invalid state for YJSONObject", cur_pos))

            cur_pos += 1
        raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, self.formatError("unexpected end of data", cur_pos))

    def has(self, key):
        if key in self._parsed:
            return True
        return False

    def getYJSONObject(self, key):
        if key not in self._parsed:
            return None
        return self._parsed[key]

    def getYJSONString(self, key):
        if key not in self._parsed:
            return None
        return self._parsed[key]

    def getYJSONArray(self, key):
        if key not in self._parsed:
            return None
        return self._parsed[key]

    def getKeys(self):
        return self._parsed.keys()

    def getYJSONNumber(self, key):
        if key not in self._parsed:
            return None
        return self._parsed[key]

    def remove(self, key):
        self._parsed.pop(key, None)

    def getString(self, key):
        if key not in self._parsed:
            return ""
        ystr = self._parsed[key]
        return ystr.getString()

    def getInt(self, key):
        if key not in self._parsed:
            return None
        yint = self._parsed[key]
        return yint.getInt()

    def get(self, key):
        if key not in self._parsed:
            return None
        return self._parsed[key]

    def getLong(self, key):
        if key not in self._parsed:
            return None
        yint = self._parsed[key]
        return yint.getLong()

    def getDouble(self, key):
        if key not in self._parsed:
            return None
        yint = self._parsed[key]
        return yint.getDouble()

    def toJSON(self):
        res = '{'
        sep = ""
        for key in self._parsed.keys():
            subContent = self._parsed[key]
            subres = subContent.toJSON()
            res += sep
            res += '"'
            res += key
            res += "\":"
            res += subres
            sep = ","
        res += '}'
        return res

    def toString(self):
        res = '{'
        sep = ""
        for key in self._parsed.keys():
            subContent = self._parsed[key]
            subres = subContent.toString()
            res += sep
            res += key
            res += "=>"
            res += subres
            sep = ","
        res += '}'
        return res

    def parseWithRef(self, reference):
        if reference is not None:
            try:
                yzon = YJSONArray(self._data, self._data_start, self._data_boundary)
                yzon.parse()
                self.convert(reference, yzon)
                return
            except YAPI.YAPI_Exception:
                self.parse()
                return
        self.parse()

    def convert(self, reference, newArray):
        length = newArray.length()
        for i in range(0, length):
            key = reference.getKeyFromIdx(i)
            new_item = newArray.get(i)
            reference_item = reference.get(key)

            if new_item.getJSONType() == reference_item.getJSONType():
                self._parsed[key] = new_item
                self._keys.append(key)
            elif new_item.getJSONType() == YJSONType.ARRAY and reference_item.getJSONType() == YJSONType.OBJECT:
                jobj = YJSONObject(new_item._data, new_item._data_start, reference_item._data_boundary)
                jobj.convert(reference_item, new_item)
                self._parsed[key] = jobj
                self._keys.append(key)
            else:
                raise YAPI.YAPI_Exception(YAPI.INVALID_ARGUMENT, "Unable to convert %s to %s" % (
                    new_item.getJSONType(), reference.getJSONType()))

    def getKeyFromIdx(self, i):
        return self._keys[i]


#--- (generated code: YAPIContext class start)
#noinspection PyProtectedMember
class YAPIContext(object):
    #--- (end of generated code: YAPIContext class start)
    #--- (generated code: YAPIContext return codes)
    #--- (end of generated code: YAPIContext return codes)
    #--- (generated code: YAPIContext dlldef)
    #--- (end of generated code: YAPIContext dlldef)
    #--- (generated code: YAPIContext definitions)
    #--- (end of generated code: YAPIContext definitions)

    def __init__(self):
        #--- (generated code: YAPIContext attributes)
        self._defaultCacheValidity = 5
        #--- (end of generated code: YAPIContext attributes)

    #--- (generated code: YAPIContext implementation)
    def SetDeviceListValidity(self, deviceListValidity):
        """
        Modifies the delay between each forced enumeration of the used YoctoHubs.
        By default, the library performs a full enumeration every 10 seconds.
        To reduce network traffic, you can increase this delay.
        It's particularly useful when a YoctoHub is connected to the GSM network
        where traffic is billed. This parameter doesn't impact modules connected by USB,
        nor the working of module arrival/removal callbacks.
        Note: you must call this function after yInitAPI.

        @param deviceListValidity : nubmer of seconds between each enumeration.
        @noreturn
        """
        YAPI._yapiSetNetDevListValidity(deviceListValidity)

    def GetDeviceListValidity(self):
        """
        Returns the delay between each forced enumeration of the used YoctoHubs.
        Note: you must call this function after yInitAPI.

        @return the number of seconds between each enumeration.
        """
        # res
        res = YAPI._yapiGetNetDevListValidity()
        return res

    def SetNetworkTimeout(self, networkMsTimeout):
        """
        Modifies the network connection delay for yRegisterHub() and yUpdateDeviceList().
        This delay impacts only the YoctoHubs and VirtualHub
        which are accessible through the network. By default, this delay is of 20000 milliseconds,
        but depending or you network you may want to change this delay,
        gor example if your network infrastructure is based on a GSM connection.

        @param networkMsTimeout : the network connection delay in milliseconds.
        @noreturn
        """
        YAPI._yapiSetNetworkTimeout(networkMsTimeout)

    def GetNetworkTimeout(self):
        """
        Returns the network connection delay for yRegisterHub() and yUpdateDeviceList().
        This delay impacts only the YoctoHubs and VirtualHub
        which are accessible through the network. By default, this delay is of 20000 milliseconds,
        but depending or you network you may want to change this delay,
        for example if your network infrastructure is based on a GSM connection.

        @return the network connection delay in milliseconds.
        """
        # res
        res = YAPI._yapiGetNetworkTimeout()
        return res

    def SetCacheValidity(self, cacheValidityMs):
        """
        Change the validity period of the data loaded by the library.
        By default, when accessing a module, all the attributes of the
        module functions are automatically kept in cache for the standard
        duration (5 ms). This method can be used to change this standard duration,
        for example in order to reduce network or USB traffic. This parameter
        does not affect value change callbacks
        Note: This function must be called after yInitAPI.

        @param cacheValidityMs : an integer corresponding to the validity attributed to the
                loaded function parameters, in milliseconds.
        @noreturn
        """
        self._defaultCacheValidity = cacheValidityMs

    def GetCacheValidity(self):
        """
        Returns the validity period of the data loaded by the library.
        This method returns the cache validity of all attributes
        module functions.
        Note: This function must be called after yInitAPI .

        @return an integer corresponding to the validity attributed to the
                loaded function parameters, in milliseconds
        """
        return self._defaultCacheValidity

#--- (end of generated code: YAPIContext implementation)

#--- (generated code: YAPIContext functions)
#--- (end of generated code: YAPIContext functions)


# noinspection PyClassHasNoInit,PyProtectedMember
# noinspection PyUnresolvedReferences
class YAPI:
    # noinspection PyUnresolvedReferences
    class YPCHAR(ctypes.Structure):
        _fields_ = [("buffer", ctypes.c_char_p)]

    # Switch to turn off exceptions and use return codes instead, for source-code compatibility
    # with languages without exception support like C
    ExceptionsDisabled = False
    _apiInitialized = False
    _ydllLoaded = False

    # Default cache validity (in [ms]) before reloading data from device. This saves a lots of traffic.
    # Note that a value under 2 ms makes little sense since a USB bus itself has a 2ms round-trip period

    DefaultCacheValidity = datetime.timedelta(milliseconds=5)
    INVALID_STRING = "!INVALID!"
    INVALID_DOUBLE = -1.79769313486231E+308
    MIN_DOUBLE = float('-inf')
    MAX_DOUBLE = float('inf')
    INVALID_INT = -2147483648
    INVALID_UINT = -1
    INVALID_LONG = -9223372036854775807

    # yInitAPI argument
    Y_DETECT_NONE = 0
    Y_DETECT_USB = 1
    Y_DETECT_NET = 2
    Y_RESEND_MISSING_PKT = 4
    Y_DETECT_ALL = Y_DETECT_USB | Y_DETECT_NET

    DETECT_NONE = 0
    DETECT_USB = 1
    DETECT_NET = 2
    RESEND_MISSING_PKT = 4
    DETECT_ALL = DETECT_USB | DETECT_NET

    YOCTO_API_VERSION_STR = "1.10"
    YOCTO_API_VERSION_BCD = 0x0110

    YOCTO_API_BUILD_NO = "40411"
    YOCTO_DEFAULT_PORT = 4444
    YOCTO_VENDORID = 0x24e0
    YOCTO_DEVID_FACTORYBOOT = 1

    YOCTO_DEVID_BOOTLOADER = 2
    YOCTO_ERRMSG_LEN = 256
    YOCTO_MANUFACTURER_LEN = 20
    YOCTO_SERIAL_LEN = 20
    YOCTO_BASE_SERIAL_LEN = 8
    YOCTO_PRODUCTNAME_LEN = 28
    YOCTO_FIRMWARE_LEN = 22
    YOCTO_LOGICAL_LEN = 20
    YOCTO_FUNCTION_LEN = 20
    HASH_BUF_SIZE = 28

    # Size of the data (can be non null terminated)
    YOCTO_PUBVAL_SIZE = 6
    # Temporary storage, > YOCTO_PUBVAL_SIZE
    YOCTO_PUBVAL_LEN = 16
    YOCTO_PASS_LEN = 20
    YOCTO_REALM_LEN = 20
    YIOHDL_SIZE = 8
    INVALID_YHANDLE = 0

    YOCTO_CALIB_TYPE_OFS = 30

    yUnknowSize = 1024

    C_INTSIZE = 4  # we assume an int size is 4 byte

    _PlugEvents = []
    _DataEvents = []
    _CalibHandlers = {}

    #  private extern static void DllCallTest(ref yDeviceSt data);
    # _DllCallTest = yApiCLib.DllCallTest
    # _DllCallTest.restypes = ctypes.c_int
    # _DllCallTest.argtypes = [ctypes.c_void_p]

    _yApiCLibFile = ""
    _yApiCLibFileFallback = ""
    _yApiCLib = None
    _yapiContext = YAPIContext()

    @staticmethod
    def SelectArchitecture(arch):
        """
        Select the architecture or the library to be loaded to access to USB.
        By default, the Python library automatically detects the appropriate
        library to use. However, for Linux ARM, it not possible to reliably
        distinguish between a Hard Float (armhf) and a Soft Float (armel)
        install. For in this case, it is therefore recommended to manually
        select the proper architecture by calling SelectArchitecture()
        before any other call to the library.

        @param arch : A string containing the architecture to use.
                Possibles value are: "armhf","armel",
                "aarch64","i386","x86_64",
                "32bit", "64bit"

        @return nothing.

        On failure, throws an exception.
        """

        libpath = os.path.dirname(__file__)
        system = platform.system()
        if libpath == '':
            libpath = '.'
        if system == 'Windows':
            if arch == '32bit':
                YAPI._yApiCLibFile = libpath + "\\cdll\\yapi.dll"
            elif arch == '64bit':
                YAPI._yApiCLibFile = libpath + "\\cdll\\yapi64.dll"
            else:
                raise NotImplementedError(
                    "unsupported windows architecture (" + arch + "), contact support@yoctopuce.com.")
        #
        #  LINUX (INTEL + ARM)
        #
        elif system == 'Linux':
            if arch == "armhf":
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi-armhf.so"
            elif arch == "armel":
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi-armel.so"
            elif arch == 'i386':
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi-i386.so"
            elif arch == 'x86_64':
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi-amd64.so"
            elif arch == 'aarch64':
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi-aarch64.so"
            else:
                raise NotImplementedError(
                    "unsupported linux architecture (" + arch + "), contact support@yoctopuce.com.")
        #
        #  Mac OS X
        #
        elif system == 'Darwin':
            if arch == 'x86_64':
                YAPI._yApiCLibFile = libpath + "/cdll/libyapi.dylib"
            else:
                raise NotImplementedError(
                    "unsupported Mac OS architecture (" + arch + "), contact support@yoctopuce.com.")
        #
        #  UNKNOWN, contact Yoctopuce support :-)
        #
        else:
            raise NotImplementedError("unsupported platform " + system + ", contact support@yoctopuce.com.")

    @staticmethod
    def yloadYapiCDLL():
        if YAPI._yApiCLibFile == "":
            libpath = os.path.dirname(__file__)
            system = platform.system()
            arch = platform.architecture()[0]
            machine = platform.machine()
            if libpath == '':
                libpath = '.'
                #
            #  WINDOWS
            #
            if system == 'Windows':
                if arch == '32bit':
                    YAPI._yApiCLibFile = libpath + "\\cdll\\yapi.dll"
                elif arch == '64bit':
                    YAPI._yApiCLibFile = libpath + "\\cdll\\yapi64.dll"
                else:
                    raise NotImplementedError(
                        "unsupported windows architecture (" + arch + "), contact support@yoctopuce.com.")
            #
            #  LINUX (INTEL + ARM)
            #
            elif platform.system() == 'Linux':
                if machine.find("aarch64") >= 0:
                    YAPI._yApiCLibFile = libpath + "/cdll/libyapi-aarch64.so"
                    YAPI._yApiCLibFileFallback = libpath + "/cdll/libyapi-aarch64.so"
                elif machine.find("arm") >= 0:
                    YAPI._yApiCLibFile = libpath + "/cdll/libyapi-armhf.so"
                    YAPI._yApiCLibFileFallback = libpath + "/cdll/libyapi-armel.so"
                elif machine.find("mips") >= 0:
                    byteorder_str = sys.byteorder
                    if byteorder_str.lower() == 'little':
                        YAPI._yApiCLibFile = libpath + "/cdll/libyapi-mipsel.so"
                    else:
                        YAPI._yApiCLibFile = libpath + "/cdll/libyapi-mips.so"
                    YAPI._yApiCLibFileFallback = ""
                elif machine == 'x86_32' or (machine[0] == 'i' and machine[-2:] == '86'):
                    YAPI._yApiCLibFile = libpath + "/cdll/libyapi-i386.so"
                    YAPI._yApiCLibFileFallback = libpath + "/cdll/libyapi-amd64.so"  # just in case
                elif machine == 'x86_64':
                    YAPI._yApiCLibFile = libpath + "/cdll/libyapi-amd64.so"
                    YAPI._yApiCLibFileFallback = libpath + "/cdll/libyapi-i386.so"  # just in case
                else:
                    raise NotImplementedError(
                        "unsupported linux machine (" + machine + "), contact support@yoctopuce.com.")
            #
            #  Mac OS X
            #
            elif platform.system() == 'Darwin':
                if sys.maxsize > 2 ** 32:
                    YAPI._yApiCLibFile = libpath + "/cdll/libyapi.dylib"
                else:
                    raise NotImplementedError("Only Intel 64 bits installation are supported for Mac OS X.")
            #
            #  UNKNOWN, contact Yoctopuce support :-)
            #
            else:
                raise NotImplementedError("unsupported platform " + system +
                                          ", contact support@yoctopuce.com.")

        if not os.path.exists(YAPI._yApiCLibFile):
            raise ImportError(
                "YAPI shared library is missing (" + YAPI._yApiCLibFile +
                "), make sure it is available and accessible.")

        # try to load main librray
        libloaded = False
        # noinspection PyBroadException
        try:
            YAPI._yApiCLib = ctypes.CDLL(YAPI._yApiCLibFile)
            libloaded = True
        except Exception as ex:
            raise ImportError(
                "Unable to import YAPI shared library (" + YAPI._yApiCLibFile +
                "): " + str(ex))

        # try to load fallback library
        if not libloaded and YAPI._yApiCLibFileFallback != '':
            # noinspection PyBroadException
            try:
                YAPI._yApiCLib = ctypes.CDLL(YAPI._yApiCLibFileFallback)
                libloaded = True
            except Exception as ex:
                raise ImportError(
                    "Cannot load " + YAPI._yApiCLibFileFallback + " nor " + YAPI._yApiCLibFile + " : " + str(ex))

        if not libloaded:
            raise ImportError(
                "Unable to import YAPI shared library (" + YAPI._yApiCLibFile +
                "), make sure it is available and accessible.")


        ##--- (generated code: YFunction dlldef)
        YAPI._yapiInitAPI = YAPI._yApiCLib.yapiInitAPI
        YAPI._yapiInitAPI.restypes = ctypes.c_int
        YAPI._yapiInitAPI.argtypes = [ctypes.c_int, ctypes.c_char_p]
        YAPI._yapiFreeAPI = YAPI._yApiCLib.yapiFreeAPI
        YAPI._yapiFreeAPI.restypes = None
        YAPI._yapiFreeAPI.argtypes = []
        YAPI._yapiSetTraceFile = YAPI._yApiCLib.yapiSetTraceFile
        YAPI._yapiSetTraceFile.restypes = None
        YAPI._yapiSetTraceFile.argtypes = [ctypes.c_char_p]
        YAPI._yapiRegisterLogFunction = YAPI._yApiCLib.yapiRegisterLogFunction
        YAPI._yapiRegisterLogFunction.restypes = None
        YAPI._yapiRegisterLogFunction.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterDeviceArrivalCallback = YAPI._yApiCLib.yapiRegisterDeviceArrivalCallback
        YAPI._yapiRegisterDeviceArrivalCallback.restypes = None
        YAPI._yapiRegisterDeviceArrivalCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterDeviceRemovalCallback = YAPI._yApiCLib.yapiRegisterDeviceRemovalCallback
        YAPI._yapiRegisterDeviceRemovalCallback.restypes = None
        YAPI._yapiRegisterDeviceRemovalCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterDeviceChangeCallback = YAPI._yApiCLib.yapiRegisterDeviceChangeCallback
        YAPI._yapiRegisterDeviceChangeCallback.restypes = None
        YAPI._yapiRegisterDeviceChangeCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterDeviceConfigChangeCallback = YAPI._yApiCLib.yapiRegisterDeviceConfigChangeCallback
        YAPI._yapiRegisterDeviceConfigChangeCallback.restypes = None
        YAPI._yapiRegisterDeviceConfigChangeCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterFunctionUpdateCallback = YAPI._yApiCLib.yapiRegisterFunctionUpdateCallback
        YAPI._yapiRegisterFunctionUpdateCallback.restypes = None
        YAPI._yapiRegisterFunctionUpdateCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiRegisterTimedReportCallback = YAPI._yApiCLib.yapiRegisterTimedReportCallback
        YAPI._yapiRegisterTimedReportCallback.restypes = None
        YAPI._yapiRegisterTimedReportCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiLockDeviceCallBack = YAPI._yApiCLib.yapiLockDeviceCallBack
        YAPI._yapiLockDeviceCallBack.restypes = ctypes.c_int
        YAPI._yapiLockDeviceCallBack.argtypes = [ctypes.c_char_p]
        YAPI._yapiUnlockDeviceCallBack = YAPI._yApiCLib.yapiUnlockDeviceCallBack
        YAPI._yapiUnlockDeviceCallBack.restypes = ctypes.c_int
        YAPI._yapiUnlockDeviceCallBack.argtypes = [ctypes.c_char_p]
        YAPI._yapiLockFunctionCallBack = YAPI._yApiCLib.yapiLockFunctionCallBack
        YAPI._yapiLockFunctionCallBack.restypes = ctypes.c_int
        YAPI._yapiLockFunctionCallBack.argtypes = [ctypes.c_char_p]
        YAPI._yapiUnlockFunctionCallBack = YAPI._yApiCLib.yapiUnlockFunctionCallBack
        YAPI._yapiUnlockFunctionCallBack.restypes = ctypes.c_int
        YAPI._yapiUnlockFunctionCallBack.argtypes = [ctypes.c_char_p]
        YAPI._yapiRegisterHub = YAPI._yApiCLib.yapiRegisterHub
        YAPI._yapiRegisterHub.restypes = ctypes.c_int
        YAPI._yapiRegisterHub.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiPreregisterHub = YAPI._yApiCLib.yapiPreregisterHub
        YAPI._yapiPreregisterHub.restypes = ctypes.c_int
        YAPI._yapiPreregisterHub.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiUnregisterHub = YAPI._yApiCLib.yapiUnregisterHub
        YAPI._yapiUnregisterHub.restypes = None
        YAPI._yapiUnregisterHub.argtypes = [ctypes.c_char_p]
        YAPI._yapiUpdateDeviceList = YAPI._yApiCLib.yapiUpdateDeviceList
        YAPI._yapiUpdateDeviceList.restypes = ctypes.c_int
        YAPI._yapiUpdateDeviceList.argtypes = [ctypes.c_uint, ctypes.c_char_p]
        YAPI._yapiHandleEvents = YAPI._yApiCLib.yapiHandleEvents
        YAPI._yapiHandleEvents.restypes = ctypes.c_int
        YAPI._yapiHandleEvents.argtypes = [ctypes.c_char_p]
        YAPI._yapiGetTickCount = YAPI._yApiCLib.yapiGetTickCount
        YAPI._yapiGetTickCount.restypes = ctypes.c_ulonglong
        YAPI._yapiGetTickCount.argtypes = []
        YAPI._yapiCheckLogicalName = YAPI._yApiCLib.yapiCheckLogicalName
        YAPI._yapiCheckLogicalName.restypes = ctypes.c_int
        YAPI._yapiCheckLogicalName.argtypes = [ctypes.c_char_p]
        YAPI._yapiGetAPIVersion = YAPI._yApiCLib.yapiGetAPIVersion
        YAPI._yapiGetAPIVersion.restypes = ctypes.c_ushort
        YAPI._yapiGetAPIVersion.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        YAPI._yapiGetDevice = YAPI._yApiCLib.yapiGetDevice
        YAPI._yapiGetDevice.restypes = ctypes.c_int
        YAPI._yapiGetDevice.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiGetDeviceInfo = YAPI._yApiCLib.yapiGetDeviceInfo
        YAPI._yapiGetDeviceInfo.restypes = ctypes.c_int
        YAPI._yapiGetDeviceInfo.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiGetFunction = YAPI._yApiCLib.yapiGetFunction
        YAPI._yapiGetFunction.restypes = ctypes.c_int
        YAPI._yapiGetFunction.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiGetFunctionsByClass = YAPI._yApiCLib.yapiGetFunctionsByClass
        YAPI._yapiGetFunctionsByClass.restypes = ctypes.c_int
        YAPI._yapiGetFunctionsByClass.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiGetFunctionsByDevice = YAPI._yApiCLib.yapiGetFunctionsByDevice
        YAPI._yapiGetFunctionsByDevice.restypes = ctypes.c_int
        YAPI._yapiGetFunctionsByDevice.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiGetFunctionInfoEx = YAPI._yApiCLib.yapiGetFunctionInfoEx
        YAPI._yapiGetFunctionInfoEx.restypes = ctypes.c_int
        YAPI._yapiGetFunctionInfoEx.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestSyncStart = YAPI._yApiCLib.yapiHTTPRequestSyncStart
        YAPI._yapiHTTPRequestSyncStart.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestSyncStart.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, POINTER(POINTER(ctypes.c_ubyte)), ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestSyncStartEx = YAPI._yApiCLib.yapiHTTPRequestSyncStartEx
        YAPI._yapiHTTPRequestSyncStartEx.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestSyncStartEx.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, POINTER(POINTER(ctypes.c_ubyte)), ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestSyncDone = YAPI._yApiCLib.yapiHTTPRequestSyncDone
        YAPI._yapiHTTPRequestSyncDone.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestSyncDone.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestAsync = YAPI._yApiCLib.yapiHTTPRequestAsync
        YAPI._yapiHTTPRequestAsync.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestAsync.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestAsyncEx = YAPI._yApiCLib.yapiHTTPRequestAsyncEx
        YAPI._yapiHTTPRequestAsyncEx.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestAsyncEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequest = YAPI._yApiCLib.yapiHTTPRequest
        YAPI._yapiHTTPRequest.restypes = ctypes.c_int
        YAPI._yapiHTTPRequest.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiGetDevicePath = YAPI._yApiCLib.yapiGetDevicePath
        YAPI._yapiGetDevicePath.restypes = ctypes.c_int
        YAPI._yapiGetDevicePath.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiSleep = YAPI._yApiCLib.yapiSleep
        YAPI._yapiSleep.restypes = ctypes.c_int
        YAPI._yapiSleep.argtypes = [ctypes.c_int, ctypes.c_char_p]
        YAPI._yapiRegisterHubDiscoveryCallback = YAPI._yApiCLib.yapiRegisterHubDiscoveryCallback
        YAPI._yapiRegisterHubDiscoveryCallback.restypes = None
        YAPI._yapiRegisterHubDiscoveryCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiTriggerHubDiscovery = YAPI._yApiCLib.yapiTriggerHubDiscovery
        YAPI._yapiTriggerHubDiscovery.restypes = ctypes.c_int
        YAPI._yapiTriggerHubDiscovery.argtypes = [ctypes.c_char_p]
        YAPI._yapiRegisterDeviceLogCallback = YAPI._yApiCLib.yapiRegisterDeviceLogCallback
        YAPI._yapiRegisterDeviceLogCallback.restypes = None
        YAPI._yapiRegisterDeviceLogCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiGetAllJsonKeys = YAPI._yApiCLib.yapiGetAllJsonKeys
        YAPI._yapiGetAllJsonKeys.restypes = ctypes.c_int
        YAPI._yapiGetAllJsonKeys.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiCheckFirmware = YAPI._yApiCLib.yapiCheckFirmware
        YAPI._yapiCheckFirmware.restypes = ctypes.c_int
        YAPI._yapiCheckFirmware.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiGetBootloaders = YAPI._yApiCLib.yapiGetBootloaders
        YAPI._yapiGetBootloaders.restypes = ctypes.c_int
        YAPI._yapiGetBootloaders.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiUpdateFirmwareEx = YAPI._yApiCLib.yapiUpdateFirmwareEx
        YAPI._yapiUpdateFirmwareEx.restypes = ctypes.c_int
        YAPI._yapiUpdateFirmwareEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
        YAPI._yapiHTTPRequestSyncStartOutOfBand = YAPI._yApiCLib.yapiHTTPRequestSyncStartOutOfBand
        YAPI._yapiHTTPRequestSyncStartOutOfBand.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestSyncStartOutOfBand.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiHTTPRequestAsyncOutOfBand = YAPI._yApiCLib.yapiHTTPRequestAsyncOutOfBand
        YAPI._yapiHTTPRequestAsyncOutOfBand.restypes = ctypes.c_int
        YAPI._yapiHTTPRequestAsyncOutOfBand.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiTestHub = YAPI._yApiCLib.yapiTestHub
        YAPI._yapiTestHub.restypes = ctypes.c_int
        YAPI._yapiTestHub.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        YAPI._yapiJsonGetPath = YAPI._yApiCLib.yapiJsonGetPath
        YAPI._yapiJsonGetPath.restypes = ctypes.c_int
        YAPI._yapiJsonGetPath.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiJsonDecodeString = YAPI._yApiCLib.yapiJsonDecodeString
        YAPI._yapiJsonDecodeString.restypes = ctypes.c_int
        YAPI._yapiJsonDecodeString.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiGetSubdevices = YAPI._yApiCLib.yapiGetSubdevices
        YAPI._yapiGetSubdevices.restypes = ctypes.c_int
        YAPI._yapiGetSubdevices.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiFreeMem = YAPI._yApiCLib.yapiFreeMem
        YAPI._yapiFreeMem.restypes = None
        YAPI._yapiFreeMem.argtypes = [ctypes.c_void_p]
        YAPI._yapiGetDevicePathEx = YAPI._yApiCLib.yapiGetDevicePathEx
        YAPI._yapiGetDevicePathEx.restypes = ctypes.c_int
        YAPI._yapiGetDevicePathEx.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p]
        YAPI._yapiSetNetDevListValidity = YAPI._yApiCLib.yapiSetNetDevListValidity
        YAPI._yapiSetNetDevListValidity.restypes = None
        YAPI._yapiSetNetDevListValidity.argtypes = [ctypes.c_int]
        YAPI._yapiGetNetDevListValidity = YAPI._yApiCLib.yapiGetNetDevListValidity
        YAPI._yapiGetNetDevListValidity.restypes = ctypes.c_int
        YAPI._yapiGetNetDevListValidity.argtypes = []
        YAPI._yapiRegisterBeaconCallback = YAPI._yApiCLib.yapiRegisterBeaconCallback
        YAPI._yapiRegisterBeaconCallback.restypes = None
        YAPI._yapiRegisterBeaconCallback.argtypes = [ctypes.c_void_p]
        YAPI._yapiStartStopDeviceLogCallback = YAPI._yApiCLib.yapiStartStopDeviceLogCallback
        YAPI._yapiStartStopDeviceLogCallback.restypes = None
        YAPI._yapiStartStopDeviceLogCallback.argtypes = [ctypes.c_char_p, ctypes.c_int]
        YAPI._yapiIsModuleWritable = YAPI._yApiCLib.yapiIsModuleWritable
        YAPI._yapiIsModuleWritable.restypes = ctypes.c_int
        YAPI._yapiIsModuleWritable.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        YAPI._yapiGetDLLPath = YAPI._yApiCLib.yapiGetDLLPath
        YAPI._yapiGetDLLPath.restypes = ctypes.c_int
        YAPI._yapiGetDLLPath.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        YAPI._yapiSetNetworkTimeout = YAPI._yApiCLib.yapiSetNetworkTimeout
        YAPI._yapiSetNetworkTimeout.restypes = None
        YAPI._yapiSetNetworkTimeout.argtypes = [ctypes.c_int]
        YAPI._yapiGetNetworkTimeout = YAPI._yApiCLib.yapiGetNetworkTimeout
        YAPI._yapiGetNetworkTimeout.restypes = ctypes.c_int
        YAPI._yapiGetNetworkTimeout.argtypes = []
    #--- (end of generated code: YFunction dlldef)

        YAPI._ydllLoaded = True

    # noinspection PyUnresolvedReferences,PyTypeChecker
    class yDeviceSt(ctypes.Structure):
        _pack_ = 1
        # noinspection PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,
        # PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker,PyTypeChecker
        _fields_ = [("vendorid", ctypes.c_uint16),
                    ("deviceid", ctypes.c_uint16),
                    ("devrelease", ctypes.c_uint16),
                    ("nbinbterfaces", ctypes.c_uint16),
                    ("manufacturer", ctypes.c_char * 20),  # YAPI.YOCTO_MANUFACTURER_LEN),
                    ("productname", ctypes.c_char * 28),  # YAPI.YOCTO_PRODUCTNAME_LEN),
                    ("serial", ctypes.c_char * 20),  # YAPI.YAPI.YOCTO_SERIAL_LEN),
                    ("logicalname", ctypes.c_char * 20),  # YAPI.YOCTO_LOGICAL_LEN),
                    ("firmware", ctypes.c_char * 22),  # YAPI.YOCTO_FIRMWARE_LEN),
                    ("beacon", ctypes.c_int8),
                    ("pad", ctypes.c_int8)]

    # noinspection PyUnresolvedReferences
    class YIOHDL(ctypes.Structure):
        _pack_ = 1
        _fields_ = [("raw", ctypes.c_byte)]

    # noinspection PyClassHasNoInit
    class yDEVICE_PROP:
        PROP_VENDORID, PROP_DEVICEID, PROP_DEVRELEASE, PROP_FIRMWARELEVEL, PROP_MANUFACTURER, PROP_PRODUCTNAME, \
            PROP_SERIAL, PROP_LOGICALNAME, PROP_URL = range(9)

    # noinspection PyClassHasNoInit
    class yFACE_STATUS:
        YFACE_EMPTY, YFACE_RUNNING, YFACE_ERROR = range(3)

    class _Event:
        ARRIVAL, REMOVAL, CHANGE, FUN_VALUE, FUN_TIMEDREPORT, \
            HUB_DISCOVERY, CONFCHANGE, BEACON_CHANGE, YAPI_NOP = range(9)

        def __init__(self):
            self.ev = self.YAPI_NOP
            self.module = None
            self.func = None
            self.value = ""
            self.timestamp = 0.0
            self.duration = 0.0
            self.report = None
            self.serial = None
            self.url = None
            self.beacon = -1

        def setArrival(self, module):
            self.ev = self.ARRIVAL
            self.module = module

        def setRemoval(self, module):
            self.ev = self.REMOVAL
            self.module = module

        def setChange(self, module):
            self.ev = self.CHANGE
            self.module = module

        def setConfigChange(self, module):
            self.ev = self.CONFCHANGE
            self.module = module

        def setBeaconChange(self, module, beacon):
            self.ev = self.BEACON_CHANGE
            self.module = module
            self.beacon = beacon

        def setFunVal(self, func, value):
            self.ev = self.FUN_VALUE
            self.func = func
            self.value = value

        def setTimedReport(self, func, timestamp, duration, report):
            self.ev = self.FUN_TIMEDREPORT
            self.func = func
            self.timestamp = timestamp
            self.duration = duration
            self.report = report

        def setHubDiscovery(self, serial, url):
            self.ev = self.HUB_DISCOVERY
            self.serial = serial
            self.url = url

        def invokePlug(self):
            global yArrivalFct
            global yRemovalFct
            global yChangeFct
            global yHubDiscoveryCallback
            if self.ev == self.ARRIVAL:
                if yArrivalFct is not None:
                    # noinspection PyCallingNonCallable
                    yArrivalFct(self.module)
            elif self.ev == self.REMOVAL:
                if yRemovalFct is not None:
                    # noinspection PyCallingNonCallable
                    yRemovalFct(self.module)
            elif self.ev == self.CHANGE:
                if yChangeFct is not None:
                    # noinspection PyCallingNonCallable
                    yChangeFct(self.module)
            elif self.ev == self.HUB_DISCOVERY:
                if yHubDiscoveryCallback is not None:
                    yHubDiscoveryCallback(self.serial, self.url)

        # noinspection PyProtectedMember
        def invokeData(self):
            if self.ev == self.FUN_VALUE:
                func = self.func
                func._invokeValueCallback(self.value)
            elif self.ev == self.FUN_TIMEDREPORT:
                if self.report[0] <= 2:
                    sensor = self.func
                    sensor._invokeTimedReportCallback(sensor._decodeTimedReport(self.timestamp, self.duration, self.report))
            elif self.ev == self.CONFCHANGE:
                self.module._invokeConfigChangeCallback()
            elif self.ev == self.BEACON_CHANGE:
                self.module._invokeBeaconCallback(self.beacon)

    ##--- (generated code: YFunction return codes)
    # Yoctopuce error codes, used by default as function return value
    SUCCESS = 0                    # everything worked all right
    NOT_INITIALIZED = -1           # call yInitAPI() first !
    INVALID_ARGUMENT = -2          # one of the arguments passed to the function is invalid
    NOT_SUPPORTED = -3             # the operation attempted is (currently) not supported
    DEVICE_NOT_FOUND = -4          # the requested device is not reachable
    VERSION_MISMATCH = -5          # the device firmware is incompatible with this API version
    DEVICE_BUSY = -6               # the device is busy with another task and cannot answer
    TIMEOUT = -7                   # the device took too long to provide an answer
    IO_ERROR = -8                  # there was an I/O problem while talking to the device
    NO_MORE_DATA = -9              # there is no more data to read from
    EXHAUSTED = -10                # you have run out of a limited resource, check the documentation
    DOUBLE_ACCES = -11             # you have two process that try to access to the same device
    UNAUTHORIZED = -12             # unauthorized access to password-protected device
    RTC_NOT_READY = -13            # real-time clock has not been initialized (or time was lost)
    FILE_NOT_FOUND = -14           # the file is not found

    #--- (end of generated code: YFunction return codes)

    class YAPI_Exception(YAPI_Exception):
        pass

    YDevice_devCache = []

    # - Types used for internal yapi callbacks
    _yapiLogFunc = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int)

    _yapiDeviceUpdateFunc = ctypes.CFUNCTYPE(None, ctypes.c_int)

    _yapiBeaconUpdateFunc = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)

    _yapiFunctionUpdateFunc = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)

    _yapiTimedReportFunc = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_double, POINTER(c_ubyte), ctypes.c_int, ctypes.c_double)

    _yapiHubDiscoveryCallback = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p)

    _yapiDeviceLogCallback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)

    @staticmethod
    def YISERR(retcode):
        if retcode < 0:
            return True
        return False

    # noinspection PyClassHasNoInit
    class blockingCallbackCtx:
        res = 0
        response = ""
        errmsgRef = ""

    # noinspection PyUnusedLocal
    @staticmethod
    def YblockingCallback(device, context, returnval, result, errmsgRef):
        context.res = returnval
        context.response = result
        context.errmsgRef = errmsgRef

    #--- (generated code: YAPIContext yapiwrapper)
    @staticmethod
    def SetDeviceListValidity(deviceListValidity):
        """
        Modifies the delay between each forced enumeration of the used YoctoHubs.
        By default, the library performs a full enumeration every 10 seconds.
        To reduce network traffic, you can increase this delay.
        It's particularly useful when a YoctoHub is connected to the GSM network
        where traffic is billed. This parameter doesn't impact modules connected by USB,
        nor the working of module arrival/removal callbacks.
        Note: you must call this function after yInitAPI.

        @param deviceListValidity : nubmer of seconds between each enumeration.
        @noreturn
        """
        YAPI._yapiContext.SetDeviceListValidity(deviceListValidity)

    @staticmethod
    def GetDeviceListValidity():
        """
        Returns the delay between each forced enumeration of the used YoctoHubs.
        Note: you must call this function after yInitAPI.

        @return the number of seconds between each enumeration.
        """
        return YAPI._yapiContext.GetDeviceListValidity()

    @staticmethod
    def SetNetworkTimeout(networkMsTimeout):
        """
        Modifies the network connection delay for yRegisterHub() and yUpdateDeviceList().
        This delay impacts only the YoctoHubs and VirtualHub
        which are accessible through the network. By default, this delay is of 20000 milliseconds,
        but depending or you network you may want to change this delay,
        gor example if your network infrastructure is based on a GSM connection.

        @param networkMsTimeout : the network connection delay in milliseconds.
        @noreturn
        """
        YAPI._yapiContext.SetNetworkTimeout(networkMsTimeout)

    @staticmethod
    def GetNetworkTimeout():
        """
        Returns the network connection delay for yRegisterHub() and yUpdateDeviceList().
        This delay impacts only the YoctoHubs and VirtualHub
        which are accessible through the network. By default, this delay is of 20000 milliseconds,
        but depending or you network you may want to change this delay,
        for example if your network infrastructure is based on a GSM connection.

        @return the network connection delay in milliseconds.
        """
        return YAPI._yapiContext.GetNetworkTimeout()

    @staticmethod
    def SetCacheValidity(cacheValidityMs):
        """
        Change the validity period of the data loaded by the library.
        By default, when accessing a module, all the attributes of the
        module functions are automatically kept in cache for the standard
        duration (5 ms). This method can be used to change this standard duration,
        for example in order to reduce network or USB traffic. This parameter
        does not affect value change callbacks
        Note: This function must be called after yInitAPI.

        @param cacheValidityMs : an integer corresponding to the validity attributed to the
                loaded function parameters, in milliseconds.
        @noreturn
        """
        YAPI._yapiContext.SetCacheValidity(cacheValidityMs)

    @staticmethod
    def GetCacheValidity():
        """
        Returns the validity period of the data loaded by the library.
        This method returns the cache validity of all attributes
        module functions.
        Note: This function must be called after yInitAPI .

        @return an integer corresponding to the validity attributed to the
                loaded function parameters, in milliseconds
        """
        return YAPI._yapiContext.GetCacheValidity()

    #--- (end of generated code: YAPIContext yapiwrapper)

    @staticmethod
    def GetTickCount():
        """
        Returns the current value of a monotone millisecond-based time counter.
        This counter can be used to compute delays in relation with
        Yoctopuce devices, which also uses the millisecond as timebase.

        @return a long integer corresponding to the millisecond counter.
        """
        # for python, since some implementations don't support 64bits integers
        # GetTickCount returns a datetime object instead of a u64
        # noinspection PyUnresolvedReferences
        return datetime.datetime.today()

    @staticmethod
    def SetTraceFile(filename):
        fname = ctypes.create_string_buffer(filename.encode("ASCII"))
        # noinspection PyUnresolvedReferences
        YAPI._yapiSetTraceFile(fname)

    # noinspection PyUnresolvedReferences
    @staticmethod
    def Sleep(ms_duration, errmsg=None):
        """
        Pauses the execution flow for a specified duration.
        This function implements a passive waiting loop, meaning that it does not
        consume CPU cycles significantly. The processor is left available for
        other threads and processes. During the pause, the library nevertheless
        reads from time to time information from the Yoctopuce modules by
        calling yHandleEvents(), in order to stay up-to-date.

        This function may signal an error in case there is a communication problem
        while contacting a module.

        @param ms_duration : an integer corresponding to the duration of the pause,
                in milliseconds.
        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        if type(ms_duration) == type(int()):
            ms_duration = datetime.timedelta(milliseconds=ms_duration)
        timeout = YAPI.GetTickCount() + ms_duration
        res = YAPI.SUCCESS

        ok = True
        while ok:
            res = YAPI.HandleEvents(errmsg)
            if YAPI.YISERR(res):
                return res

            if YAPI.GetTickCount() < timeout:
                # noinspection PyUnresolvedReferences
                res = YAPI._yapiSleep(2, errBuffer)
                if YAPI.YISERR(res):
                    if errmsg is not None:
                        errmsg.value = YByte2String(errBuffer.value)
                    return res
            ok = YAPI.GetTickCount() < timeout
        if errmsg is not None:
            errmsg.value = YByte2String(errBuffer.value)
        return res

    @staticmethod
    def CheckLogicalName(name):
        """
        Checks if a given string is valid as logical name for a module or a function.
        A valid logical name has a maximum of 19 characters, all among
        A..Z, a..z, 0..9, _, and -.
        If you try to configure a logical name with an incorrect string,
        the invalid characters are ignored.

        @param name : a string containing the name to check.

        @return true if the name is valid, false otherwise.
        """
        # noinspection PyUnresolvedReferences
        if not YAPI._yapiCheckLogicalName(name.encode("ASCII")):
            return False
        return True

    @staticmethod
    def yapiLockFunctionCallBack(errmsgRef=None):
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiLockFunctionCallBack(errBuffer)
        if errmsgRef is not None:
            # noinspection PyAttributeOutsideInit
            errmsgRef.value = YByte2String(errBuffer.value)
        return res

    @staticmethod
    def yapiUnlockFunctionCallBack(errmsgRef=None):
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiUnlockFunctionCallBack(errBuffer)
        if errmsgRef is not None:
            # noinspection PyAttributeOutsideInit
            errmsgRef.value = YByte2String(errBuffer.value)
        return res

    @staticmethod
    def _getCalibrationHandler(calType):
        key = str(calType)
        if key in YAPI._CalibHandlers:
            return YAPI._CalibHandlers[key]
        return None

    @staticmethod
    def _setArrayLength(a, length):
        if len(a) > length:
            del a[length:]
        while len(a) < length:
            a.append(0)

    decExp = [1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0e-1, 1.0, 1.0e1, 1.0e2, 1.0e3, 1.0e4, 1.0e5, 1.0e6, 1.0e7,
              1.0e8, 1.0e9]

    # Convert Yoctopuce 16-bit decimal floats to standard double-precision floats

    @staticmethod
    def _decimalToDouble(val):
        negate = False
        mantis = val & 2047
        if mantis == 0:
            return 0.0
        if val > 32767:
            negate = True
            val = 65536 - val
        if val < 0:
            negate = True
            val = -val
        exp = val >> 11
        res = (mantis) * YAPI.decExp[exp]
        if negate:
            return -res
        else:
            return res

    # Convert standard double-precision floats to Yoctopuce 16-bit decimal floats
    @staticmethod
    def _doubleToDecimal(val):
        negate = False

        if val == 0.0:
            return 0
        if val < 0:
            negate = True
            val = -val
        comp = val / 1999.0
        decpow = 0
        while comp > YAPI.decExp[decpow] and decpow < 15:
            decpow += 1
        mant = val / YAPI.decExp[decpow]
        if decpow == 15 and mant > 2047.0:
            res = (15 << 11) + 2047  # overflow
        else:
            res = (decpow << 11) + round(mant)
        if negate:
            return -res
        else:
            return res

    @staticmethod
    def _decodeWords(sdat):
        p = 0
        udat = []
        while p < len(sdat):
            c = sdat[p]
            p += 1
            if c == '*':
                val = 0
            elif c == 'X':
                val = 0xffff
            elif c == 'Y':
                val = 0x7fff
            elif c >= 'a':
                srcpos = int(len(udat) - 1 - (ord(c) - ord('a')))
                if srcpos < 0:
                    val = 0
                else:
                    val = udat[srcpos]
            else:
                if p + 2 > len(sdat):
                    return udat
                val = (ord(c) - ord('0'))
                c = sdat[p]
                p += 1
                val += (ord(c) - ord('0')) << 5
                c = sdat[p]
                p += 1
                if c == 'z':
                    c = "\\"
                val += (ord(c) - ord('0')) << 10
            udat.append(val)
        return udat

    @staticmethod
    def _decodeFloats(sdat):
        p = 0
        idat = []
        while p < len(sdat):
            val = 0
            sign = 1
            dec = 0
            decInc = 0
            c = sdat[p]
            p += 1
            while c != '-' and (c < '0' or c > '9'):
                if p >= len(sdat):
                    return idat
                c = sdat[p]
                p += 1
            if c == '-':
                if p >= len(sdat):
                    return idat
                sign = -sign
                c = sdat[p]
                p += 1
            while ('0' <= c <= '9') or c == '.':
                if c == '.':
                    decInc = 1
                elif dec < 3:
                    val = val * 10 + ord(c) - ord('0')
                    dec += decInc
                if p < len(sdat):
                    c = sdat[p]
                    p += 1
                else:
                    c = 0
            if dec < 3:
                if dec == 0:
                    val *= 1000
                elif dec == 1:
                    val *= 100
                elif dec == 2:
                    val *= 10
            idat.append(sign * val)
        return idat

    @staticmethod
    def _atoi(val):
        val = val.strip()
        p = 0
        if p < len(val) and (val[p] == '-' or val[p] == '+'):
            p += 1
        while p < len(val) and val[p].isdigit():
            p += 1
        if p == 0:
            return 0
        return int(val[: p])

    @staticmethod
    def _bytesToHexStr(bindata):
        return YByte2String(binascii.hexlify(bindata)).upper()

    @staticmethod
    def _hexStrToBin(hex_str):
        return binascii.unhexlify(YString2Byte(hex_str))

    # noinspection PyUnresolvedReferences
    @staticmethod
    def HandleEvents(errmsg=None):
        """
        Maintains the device-to-library communication channel.
        If your program includes significant loops, you may want to include
        a call to this function to make sure that the library takes care of
        the information pushed by the modules on the communication channels.
        This is not strictly necessary, but it may improve the reactivity
        of the library for the following commands.

        This function may signal an error in case there is a communication problem
        while contacting a module.

        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)

        if not YAPI._apiInitialized:
            if errmsg is not None:
                errmsg.value = "API not initialized"
            return YAPI.NOT_INITIALIZED

        # noinspection PyUnresolvedReferences
        res = YAPI._yapiHandleEvents(errBuffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                # noinspection PyAttributeOutsideInit
                errmsg.value = YByte2String(errBuffer.value)
            return res

        while len(YAPI._DataEvents) > 0:
            YAPI.yapiLockFunctionCallBack(errmsg)
            if not (len(YAPI._DataEvents)):
                YAPI.yapiUnlockFunctionCallBack(errmsg)
                break

            ev = YAPI._DataEvents.pop(0)
            YAPI.yapiUnlockFunctionCallBack(errmsg)
            ev.invokeData()
        return YAPI.SUCCESS

    @staticmethod
    def DisableExceptions():
        """
        Disables the use of exceptions to report runtime errors.
        When exceptions are disabled, every function returns a specific
        error value which depends on its type and which is documented in
        this reference manual.
        """
        YAPI.ExceptionsDisabled = True

    @staticmethod
    def EnableExceptions():
        """
        Re-enables the use of exceptions for runtime error handling.
        Be aware than when exceptions are enabled, every function that fails
        triggers an exception. If the exception is not caught by the user code,
        it  either fires the debugger or aborts (i.e. crash) the program.
        On failure, throws an exception or returns a negative error code.
        """
        YAPI.ExceptionsDisabled = False

    # - Internal callback registered into YAPI
    # noinspection PyUnusedLocal
    @staticmethod
    def native_yLogFunction(log, loglen):

        global yLogFct
        if yLogFct is not None:
            # noinspection PyCallingNonCallable
            yLogFct(YByte2String(log))
        return 0

    @staticmethod
    def RegisterLogFunction(logfun):
        """
        Registers a log callback function. This callback will be called each time
        the API have something to say. Quite useful to debug the API.

        @param logfun : a procedure taking a string parameter, or None
                to unregister a previously registered  callback.
        """
        global yLogFct
        yLogFct = logfun

    @staticmethod
    def emptyDeviceSt():
        infos = YAPI.yDeviceSt()
        infos.vendorid = 0
        infos.deviceid = 0
        infos.devrelease = 0
        infos.nbinbterfaces = 0
        infos.manufacturer = "".encode("ASCII")
        infos.productname = "".encode("ASCII")
        infos.serial = "".encode("ASCII")
        infos.logicalname = "".encode("ASCII")
        infos.firmware = "".encode("ASCII")
        infos.beacon = 0
        return infos

    @staticmethod
    def yapiGetDeviceInfo(d, infos, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetDeviceInfo(d, ctypes.byref(infos), errmsg_buffer)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def native_yDeviceArrivalCallback(d):
        YDevice.PlugDevice(d)
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        # noinspection PyTypeChecker
        modul.setImmutableAttributes(infos)
        if yArrivalFct is not None:
            ev = YAPI._Event()
            ev.setArrival(modul)
            YAPI._PlugEvents.append(ev)

    @staticmethod
    def native_HubDiscoveryCallback(serial_ptr, url_ptr):
        serial = YByte2String(serial_ptr)
        url = YByte2String(url_ptr)
        ev = YAPI._Event()
        ev.setHubDiscovery(serial, url)
        YAPI._PlugEvents.append(ev)

    @staticmethod
    def native_DeviceLogCallback(d, line):
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        callback = modul.get_logCallback()
        if callback is not None:
            callback(modul, YByte2String(line))
        return 0

    @staticmethod
    def yapiLockDeviceCallBack(errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiLockDeviceCallBack(errmsg_buffer)
        if errmsgRef is not None:
            # noinspection PyAttributeOutsideInit
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def yapiUnlockDeviceCallBack(errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiUnlockDeviceCallBack(errmsg_buffer)
        if errmsgRef is not None:
            # noinspection PyAttributeOutsideInit
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def RegisterDeviceArrivalCallback(arrivalCallback):
        """
        Register a callback function, to be called each time
        a device is plugged. This callback will be invoked while yUpdateDeviceList
        is running. You will have to call this function on a regular basis.

        @param arrivalCallback : a procedure taking a YModule parameter, or None
                to unregister a previously registered  callback.
        """
        global yArrivalFct
        yArrivalFct = arrivalCallback
        if arrivalCallback is not None:
            error = YRefParam()
            mod = YModule.FirstModule()
            while mod is not None:
                if mod.isOnline():
                    YAPI.yapiLockDeviceCallBack(error)
                    YAPI.native_yDeviceArrivalCallback(mod.functionDescriptor())
                    YAPI.yapiUnlockDeviceCallBack(error)
                mod = mod.nextModule()
        return 0

    @staticmethod
    def RegisterDeviceRemovalCallback(removalCallback):
        """
        Register a callback function, to be called each time
        a device is unplugged. This callback will be invoked while yUpdateDeviceList
        is running. You will have to call this function on a regular basis.

        @param removalCallback : a procedure taking a YModule parameter, or None
                to unregister a previously registered  callback.
        """
        global yRemovalFct
        yRemovalFct = removalCallback

    @staticmethod
    def RegisterHubDiscoveryCallback(hubDiscoveryCallback):
        """
        Register a callback function, to be called each time an Network Hub send
        an SSDP message. The callback has two string parameter, the first one
        contain the serial number of the hub and the second contain the URL of the
        network hub (this URL can be passed to RegisterHub). This callback will be invoked
        while yUpdateDeviceList is running. You will have to call this function on a regular basis.

        @param hubDiscoveryCallback : a procedure taking two string parameter, the serial
                number and the hub URL. Use None to unregister a previously registered  callback.
        """
        global yHubDiscoveryCallback
        yHubDiscoveryCallback = hubDiscoveryCallback
        errmsgRef = YRefParam()
        YAPI.TriggerHubDiscovery(errmsgRef)
        return 0

    # noinspection PyUnresolvedReferences
    @staticmethod
    def native_yDeviceChangeCallback(d):
        global yChangeFct
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if yChangeFct is None:
            return
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        ev = YAPI._Event()
        ev.setChange(modul)
        YAPI._PlugEvents.append(ev)
        return

    @staticmethod
    def RegisterDeviceChangeCallback(callback):
        global yChangeFct
        yChangeFct = callback

    # noinspection PyUnresolvedReferences
    @staticmethod
    def native_yDeviceConfigChangeCallback(d):
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        if modul in YModule._moduleCallbackList and YModule._moduleCallbackList[modul] > 0:
            ev = YAPI._Event()
            ev.setConfigChange(modul)
            YAPI._DataEvents.append(ev)
        return 0

    @staticmethod
    def native_yBeaconChangeCallback(d, beacon):
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        if modul in YModule._moduleCallbackList and YModule._moduleCallbackList[modul] > 0:
            ev = YAPI._Event()
            ev.setBeaconChange(modul, beacon)
            YAPI._DataEvents.append(ev)
        return 0

    @staticmethod
    def queuesCleanUp():
        del YAPI._PlugEvents[:]
        del YAPI._DataEvents[:]

    @staticmethod
    def native_yFunctionUpdateCallback(f, data):
        if data is None:
            return
        for i in range(len(YFunction._FunctionCallbacks)):
            if YFunction._FunctionCallbacks[i].get_functionDescriptor() == f:
                ev = YAPI._Event()
                ev.setFunVal(YFunction._FunctionCallbacks[i], YByte2String(data))
                YAPI._DataEvents.append(ev)
                return 0
        return 0

    @staticmethod
    def native_yTimedReportCallback(f, timestamp, data, dataLen, duration):
        for i in range(len(YFunction._TimedReportCallbackList)):
            if YFunction._TimedReportCallbackList[i].get_functionDescriptor() == f:
                report = []
                for d in range(dataLen):
                    report.append(int(data[d]))
                ev = YAPI._Event()
                ev.setTimedReport(YFunction._TimedReportCallbackList[i], timestamp, duration, report)
                YAPI._DataEvents.append(ev)
                return
        return 0

    @staticmethod
    def RegisterCalibrationHandler(calibType, callback):
        key = str(calibType)
        YAPI._CalibHandlers[key] = callback

    # noinspection PyUnusedLocal
    @staticmethod
    def LinearCalibrationHandler(rawValue, calibType, params, rawValues, refValues):
        x = rawValues[0]
        adj = refValues[0] - x
        i = 0

        if calibType < YAPI.YOCTO_CALIB_TYPE_OFS:
            npt = calibType % 10
            if npt > len(rawValues):
                npt = len(rawValues)
            if npt > len(refValues):
                npt = len(refValues)
        else:
            npt = len(refValues)
        while rawValue > rawValues[i] and i + 1 < npt:
            i += 1
            x2 = x
            adj2 = adj
            x = rawValues[i]
            adj = refValues[i] - x
            if rawValue < x and x > x2:
                adj = adj2 + (adj - adj2) * (rawValue - x2) / (x - x2)
        return rawValue + adj

    # noinspection PyUnresolvedReferences
    @staticmethod
    def native_yDeviceRemovalCallback(d):
        global yRemovalFct
        infos = YAPI.emptyDeviceSt()
        errmsgRef = YRefParam()
        if yRemovalFct is None:
            return
        infos.deviceid = 0
        if YAPI.yapiGetDeviceInfo(d, infos, errmsgRef) != YAPI.SUCCESS:
            return
        modul = YModule.FindModule(YByte2String(infos.serial) + ".module")
        ev = YAPI._Event()
        ev.setRemoval(modul)
        YAPI._PlugEvents.append(ev)
        return 0

    @staticmethod
    def apiGetAPIVersion(versionRef, dateRef):
        pversion = YAPI.YPCHAR()
        pdate = YAPI.YPCHAR()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetAPIVersion(ctypes.byref(pversion), ctypes.byref(pdate))
        # noinspection PyAttributeOutsideInit
        versionRef.value = YByte2String(pversion.buffer)
        dateRef.value = YByte2String(pdate.buffer)
        return res

    @staticmethod
    def parseHTTP(data, start, stop):
        httpheader = "HTTP/1.1 "
        okHeader = "OK\r\n"
        CR = "\r\n"
        if (stop - start) > len(okHeader) and data[start: start + len(okHeader)] == okHeader:
            httpcode = 200
            errmsg = ""
        else:
            if (stop - start) < len(httpheader) or data[start: start + len(httpheader)] != httpheader:
                errmsg = "data should start with " + httpheader
                headerlen = 0
                return -1, headerlen, errmsg
            p1 = data.find(" ", start + len(httpheader) - 1)
            p2 = data.find(" ", p1 + 1)
            if p1 < 0 or p2 < 0:
                errmsg = "Invalid HTTP header (invalid first line)"
                headerlen = 0
                return -1, headerlen, errmsg
            httpcode = YAPI._atoi(data[p1: p2])
            if httpcode != 200:
                errmsg = "Unexpected HTTP return code:%d" % httpcode
            else:
                errmsg = ""
        p1 = data.find(CR + CR, start)  # json data is a structure
        if p1 < 0:
            errmsg = "Invalid HTTP header (missing header end)"
            headerlen = 0
            return -1, headerlen, errmsg

        headerlen = p1 + 4
        return httpcode, headerlen, errmsg

    @staticmethod
    def GetAPIVersion():
        """
        Returns the version identifier for the Yoctopuce library in use.
        The version is a string in the form "Major.Minor.Build",
        for instance "1.01.5535". For languages using an external
        DLL (for instance C#, VisualBasic or Delphi), the character string
        includes as well the DLL version, for instance
        "1.01.5535 (1.01.5439)".

        If you want to verify in your code that the library version is
        compatible with the version that you have used during development,
        verify that the major number is strictly equal and that the minor
        number is greater or equal. The build number is not relevant
        with respect to the library compatibility.

        @return a character string describing the library version.
        """
        version = YRefParam()
        date = YRefParam()
        # load yapi functions form dynamic library
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        YAPI.apiGetAPIVersion(version, date)
        # noinspection PyTypeChecker
        return YAPI.YOCTO_API_VERSION_STR + "." + YAPI.YOCTO_API_BUILD_NO + " (" + version.value + ")"

    @staticmethod
    def InitAPI(mode, errmsg=None):
        """
        Initializes the Yoctopuce programming library explicitly.
        It is not strictly needed to call yInitAPI(), as the library is
        automatically  initialized when calling yRegisterHub() for the
        first time.

        When YAPI.DETECT_NONE is used as detection mode,
        you must explicitly use yRegisterHub() to point the API to the
        VirtualHub on which your devices are connected before trying to access them.

        @param mode : an integer corresponding to the type of automatic
                device detection to use. Possible values are
                YAPI.DETECT_NONE, YAPI.DETECT_USB, YAPI.DETECT_NET,
                and YAPI.DETECT_ALL.
        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        if YAPI._apiInitialized:
            return YAPI.SUCCESS
            # load yapi functions form dynamic library
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        version = YRefParam()
        date = YRefParam()
        if YAPI.apiGetAPIVersion(version, date) != YAPI.YOCTO_API_VERSION_BCD:
            if errmsg is not None:
                errmsg.value = YAPI._yApiCLibFile + " does does not match the version of the Libary (Libary=" + YAPI.YOCTO_API_VERSION_STR + "." + YAPI.YOCTO_API_BUILD_NO
                # noinspection PyTypeChecker
                errmsg.value += " yapi.dll=" + version.value + ")"
                return YAPI.VERSION_MISMATCH

        YAPI.pymodule_initialization()

        # noinspection PyUnresolvedReferences
        res = YAPI._yapiInitAPI(mode, errmsg_buffer)
        if errmsg is not None:
            errmsg.value = YByte2String(errmsg_buffer.value)
        if YAPI.YISERR(res):
            return res

        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterDeviceArrivalCallback(native_yDeviceArrivalAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterDeviceRemovalCallback(native_yDeviceRemovalAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterDeviceChangeCallback(native_yDeviceChangeAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterDeviceConfigChangeCallback(native_yDeviceConfigChangeAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterBeaconCallback(native_yBeaconChangeCallbackAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterFunctionUpdateCallback(native_yFunctionUpdateAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterTimedReportCallback(native_yTimedReportAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterLogFunction(native_yLogFunctionAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterHubDiscoveryCallback(native_yHubDiscoveryAnchor)
        # noinspection PyUnresolvedReferences
        YAPI._yapiRegisterDeviceLogCallback(native_yDeviceLogAnchor)

        for i in range(21):
            YAPI.RegisterCalibrationHandler(i, YAPI.LinearCalibrationHandler)
        YAPI.RegisterCalibrationHandler(YAPI.YOCTO_CALIB_TYPE_OFS, YAPI.LinearCalibrationHandler)
        YAPI._apiInitialized = True
        return res

    @staticmethod
    def FreeAPI():
        """
        Frees dynamically allocated memory blocks used by the Yoctopuce library.
        It is generally not required to call this function, unless you
        want to free all dynamically allocated memory blocks in order to
        track a memory leak for instance.
        You should not call any other library function after calling
        yFreeAPI(), or your program will crash.
        """
        if YAPI._apiInitialized:
            # noinspection PyUnresolvedReferences
            YAPI._yapiFreeAPI()
            YAPI.pymodule_cleanup()
            YFunction._ClearCache()
            YAPI._apiInitialized = False

    @staticmethod
    def RegisterHub(url, errmsg=None):
        """
        Setup the Yoctopuce library to use modules connected on a given machine. The
        parameter will determine how the API will work. Use the following values:

        <b>usb</b>: When the usb keyword is used, the API will work with
        devices connected directly to the USB bus. Some programming languages such a JavaScript,
        PHP, and Java don't provide direct access to USB hardware, so usb will
        not work with these. In this case, use a VirtualHub or a networked YoctoHub (see below).

        <b><i>x.x.x.x</i></b> or <b><i>hostname</i></b>: The API will use the devices connected to the
        host with the given IP address or hostname. That host can be a regular computer
        running a VirtualHub, or a networked YoctoHub such as YoctoHub-Ethernet or
        YoctoHub-Wireless. If you want to use the VirtualHub running on you local
        computer, use the IP address 127.0.0.1.

        <b>callback</b>: that keyword make the API run in "<i>HTTP Callback</i>" mode.
        This a special mode allowing to take control of Yoctopuce devices
        through a NAT filter when using a VirtualHub or a networked YoctoHub. You only
        need to configure your hub to call your server script on a regular basis.
        This mode is currently available for PHP and Node.JS only.

        Be aware that only one application can use direct USB access at a
        given time on a machine. Multiple access would cause conflicts
        while trying to access the USB modules. In particular, this means
        that you must stop the VirtualHub software before starting
        an application that uses direct USB access. The workaround
        for this limitation is to setup the library to use the VirtualHub
        rather than direct USB access.

        If access control has been activated on the hub, virtual or not, you want to
        reach, the URL parameter should look like:

        http://username:password@address:port

        You can call <i>RegisterHub</i> several times to connect to several machines.

        @param url : a string containing either "usb","callback" or the
                root URL of the hub to monitor
        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN + 1)
        if not YAPI._apiInitialized:
            res = YAPI.InitAPI(0, errmsg)
            if YAPI.YISERR(res):
                return res
        p = ctypes.create_string_buffer(url.encode("ASCII"))
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiRegisterHub(p, errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                errmsg.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def PreregisterHub(url, errmsg=None):
        """
        Fault-tolerant alternative to yRegisterHub(). This function has the same
        purpose and same arguments as yRegisterHub(), but does not trigger
        an error when the selected hub is not available at the time of the function call.
        This makes it possible to register a network hub independently of the current
        connectivity, and to try to contact it only when a device is actively needed.

        @param url : a string containing either "usb","callback" or the
                root URL of the hub to monitor
        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)

        if not YAPI._apiInitialized:
            res = YAPI.InitAPI(0, errmsg)
            if YAPI.YISERR(res):
                return res
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiPreregisterHub(ctypes.create_string_buffer(url.encode("ASCII")), errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                errmsg.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def UnregisterHub(url):
        """
        Setup the Yoctopuce library to no more use modules connected on a previously
        registered machine with RegisterHub.

        @param url : a string containing either "usb" or the
                root URL of the hub to monitor
        """
        if not YAPI._apiInitialized:
            return

        # noinspection PyUnresolvedReferences
        YAPI._yapiUnregisterHub(ctypes.create_string_buffer(url.encode("ASCII")))

    @staticmethod
    def TestHub(url, mstimeout, errmsg=None):
        """
        Test if the hub is reachable. This method do not register the hub, it only test if the
        hub is usable. The url parameter follow the same convention as the yRegisterHub
        method. This method is useful to verify the authentication parameters for a hub. It
        is possible to force this method to return after mstimeout milliseconds.

        @param url : a string containing either "usb","callback" or the
                root URL of the hub to monitor
        @param mstimeout : the number of millisecond available to test the connection.
        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()

        # noinspection PyUnresolvedReferences
        res = YAPI._yapiTestHub(ctypes.create_string_buffer(url.encode("ASCII")), mstimeout, errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                errmsg.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def UpdateDeviceList(errmsg=None):
        """
        Triggers a (re)detection of connected Yoctopuce modules.
        The library searches the machines or USB ports previously registered using
        yRegisterHub(), and invokes any user-defined callback function
        in case a change in the list of connected devices is detected.

        This function can be called as frequently as desired to refresh the device list
        and to make the application aware of hot-plug events. However, since device
        detection is quite a heavy process, UpdateDeviceList shouldn't be called more
        than once every two seconds.

        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        if not YAPI._apiInitialized:
            res = YAPI.InitAPI(0, errmsg)
            if YAPI.YISERR(res):
                return res
        res = YAPI.yapiUpdateDeviceList(0, errmsg)
        if YAPI.YISERR(res):
            return res
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiHandleEvents(errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                # noinspection PyAttributeOutsideInit
                errmsg.value = YByte2String(errmsg_buffer.value)
            return res
        while len(YAPI._PlugEvents) > 0:
            YAPI.yapiLockDeviceCallBack(errmsg)
            p = YAPI._PlugEvents.pop(0)
            YAPI.yapiUnlockDeviceCallBack(errmsg)
            p.invokePlug()
        return YAPI.SUCCESS

    @staticmethod
    def TriggerHubDiscovery(errmsg=None):
        """
        Force a hub discovery, if a callback as been registered with yRegisterHubDiscoveryCallback it
        will be called for each net work hub that will respond to the discovery.

        @param errmsg : a string passed by reference to receive any error message.

        @return YAPI.SUCCESS when the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN + 1)
        if not YAPI._apiInitialized:
            res = YAPI.InitAPI(0, errmsg)
            if YAPI.YISERR(res):
                return res
        res = YAPI._yapiTriggerHubDiscovery(errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsg is not None:
                errmsg.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def yapiGetFunctionInfo(fundesc, devdescRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef=None):
        serialBuffer = ctypes.create_string_buffer(YAPI.YOCTO_SERIAL_LEN)
        funcIdBuffer = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcNameBuffer = ctypes.create_string_buffer(YAPI.YOCTO_LOGICAL_LEN)
        funcValBuffer = ctypes.create_string_buffer(YAPI.YOCTO_PUBVAL_LEN)
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        p = ctypes.c_int()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundesc, ctypes.byref(p), serialBuffer, funcIdBuffer, None,
                                          funcNameBuffer, funcValBuffer, errBuffer)
        devdescRef.value = p.value
        serialRef.value = YByte2String(serialBuffer.value)
        funcIdRef.value = YByte2String(funcIdBuffer.value)
        funcNameRef.value = YByte2String(funcNameBuffer.value)
        funcValRef.value = YByte2String(funcValBuffer.value)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errBuffer.value)
        return res

    @staticmethod
    def yapiGetFunctionInfoEx(fundesc, devdescRef, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef,
                              errmsgRef=None):
        serialBuffer = ctypes.create_string_buffer(YAPI.YOCTO_SERIAL_LEN)
        funcIdBuffer = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        baseTypeBuffer = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcNameBuffer = ctypes.create_string_buffer(YAPI.YOCTO_LOGICAL_LEN)
        funcValBuffer = ctypes.create_string_buffer(YAPI.YOCTO_PUBVAL_LEN)
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        p = ctypes.c_int()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundesc, ctypes.byref(p), serialBuffer, funcIdBuffer, baseTypeBuffer,
                                          funcNameBuffer, funcValBuffer, errBuffer)
        devdescRef.value = p.value
        serialRef.value = YByte2String(serialBuffer.value)
        funcIdRef.value = YByte2String(funcIdBuffer.value)
        baseTypeRef.value = YByte2String(baseTypeBuffer.value)
        funcNameRef.value = YByte2String(funcNameBuffer.value)
        funcValRef.value = YByte2String(funcValBuffer.value)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errBuffer.value)
        return res

    @staticmethod
    def yapiGetDeviceByFunction(fundesc, errmsgRef=None):
        errBuffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        devdesc = ctypes.c_int()
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundesc, ctypes.byref(devdesc), None, None, None, None, None, errBuffer)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errBuffer.value)
        if res < 0:
            return res
        return devdesc.value

    @staticmethod
    def yapiUpdateDeviceList(force, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiUpdateDeviceList(force, errmsg_buffer)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def yapiGetDevice(device_str, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        p = ctypes.create_string_buffer(device_str.encode("ASCII"))
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetDevice(p, errmsg_buffer)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def yapiGetFunction(class_str, function_str, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunction(ctypes.create_string_buffer(class_str.encode("ASCII")),
                                    ctypes.create_string_buffer(function_str.encode("ASCII")), errmsg_buffer)
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def apiGetFunctionsByClass(class_str, precFuncDesc, dbuffer, maxsize, neededsizeRef, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        cneededsize = ctypes.c_int()
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionsByClass(ctypes.create_string_buffer(class_str.encode("ASCII")), precFuncDesc,
                                            dbuffer, maxsize, ctypes.byref(cneededsize), errmsg_buffer)
        # noinspection PyUnresolvedReferences
        neededsizeRef.value = cneededsize.value
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def apiGetFunctionsByDevice(devdesc, precFuncDesc, dbuffer, maxsize, neededsizeRef, errmsgRef=None):
        errmsg_buffer = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        cneededsize = ctypes.c_int()
        if not YAPI._ydllLoaded:
            YAPI.yloadYapiCDLL()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionsByDevice(devdesc, precFuncDesc, dbuffer, maxsize, ctypes.byref(cneededsize),
                                             errmsg_buffer)
        # noinspection PyUnresolvedReferences
        neededsizeRef.value = cneededsize.value
        if errmsgRef is not None:
            errmsgRef.value = YByte2String(errmsg_buffer.value)
        return res

    @staticmethod
    def pymodule_initialization():
        pass

    @staticmethod
    def pymodule_cleanup():
        del YAPI.YDevice_devCache[:]
        del YAPI._PlugEvents[:]
        del YAPI._DataEvents[:]
        YFunction._CalibHandlers.clear()


# --- (generated code: YFirmwareUpdate class start)
#noinspection PyProtectedMember
class YFirmwareUpdate(object):
    """
    The YFirmwareUpdate class let you control the firmware update of a Yoctopuce
    module. This class should not be instantiate directly, but instances should be retrieved
    using the YModule method module.updateFirmware.

    """
    #--- (end of generated code: YFirmwareUpdate class start)
    # --- (generated code: YFirmwareUpdate definitions)
    #--- (end of generated code: YFirmwareUpdate definitions)

    def __init__(self, serial, path, settings, force=False):
        # --- (generated code: YFirmwareUpdate attributes)
        self._serial = ''
        self._settings = ''
        self._firmwarepath = ''
        self._progress_msg = ''
        self._progress_c = 0
        self._progress = 0
        self._restore_step = 0
        self._force = 0
        #--- (end of generated code: YFirmwareUpdate attributes)
        self._serial = serial
        self._settings = settings
        self._firmwarepath = path
        self._force = force

    # --- (generated code: YFirmwareUpdate implementation)
    def _processMore(self, newupdate):
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # m
        # res
        # serial
        # firmwarepath
        # settings
        # prod_prefix
        # force
        if (self._progress_c < 100) and (self._progress_c != YAPI.VERSION_MISMATCH):
            serial = self._serial
            firmwarepath = self._firmwarepath
            settings = YByte2String(self._settings)
            if self._force:
                force = 1
            else:
                force = 0
            res = YAPI._yapiUpdateFirmwareEx(ctypes.create_string_buffer(YString2Byte(serial)), ctypes.create_string_buffer(YString2Byte(firmwarepath)), ctypes.create_string_buffer(YString2Byte(settings)), force, newupdate, errmsg)
            if (res == YAPI.VERSION_MISMATCH) and (len(self._settings) != 0):
                self._progress_c = res
                self._progress_msg = YByte2String(errmsg.value)
                return self._progress
            if res < 0:
                self._progress = res
                self._progress_msg = YByte2String(errmsg.value)
                return res
            self._progress_c = res
            self._progress = int((self._progress_c * 9) / (10))
            self._progress_msg = YByte2String(errmsg.value)
        else:
            if (len(self._settings) != 0):
                self._progress_msg = "restoring settings"
                m = YModule.FindModule(self._serial + ".module")
                if not (m.isOnline()):
                    return self._progress
                if self._progress < 95:
                    prod_prefix = (m.get_productName())[0: 0 + 8]
                    if prod_prefix == "YoctoHub":
                        YAPI.Sleep(1000)
                        self._progress = self._progress + 1
                        return self._progress
                    else:
                        self._progress = 95
                if self._progress < 100:
                    m.set_allSettingsAndFiles(self._settings)
                    m.saveToFlash()
                    self._settings = bytearray(0)
                    if self._progress_c == YAPI.VERSION_MISMATCH:
                        self._progress = YAPI.IO_ERROR
                        self._progress_msg = "Unable to update firmware"
                    else:
                        self._progress = 100
                        self._progress_msg = "success"
            else:
                self._progress = 100
                self._progress_msg = "success"
        return self._progress

    @staticmethod
    def GetAllBootLoaders():
        """
        Returns a list of all the modules in "firmware update" mode. Only devices
        connected over USB are listed. For devices connected to a YoctoHub, you
        must connect yourself to the YoctoHub web interface.

        @return an array of strings containing the serial numbers of devices in "firmware update" mode.
        """
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        smallbuff = ctypes.create_string_buffer(1024)
        # bigbuff
        # buffsize
        fullsize = ctypes.c_int()
        # yapi_res
        # bootloader_list
        bootladers = []
        fullsize.value = 0
        yapi_res = YAPI._yapiGetBootloaders(smallbuff, 1024, ctypes.byref(fullsize), errmsg)
        if yapi_res < 0:
            return bootladers
        if fullsize.value <= 1024:
            bootloader_list = YByte2String(smallbuff.value)
        else:
            buffsize = fullsize.value
            bigbuff = ctypes.create_string_buffer(buffsize)
            yapi_res = YAPI._yapiGetBootloaders(bigbuff, buffsize, ctypes.byref(fullsize), errmsg)
            if yapi_res < 0:
                bigbuff = None
                return bootladers
            else:
                bootloader_list = YByte2String(bigbuff.value)
            bigbuff = None
        if not (bootloader_list == ""):
            bootladers = (bootloader_list).split(',')
        return bootladers

    @staticmethod
    def CheckFirmware(serial, path, minrelease):
        """
        Test if the byn file is valid for this module. It is possible to pass a directory instead of a file.
        In that case, this method returns the path of the most recent appropriate byn file. This method will
        ignore any firmware older than minrelease.

        @param serial : the serial number of the module to update
        @param path : the path of a byn file or a directory that contains byn files
        @param minrelease : a positive integer

        @return : the path of the byn file to use, or an empty string if no byn files matches the requirement

        On failure, returns a string that starts with "error:".
        """
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        smallbuff = ctypes.create_string_buffer(1024)
        # bigbuff
        # buffsize
        fullsize = ctypes.c_int()
        # res
        # firmware_path
        # release
        fullsize.value = 0
        release = str(minrelease)
        res = YAPI._yapiCheckFirmware(ctypes.create_string_buffer(YString2Byte(serial)), ctypes.create_string_buffer(YString2Byte(release)), ctypes.create_string_buffer(YString2Byte(path)), smallbuff, 1024, ctypes.byref(fullsize), errmsg)
        if res < 0:
            firmware_path = "error:" + YByte2String(errmsg.value)
            return "error:" + YByte2String(errmsg.value)
        if fullsize.value <= 1024:
            firmware_path = YByte2String(smallbuff.value)
        else:
            buffsize = fullsize.value
            bigbuff = ctypes.create_string_buffer(buffsize)
            res = YAPI._yapiCheckFirmware(ctypes.create_string_buffer(YString2Byte(serial)), ctypes.create_string_buffer(YString2Byte(release)), ctypes.create_string_buffer(YString2Byte(path)), bigbuff, buffsize, ctypes.byref(fullsize), errmsg)
            if res < 0:
                firmware_path = "error:" + YByte2String(errmsg.value)
            else:
                firmware_path = YByte2String(bigbuff.value)
            bigbuff = None
        return firmware_path

    def get_progress(self):
        """
        Returns the progress of the firmware update, on a scale from 0 to 100. When the object is
        instantiated, the progress is zero. The value is updated during the firmware update process until
        the value of 100 is reached. The 100 value means that the firmware update was completed
        successfully. If an error occurs during the firmware update, a negative value is returned, and the
        error message can be retrieved with get_progressMessage.

        @return an integer in the range 0 to 100 (percentage of completion)
                or a negative error code in case of failure.
        """
        if self._progress >= 0:
            self._processMore(0)
        return self._progress

    def get_progressMessage(self):
        """
        Returns the last progress message of the firmware update process. If an error occurs during the
        firmware update process, the error message is returned

        @return a string  with the latest progress message, or the error message.
        """
        return self._progress_msg

    def startUpdate(self):
        """
        Starts the firmware update process. This method starts the firmware update process in background. This method
        returns immediately. You can monitor the progress of the firmware update with the get_progress()
        and get_progressMessage() methods.

        @return an integer in the range 0 to 100 (percentage of completion),
                or a negative error code in case of failure.

        On failure returns a negative error code.
        """
        # err
        # leng
        err = YByte2String(self._settings)
        leng = len(err)
        if (leng >= 6) and ("error:" == (err)[0: 0 + 6]):
            self._progress = -1
            self._progress_msg = (err)[6: 6 + leng - 6]
        else:
            self._progress = 0
            self._progress_c = 0
            self._processMore(1)
        return self._progress

#--- (end of generated code: YFirmwareUpdate implementation)
# --- (generated code: YFirmwareUpdate functions)
#--- (end of generated code: YFirmwareUpdate functions)


# --- (generated code: YDataStream class start)
#noinspection PyProtectedMember
class YDataStream(object):
    """
    DataStream objects represent bare recorded measure sequences,
    exactly as found within the data logger present on Yoctopuce
    sensors.

    In most cases, it is not necessary to use DataStream objects
    directly, as the DataSet objects (returned by the
    get_recordedData() method from sensors and the
    get_dataSets() method from the data logger) provide
    a more convenient interface.

    """
    #--- (end of generated code: YDataStream class start)
    # --- (generated code: YDataStream definitions)
    #--- (end of generated code: YDataStream definitions)

    DATA_INVALID = YAPI.INVALID_DOUBLE
    DURATION_INVALID = -1

    def __init__(self, parent, dataset=None, encoded=None):
        # --- (generated code: YDataStream attributes)
        self._parent = None
        self._runNo = 0
        self._utcStamp = 0
        self._nCols = 0
        self._nRows = 0
        self._startTime = 0
        self._duration = 0
        self._dataSamplesInterval = 0
        self._firstMeasureDuration = 0
        self._columnNames = []
        self._functionId = ''
        self._isClosed = 0
        self._isAvg = 0
        self._minVal = 0
        self._avgVal = 0
        self._maxVal = 0
        self._caltyp = 0
        self._calpar = []
        self._calraw = []
        self._calref = []
        self._values = []
        #--- (end of generated code: YDataStream attributes)
        self._calhdl = None
        self._parent = parent
        if dataset is not None:
            self._initFromDataSet(dataset, encoded)

    # --- (generated code: YDataStream implementation)
    def _initFromDataSet(self, dataset, encoded):
        # val
        # i
        # maxpos
        # ms_offset
        # samplesPerHour
        # fRaw
        # fRef
        iCalib = []
        # // decode sequence header to extract data
        self._runNo = encoded[0] + (((encoded[1]) << (16)))
        self._utcStamp = encoded[2] + (((encoded[3]) << (16)))
        val = encoded[4]
        self._isAvg = (((val) & (0x100)) == 0)
        samplesPerHour = ((val) & (0xff))
        if ((val) & (0x100)) != 0:
            samplesPerHour = samplesPerHour * 3600
        else:
            if ((val) & (0x200)) != 0:
                samplesPerHour = samplesPerHour * 60
        self._dataSamplesInterval = 3600.0 / samplesPerHour
        ms_offset = encoded[6]
        if ms_offset < 1000:
            # // new encoding . add the ms to the UTC timestamp
            self._startTime = self._utcStamp + (ms_offset / 1000.0)
        else:
            # // legacy encoding subtract the measure interval form the UTC timestamp
            self._startTime = self._utcStamp -  self._dataSamplesInterval
        self._firstMeasureDuration = encoded[5]
        if not (self._isAvg):
            self._firstMeasureDuration = self._firstMeasureDuration / 1000.0
        val = encoded[7]
        self._isClosed = (val != 0xffff)
        if val == 0xffff:
            val = 0
        self._nRows = val
        if self._nRows > 0:
            if self._firstMeasureDuration > 0:
                self._duration = self._firstMeasureDuration + (self._nRows - 1) * self._dataSamplesInterval
            else:
                self._duration = self._nRows * self._dataSamplesInterval
        else:
            self._duration = 0
        # // precompute decoding parameters
        iCalib = dataset._get_calibration()
        self._caltyp = iCalib[0]
        if self._caltyp != 0:
            self._calhdl = YAPI._getCalibrationHandler(self._caltyp)
            maxpos = len(iCalib)
            del self._calpar[:]
            del self._calraw[:]
            del self._calref[:]
            i = 1
            while i < maxpos:
                self._calpar.append(iCalib[i])
                i = i + 1
            i = 1
            while i + 1 < maxpos:
                fRaw = iCalib[i]
                fRaw = fRaw / 1000.0
                fRef = iCalib[i + 1]
                fRef = fRef / 1000.0
                self._calraw.append(fRaw)
                self._calref.append(fRef)
                i = i + 2
        # // preload column names for backward-compatibility
        self._functionId = dataset.get_functionId()
        if self._isAvg:
            del self._columnNames[:]
            self._columnNames.append("" + self._functionId + "_min")
            self._columnNames.append("" + self._functionId + "_avg")
            self._columnNames.append("" + self._functionId + "_max")
            self._nCols = 3
        else:
            del self._columnNames[:]
            self._columnNames.append(self._functionId)
            self._nCols = 1
        # // decode min/avg/max values for the sequence
        if self._nRows > 0:
            self._avgVal = self._decodeAvg(encoded[8] + (((((encoded[9]) ^ (0x8000))) << (16))), 1)
            self._minVal = self._decodeVal(encoded[10] + (((encoded[11]) << (16))))
            self._maxVal = self._decodeVal(encoded[12] + (((encoded[13]) << (16))))
        return 0

    def _parseStream(self, sdata):
        # idx
        udat = []
        dat = []
        if len(sdata) == 0:
            self._nRows = 0
            return YAPI.SUCCESS

        udat = YAPI._decodeWords(self._parent._json_get_string(sdata))
        del self._values[:]
        idx = 0
        if self._isAvg:
            while idx + 3 < len(udat):
                del dat[:]
                dat.append(self._decodeVal(udat[idx + 2] + (((udat[idx + 3]) << (16)))))
                dat.append(self._decodeAvg(udat[idx] + (((((udat[idx + 1]) ^ (0x8000))) << (16))), 1))
                dat.append(self._decodeVal(udat[idx + 4] + (((udat[idx + 5]) << (16)))))
                idx = idx + 6
                self._values.append(dat[:])
        else:
            while idx + 1 < len(udat):
                del dat[:]
                dat.append(self._decodeAvg(udat[idx] + (((((udat[idx + 1]) ^ (0x8000))) << (16))), 1))
                self._values.append(dat[:])
                idx = idx + 2

        self._nRows = len(self._values)
        return YAPI.SUCCESS

    def _get_url(self):
        # url
        url = "logger.json?id=" + self._functionId + "&run=" + str(int(self._runNo)) + "&utc=" + str(int(self._utcStamp))
        return url

    def loadStream(self):
        return self._parseStream(self._parent._download(self._get_url()))

    def _decodeVal(self, w):
        # val
        val = w if w <= 0x7fffffff else -0x100000000 + w
        val = val / 1000.0
        if self._caltyp != 0:
            if self._calhdl is not None:
                val = self._calhdl(val, self._caltyp, self._calpar, self._calraw, self._calref)
        return val

    def _decodeAvg(self, dw, count):
        # val
        val = dw if dw <= 0x7fffffff else -0x100000000 + dw
        val = val / 1000.0
        if self._caltyp != 0:
            if self._calhdl is not None:
                val = self._calhdl(val, self._caltyp, self._calpar, self._calraw, self._calref)
        return val

    def isClosed(self):
        return self._isClosed

    def get_runIndex(self):
        """
        Returns the run index of the data stream. A run can be made of
        multiple datastreams, for different time intervals.

        @return an unsigned number corresponding to the run index.
        """
        return self._runNo

    def get_startTime(self):
        """
        Returns the relative start time of the data stream, measured in seconds.
        For recent firmwares, the value is relative to the present time,
        which means the value is always negative.
        If the device uses a firmware older than version 13000, value is
        relative to the start of the time the device was powered on, and
        is always positive.
        If you need an absolute UTC timestamp, use get_realStartTimeUTC().

        <b>DEPRECATED</b>: This method has been replaced by get_realStartTimeUTC().

        @return an unsigned number corresponding to the number of seconds
                between the start of the run and the beginning of this data
                stream.
        """
        return self._utcStamp - int(time.time())

    def get_startTimeUTC(self):
        """
        Returns the start time of the data stream, relative to the Jan 1, 1970.
        If the UTC time was not set in the datalogger at the time of the recording
        of this data stream, this method returns 0.

        <b>DEPRECATED</b>: This method has been replaced by get_realStartTimeUTC().

        @return an unsigned number corresponding to the number of seconds
                between the Jan 1, 1970 and the beginning of this data
                stream (i.e. Unix time representation of the absolute time).
        """
        return int(round(self._startTime))

    def get_realStartTimeUTC(self):
        """
        Returns the start time of the data stream, relative to the Jan 1, 1970.
        If the UTC time was not set in the datalogger at the time of the recording
        of this data stream, this method returns 0.

        @return a floating-point number  corresponding to the number of seconds
                between the Jan 1, 1970 and the beginning of this data
                stream (i.e. Unix time representation of the absolute time).
        """
        return self._startTime

    def get_dataSamplesIntervalMs(self):
        """
        Returns the number of milliseconds between two consecutive
        rows of this data stream. By default, the data logger records one row
        per second, but the recording frequency can be changed for
        each device function

        @return an unsigned number corresponding to a number of milliseconds.
        """
        return int(round(self._dataSamplesInterval*1000))

    def get_dataSamplesInterval(self):
        return self._dataSamplesInterval

    def get_firstDataSamplesInterval(self):
        return self._firstMeasureDuration

    def get_rowCount(self):
        """
        Returns the number of data rows present in this stream.

        If the device uses a firmware older than version 13000,
        this method fetches the whole data stream from the device
        if not yet done, which can cause a little delay.

        @return an unsigned number corresponding to the number of rows.

        On failure, throws an exception or returns zero.
        """
        if (self._nRows != 0) and self._isClosed:
            return self._nRows
        self.loadStream()
        return self._nRows

    def get_columnCount(self):
        """
        Returns the number of data columns present in this stream.
        The meaning of the values present in each column can be obtained
        using the method get_columnNames().

        If the device uses a firmware older than version 13000,
        this method fetches the whole data stream from the device
        if not yet done, which can cause a little delay.

        @return an unsigned number corresponding to the number of columns.

        On failure, throws an exception or returns zero.
        """
        if self._nCols != 0:
            return self._nCols
        self.loadStream()
        return self._nCols

    def get_columnNames(self):
        """
        Returns the title (or meaning) of each data column present in this stream.
        In most case, the title of the data column is the hardware identifier
        of the sensor that produced the data. For streams recorded at a lower
        recording rate, the dataLogger stores the min, average and max value
        during each measure interval into three columns with suffixes _min,
        _avg and _max respectively.

        If the device uses a firmware older than version 13000,
        this method fetches the whole data stream from the device
        if not yet done, which can cause a little delay.

        @return a list containing as many strings as there are columns in the
                data stream.

        On failure, throws an exception or returns an empty array.
        """
        if len(self._columnNames) != 0:
            return self._columnNames
        self.loadStream()
        return self._columnNames

    def get_minValue(self):
        """
        Returns the smallest measure observed within this stream.
        If the device uses a firmware older than version 13000,
        this method will always return YDataStream.DATA_INVALID.

        @return a floating-point number corresponding to the smallest value,
                or YDataStream.DATA_INVALID if the stream is not yet complete (still recording).

        On failure, throws an exception or returns YDataStream.DATA_INVALID.
        """
        return self._minVal

    def get_averageValue(self):
        """
        Returns the average of all measures observed within this stream.
        If the device uses a firmware older than version 13000,
        this method will always return YDataStream.DATA_INVALID.

        @return a floating-point number corresponding to the average value,
                or YDataStream.DATA_INVALID if the stream is not yet complete (still recording).

        On failure, throws an exception or returns YDataStream.DATA_INVALID.
        """
        return self._avgVal

    def get_maxValue(self):
        """
        Returns the largest measure observed within this stream.
        If the device uses a firmware older than version 13000,
        this method will always return YDataStream.DATA_INVALID.

        @return a floating-point number corresponding to the largest value,
                or YDataStream.DATA_INVALID if the stream is not yet complete (still recording).

        On failure, throws an exception or returns YDataStream.DATA_INVALID.
        """
        return self._maxVal

    def get_realDuration(self):
        if self._isClosed:
            return self._duration
        return int(int(time.time()) - self._utcStamp)

    def get_dataRows(self):
        """
        Returns the whole data set contained in the stream, as a bidimensional
        table of numbers.
        The meaning of the values present in each column can be obtained
        using the method get_columnNames().

        This method fetches the whole data stream from the device,
        if not yet done.

        @return a list containing as many elements as there are rows in the
                data stream. Each row itself is a list of floating-point
                numbers.

        On failure, throws an exception or returns an empty array.
        """
        if (len(self._values) == 0) or not (self._isClosed):
            self.loadStream()
        return self._values

    def get_data(self, row, col):
        """
        Returns a single measure from the data stream, specified by its
        row and column index.
        The meaning of the values present in each column can be obtained
        using the method get_columnNames().

        This method fetches the whole data stream from the device,
        if not yet done.

        @param row : row index
        @param col : column index

        @return a floating-point number

        On failure, throws an exception or returns YDataStream.DATA_INVALID.
        """
        if (len(self._values) == 0) or not (self._isClosed):
            self.loadStream()
        if row >= len(self._values):
            return YDataStream.DATA_INVALID
        if col >= len(self._values[row]):
            return YDataStream.DATA_INVALID
        return self._values[row][col]

#--- (end of generated code: YDataStream implementation)
# --- (generated code: YDataStream functions)
#--- (end of generated code: YDataStream functions)


# --- (generated code: YMeasure class start)
#noinspection PyProtectedMember
class YMeasure(object):
    """
    YMeasure objects are used within the API to represent
    a value measured at a specified time. These objects are
    used in particular in conjunction with the YDataSet class,
    but also for sensors periodic timed reports
    (see sensor.registerTimedReportCallback).

    """
    #--- (end of generated code: YMeasure class start)
    # --- (generated code: YMeasure definitions)
    #--- (end of generated code: YMeasure definitions)

    def __init__(self, start, end, minVal, avgVal, maxVal):
        # --- (generated code: YMeasure attributes)
        self._start = 0
        self._end = 0
        self._minVal = 0
        self._avgVal = 0
        self._maxVal = 0
        #--- (end of generated code: YMeasure attributes)
        self._start = start
        self._end = end
        self._minVal = minVal
        self._avgVal = avgVal
        self._maxVal = maxVal
        rounded = int(start * 100 + 0.5)
        self._start_datetime = datetime.datetime.fromtimestamp(rounded / 100.0)
        rounded = int(end * 100 + 0.5)
        self._end_datetime = datetime.datetime.fromtimestamp(rounded / 100.0)

    def get_startTimeUTC_asDatetime(self):
        """
        """
        return self._start_datetime

    def get_endTimeUTC_asDatetime(self):
        """
        """
        return self._end_datetime

    # --- (generated code: YMeasure implementation)
    def get_startTimeUTC(self):
        """
        Returns the start time of the measure, relative to the Jan 1, 1970 UTC
        (Unix timestamp). When the recording rate is higher then 1 sample
        per second, the timestamp may have a fractional part.

        @return a floating point number corresponding to the number of seconds
                between the Jan 1, 1970 UTC and the beginning of this measure.
        """
        return self._start

    def get_endTimeUTC(self):
        """
        Returns the end time of the measure, relative to the Jan 1, 1970 UTC
        (Unix timestamp). When the recording rate is higher than 1 sample
        per second, the timestamp may have a fractional part.

        @return a floating point number corresponding to the number of seconds
                between the Jan 1, 1970 UTC and the end of this measure.
        """
        return self._end

    def get_minValue(self):
        """
        Returns the smallest value observed during the time interval
        covered by this measure.

        @return a floating-point number corresponding to the smallest value observed.
        """
        return self._minVal

    def get_averageValue(self):
        """
        Returns the average value observed during the time interval
        covered by this measure.

        @return a floating-point number corresponding to the average value observed.
        """
        return self._avgVal

    def get_maxValue(self):
        """
        Returns the largest value observed during the time interval
        covered by this measure.

        @return a floating-point number corresponding to the largest value observed.
        """
        return self._maxVal

#--- (end of generated code: YMeasure implementation)

# --- (generated code: YMeasure functions)
#--- (end of generated code: YMeasure functions)


# --- (generated code: YDataSet class start)
#noinspection PyProtectedMember
class YDataSet(object):
    """
    YDataSet objects make it possible to retrieve a set of recorded measures
    for a given sensor and a specified time interval. They can be used
    to load data points with a progress report. When the YDataSet object is
    instantiated by the sensor.get_recordedData()  function, no data is
    yet loaded from the module. It is only when the loadMore()
    method is called over and over than data will be effectively loaded
    from the dataLogger.

    A preview of available measures is available using the function
    get_preview() as soon as loadMore() has been called
    once. Measures themselves are available using function get_measures()
    when loaded by subsequent calls to loadMore().

    This class can only be used on devices that use a relatively recent firmware,
    as YDataSet objects are not supported by firmwares older than version 13000.

    """
    #--- (end of generated code: YDataSet class start)
    # --- (generated code: YDataSet definitions)
    #--- (end of generated code: YDataSet definitions)

    def __init__(self, parent, functionId=None, unit=None, starttime=None, endTime=None):
        # --- (generated code: YDataSet attributes)
        self._parent = None
        self._hardwareId = ''
        self._functionId = ''
        self._unit = ''
        self._startTimeMs = 0
        self._endTimeMs = 0
        self._progress = 0
        self._calib = []
        self._streams = []
        self._summary = None
        self._preview = []
        self._measures = []
        self._summaryMinVal = 0
        self._summaryMaxVal = 0
        self._summaryTotalAvg = 0
        self._summaryTotalTime = 0
        #--- (end of generated code: YDataSet attributes)
        self._summary = YMeasure(0, 0, 0, 0, 0)
        if unit is None:
            self._initFromJson(parent)
        else:
            self._initFromParams(parent, functionId, unit, starttime, endTime)

    def _initFromParams(self, parent, functionId, unit, startTime, endTime):
        self._parent = parent
        self._functionId = functionId
        self._unit = unit
        self._startTimeMs = startTime * 1000
        self._endTimeMs = endTime * 1000
        self._progress = -1

    def _initFromJson(self, parent):
        self._parent = parent
        self._startTimeMs = 0
        self._endTimeMs = 0

    def _parse(self, json):
        p = YJSONObject(json, 0, len(json))
        if not YAPI.ExceptionsDisabled:
            p.parse()
        else:
            try:
                p.parse()
            except Exception:
                return YAPI.IO_ERROR

        streamStartTime = 0x7fffffff
        streamEndTime = 0
        self._functionId = p.getString("id")
        self._unit = p.getString("unit")
        if p.has("calib"):
            self._calib = YAPI._decodeFloats(p.getString("calib"))
            self._calib[0] = round(self._calib[0] / 1000)
        else:
            self._calib = YAPI._decodeWords(p.getString("cal"))
        arr = p.getYJSONArray("streams")
        self._streams = []
        self._preview = []
        self._measures = []
        for i in range(0, arr.length()):
            stream = self._parent._findDataStream(self, arr.getString(i))
            streamStartTime = stream.get_realStartTimeUTC() * 1000
            streamEndTime = streamStartTime + stream.get_realDuration() * 1000
            if self._startTimeMs > 0 and streamEndTime <= self._startTimeMs:
                # this stream is too early, drop it
                pass
            elif self._endTimeMs > 0 and streamStartTime >= self._endTimeMs:
                # this stream is too late, drop it
                pass
            else:
                self._streams.append(stream)
        self._progress = 0
        return self.get_progress()

    # --- (generated code: YDataSet implementation)
    def _get_calibration(self):
        return self._calib

    def loadSummary(self, data):
        dataRows = []
        # tim
        # mitv
        # itv
        # fitv
        # end_
        # nCols
        # minCol
        # avgCol
        # maxCol
        # res
        # m_pos
        # previewTotalTime
        # previewTotalAvg
        # previewMinVal
        # previewMaxVal
        # previewAvgVal
        # previewStartMs
        # previewStopMs
        # previewDuration
        # streamStartTimeMs
        # streamDuration
        # streamEndTimeMs
        # minVal
        # avgVal
        # maxVal
        # summaryStartMs
        # summaryStopMs
        # summaryTotalTime
        # summaryTotalAvg
        # summaryMinVal
        # summaryMaxVal
        # url
        # strdata
        measure_data = []

        if self._progress < 0:
            strdata = YByte2String(data)
            if strdata == "{}":
                self._parent._throw(YAPI.VERSION_MISMATCH, "device firmware is too old")
                return YAPI.VERSION_MISMATCH
            res = self._parse(strdata)
            if res < 0:
                return res
        summaryTotalTime = 0
        summaryTotalAvg = 0
        summaryMinVal = YAPI.MAX_DOUBLE
        summaryMaxVal = YAPI.MIN_DOUBLE
        summaryStartMs = YAPI.MAX_DOUBLE
        summaryStopMs = YAPI.MIN_DOUBLE

        # // Parse complete streams
        for y in self._streams:
            streamStartTimeMs = round(y.get_realStartTimeUTC() *1000)
            streamDuration = y.get_realDuration()
            streamEndTimeMs = streamStartTimeMs + round(streamDuration * 1000)
            if (streamStartTimeMs >= self._startTimeMs) and ((self._endTimeMs == 0) or (streamEndTimeMs <= self._endTimeMs)):
                # // stream that are completely inside the dataset
                previewMinVal = y.get_minValue()
                previewAvgVal = y.get_averageValue()
                previewMaxVal = y.get_maxValue()
                previewStartMs = streamStartTimeMs
                previewStopMs = streamEndTimeMs
                previewDuration = streamDuration
            else:
                # // stream that are partially in the dataset
                # // we need to parse data to filter value outside the dataset
                url = y._get_url()
                data = self._parent._download(url)
                y._parseStream(data)
                dataRows = y.get_dataRows()
                if len(dataRows) == 0:
                    return self.get_progress()
                tim = streamStartTimeMs
                fitv = round(y.get_firstDataSamplesInterval() * 1000)
                itv = round(y.get_dataSamplesInterval() * 1000)
                nCols = len(dataRows[0])
                minCol = 0
                if nCols > 2:
                    avgCol = 1
                else:
                    avgCol = 0
                if nCols > 2:
                    maxCol = 2
                else:
                    maxCol = 0
                previewTotalTime = 0
                previewTotalAvg = 0
                previewStartMs = streamEndTimeMs
                previewStopMs = streamStartTimeMs
                previewMinVal = YAPI.MAX_DOUBLE
                previewMaxVal = YAPI.MIN_DOUBLE
                m_pos = 0
                while m_pos < len(dataRows):
                    measure_data  = dataRows[m_pos]
                    if m_pos == 0:
                        mitv = fitv
                    else:
                        mitv = itv
                    end_ = tim + mitv
                    if (end_ > self._startTimeMs) and ((self._endTimeMs == 0) or (tim < self._endTimeMs)):
                        minVal = measure_data[minCol]
                        avgVal = measure_data[avgCol]
                        maxVal = measure_data[maxCol]
                        if previewStartMs > tim:
                            previewStartMs = tim
                        if previewStopMs < end_:
                            previewStopMs = end_
                        if previewMinVal > minVal:
                            previewMinVal = minVal
                        if previewMaxVal < maxVal:
                            previewMaxVal = maxVal
                        previewTotalAvg = previewTotalAvg + (avgVal * mitv)
                        previewTotalTime = previewTotalTime + mitv
                    tim = end_
                    m_pos = m_pos + 1
                if previewTotalTime > 0:
                    previewAvgVal = previewTotalAvg / previewTotalTime
                    previewDuration = (previewStopMs - previewStartMs) / 1000.0
                else:
                    previewAvgVal = 0.0
                    previewDuration = 0.0
            self._preview.append(YMeasure(previewStartMs / 1000.0, previewStopMs / 1000.0, previewMinVal, previewAvgVal, previewMaxVal))
            if summaryMinVal > previewMinVal:
                summaryMinVal = previewMinVal
            if summaryMaxVal < previewMaxVal:
                summaryMaxVal = previewMaxVal
            if summaryStartMs > previewStartMs:
                summaryStartMs = previewStartMs
            if summaryStopMs < previewStopMs:
                summaryStopMs = previewStopMs
            summaryTotalAvg = summaryTotalAvg + (previewAvgVal * previewDuration)
            summaryTotalTime = summaryTotalTime + previewDuration
        if (self._startTimeMs == 0) or (self._startTimeMs > summaryStartMs):
            self._startTimeMs = summaryStartMs
        if (self._endTimeMs == 0) or (self._endTimeMs < summaryStopMs):
            self._endTimeMs = summaryStopMs
        if summaryTotalTime > 0:
            self._summary = YMeasure(summaryStartMs / 1000.0, summaryStopMs / 1000.0, summaryMinVal, summaryTotalAvg / summaryTotalTime, summaryMaxVal)
        else:
            self._summary = YMeasure(0.0, 0.0, YAPI.INVALID_DOUBLE, YAPI.INVALID_DOUBLE, YAPI.INVALID_DOUBLE)
        return self.get_progress()

    def processMore(self, progress, data):
        # stream
        dataRows = []
        # tim
        # itv
        # fitv
        # end_
        # nCols
        # minCol
        # avgCol
        # maxCol
        # firstMeasure

        if progress != self._progress:
            return self._progress
        if self._progress < 0:
            return self.loadSummary(data)
        stream = self._streams[self._progress]
        stream._parseStream(data)
        dataRows = stream.get_dataRows()
        self._progress = self._progress + 1
        if len(dataRows) == 0:
            return self.get_progress()
        tim = round(stream.get_realStartTimeUTC() * 1000)
        fitv = round(stream.get_firstDataSamplesInterval() * 1000)
        itv = round(stream.get_dataSamplesInterval() * 1000)
        if fitv == 0:
            fitv = itv
        if tim < itv:
            tim = itv
        nCols = len(dataRows[0])
        minCol = 0
        if nCols > 2:
            avgCol = 1
        else:
            avgCol = 0
        if nCols > 2:
            maxCol = 2
        else:
            maxCol = 0

        firstMeasure = True
        for y in dataRows:
            if firstMeasure:
                end_ = tim + fitv
                firstMeasure = False
            else:
                end_ = tim + itv
            if (end_ > self._startTimeMs) and ((self._endTimeMs == 0) or (tim < self._endTimeMs)):
                self._measures.append(YMeasure(tim / 1000, end_ / 1000, y[minCol], y[avgCol], y[maxCol]))
            tim = end_

        return self.get_progress()

    def get_privateDataStreams(self):
        return self._streams

    def get_hardwareId(self):
        """
        Returns the unique hardware identifier of the function who performed the measures,
        in the form SERIAL.FUNCTIONID. The unique hardware identifier is composed of the
        device serial number and of the hardware identifier of the function
        (for example THRMCPL1-123456.temperature1)

        @return a string that uniquely identifies the function (ex: THRMCPL1-123456.temperature1)

        On failure, throws an exception or returns  YDataSet.HARDWAREID_INVALID.
        """
        # mo
        if not (self._hardwareId == ""):
            return self._hardwareId
        mo = self._parent.get_module()
        self._hardwareId = "" + mo.get_serialNumber() + "." + self.get_functionId()
        return self._hardwareId

    def get_functionId(self):
        """
        Returns the hardware identifier of the function that performed the measure,
        without reference to the module. For example temperature1.

        @return a string that identifies the function (ex: temperature1)
        """
        return self._functionId

    def get_unit(self):
        """
        Returns the measuring unit for the measured value.

        @return a string that represents a physical unit.

        On failure, throws an exception or returns  YDataSet.UNIT_INVALID.
        """
        return self._unit

    def get_startTimeUTC(self):
        """
        Returns the start time of the dataset, relative to the Jan 1, 1970.
        When the YDataSet object is created, the start time is the value passed
        in parameter to the get_dataSet() function. After the
        very first call to loadMore(), the start time is updated
        to reflect the timestamp of the first measure actually found in the
        dataLogger within the specified range.

        <b>DEPRECATED</b>: This method has been replaced by get_summary()
        which contain more precise informations.

        @return an unsigned number corresponding to the number of seconds
                between the Jan 1, 1970 and the beginning of this data
                set (i.e. Unix time representation of the absolute time).
        """
        return self.imm_get_startTimeUTC()

    def imm_get_startTimeUTC(self):
        return int((self._startTimeMs / 1000.0))

    def get_endTimeUTC(self):
        """
        Returns the end time of the dataset, relative to the Jan 1, 1970.
        When the YDataSet object is created, the end time is the value passed
        in parameter to the get_dataSet() function. After the
        very first call to loadMore(), the end time is updated
        to reflect the timestamp of the last measure actually found in the
        dataLogger within the specified range.

        <b>DEPRECATED</b>: This method has been replaced by get_summary()
        which contain more precise informations.

        @return an unsigned number corresponding to the number of seconds
                between the Jan 1, 1970 and the end of this data
                set (i.e. Unix time representation of the absolute time).
        """
        return self.imm_get_endTimeUTC()

    def imm_get_endTimeUTC(self):
        return int(round(self._endTimeMs / 1000.0))

    def get_progress(self):
        """
        Returns the progress of the downloads of the measures from the data logger,
        on a scale from 0 to 100. When the object is instantiated by get_dataSet,
        the progress is zero. Each time loadMore() is invoked, the progress
        is updated, to reach the value 100 only once all measures have been loaded.

        @return an integer in the range 0 to 100 (percentage of completion).
        """
        if self._progress < 0:
            return 0
        # // index not yet loaded
        if self._progress >= len(self._streams):
            return 100
        return int((1 + (1 + self._progress) * 98) / ((1 + len(self._streams))))

    def loadMore(self):
        """
        Loads the the next block of measures from the dataLogger, and updates
        the progress indicator.

        @return an integer in the range 0 to 100 (percentage of completion),
                or a negative error code in case of failure.

        On failure, throws an exception or returns a negative error code.
        """
        # url
        # stream
        if self._progress < 0:
            url = "logger.json?id=" + self._functionId
            if self._startTimeMs != 0:
                url = "" + url + "&from=" + str(int(self.imm_get_startTimeUTC()))
            if self._endTimeMs != 0:
                url = "" + url + "&to=" + str(int(self.imm_get_endTimeUTC()+1))
        else:
            if self._progress >= len(self._streams):
                return 100
            else:
                stream = self._streams[self._progress]
                url = stream._get_url()
        try:
            return self.processMore(self._progress, self._parent._download(url))
        except:
            return self.processMore(self._progress, self._parent._download(url))

    def get_summary(self):
        """
        Returns an YMeasure object which summarizes the whole
        YDataSet. In includes the following information:
        - the start of a time interval
        - the end of a time interval
        - the minimal value observed during the time interval
        - the average value observed during the time interval
        - the maximal value observed during the time interval

        This summary is available as soon as loadMore() has
        been called for the first time.

        @return an YMeasure object
        """
        return self._summary

    def get_preview(self):
        """
        Returns a condensed version of the measures that can
        retrieved in this YDataSet, as a list of YMeasure
        objects. Each item includes:
        - the start of a time interval
        - the end of a time interval
        - the minimal value observed during the time interval
        - the average value observed during the time interval
        - the maximal value observed during the time interval

        This preview is available as soon as loadMore() has
        been called for the first time.

        @return a table of records, where each record depicts the
                measured values during a time interval

        On failure, throws an exception or returns an empty array.
        """
        return self._preview

    def get_measuresAt(self, measure):
        """
        Returns the detailed set of measures for the time interval corresponding
        to a given condensed measures previously returned by get_preview().
        The result is provided as a list of YMeasure objects.

        @param measure : condensed measure from the list previously returned by
                get_preview().

        @return a table of records, where each record depicts the
                measured values during a time interval

        On failure, throws an exception or returns an empty array.
        """
        # startUtcMs
        # stream
        dataRows = []
        measures = []
        # tim
        # itv
        # end_
        # nCols
        # minCol
        # avgCol
        # maxCol

        startUtcMs = measure.get_startTimeUTC() * 1000
        stream = None
        for y in self._streams:
            if round(y.get_realStartTimeUTC() *1000) == startUtcMs:
                stream = y
        if stream is None:
            return measures
        dataRows = stream.get_dataRows()
        if len(dataRows) == 0:
            return measures
        tim = round(stream.get_realStartTimeUTC() * 1000)
        itv = round(stream.get_dataSamplesInterval() * 1000)
        if tim < itv:
            tim = itv
        nCols = len(dataRows[0])
        minCol = 0
        if nCols > 2:
            avgCol = 1
        else:
            avgCol = 0
        if nCols > 2:
            maxCol = 2
        else:
            maxCol = 0

        for y in dataRows:
            end_ = tim + itv
            if (end_ > self._startTimeMs) and ((self._endTimeMs == 0) or (tim < self._endTimeMs)):
                measures.append(YMeasure(tim / 1000.0, end_ / 1000.0, y[minCol], y[avgCol], y[maxCol]))
            tim = end_

        return measures

    def get_measures(self):
        """
        Returns all measured values currently available for this DataSet,
        as a list of YMeasure objects. Each item includes:
        - the start of the measure time interval
        - the end of the measure time interval
        - the minimal value observed during the time interval
        - the average value observed during the time interval
        - the maximal value observed during the time interval

        Before calling this method, you should call loadMore()
        to load data from the device. You may have to call loadMore()
        several time until all rows are loaded, but you can start
        looking at available data rows before the load is complete.

        The oldest measures are always loaded first, and the most
        recent measures will be loaded last. As a result, timestamps
        are normally sorted in ascending order within the measure table,
        unless there was an unexpected adjustment of the datalogger UTC
        clock.

        @return a table of records, where each record depicts the
                measured value for a given time interval

        On failure, throws an exception or returns an empty array.
        """
        return self._measures

#--- (end of generated code: YDataSet implementation)

# --- (generated code: YDataSet functions)
#--- (end of generated code: YDataSet functions)


# --- (generated code: YConsolidatedDataSet class start)
#noinspection PyProtectedMember
class YConsolidatedDataSet(object):
    """
    YConsolidatedDataSet objects make it possible to retrieve a set of
    recorded measures from multiple sensors, for a specified time interval.
    They can be used to load data points progressively, and to receive
    data records by timestamp, one by one..

    """
    #--- (end of generated code: YConsolidatedDataSet class start)
    # --- (generated code: YConsolidatedDataSet definitions)
    #--- (end of generated code: YConsolidatedDataSet definitions)

    def __init__(self, start, end, sensorList):
        # --- (generated code: YConsolidatedDataSet attributes)
        self._start = 0
        self._end = 0
        self._nsensors = 0
        self._sensors = []
        self._datasets = []
        self._progresss = []
        self._nextidx = []
        self._nexttim = []
        #--- (end of generated code: YConsolidatedDataSet attributes)
        self.imm_init(start, end, sensorList)

    # --- (generated code: YConsolidatedDataSet implementation)
    def imm_init(self, startt, endt, sensorList):
        self._start = startt
        self._end = endt
        self._sensors = sensorList
        self._nsensors = -1
        return YAPI.SUCCESS

    @staticmethod
    def Init(sensorNames, startTime, endTime):
        """
        Returns an object holding historical data for multiple
        sensors, for a specified time interval.
        The measures will be retrieved from the data logger, which must have been turned
        on at the desired time. The resulting object makes it possible to load progressively
        a large set of measures from multiple sensors, consolidating data on the fly
        to align records based on measurement timestamps.

        @param sensorNames : array of logical names or hardware identifiers of the sensors
                for which data must be loaded from their data logger.
        @param startTime : the start of the desired measure time interval,
                as a Unix timestamp, i.e. the number of seconds since
                January 1, 1970 UTC. The special value 0 can be used
                to include any measure, without initial limit.
        @param endTime : the end of the desired measure time interval,
                as a Unix timestamp, i.e. the number of seconds since
                January 1, 1970 UTC. The special value 0 can be used
                to include any measure, without ending limit.

        @return an instance of YConsolidatedDataSet, providing access to
                consolidated historical data. Records can be loaded progressively
                using the YConsolidatedDataSet.nextRecord() method.
        """
        # nSensors
        sensorList = []
        # idx
        # sensorName
        # s
        # obj
        nSensors = len(sensorNames)
        del sensorList[:]
        idx = 0
        while idx < nSensors:
            sensorName = sensorNames[idx]
            s = YSensor.FindSensor(sensorName)
            sensorList.append(s)
            idx = idx + 1

        obj = YConsolidatedDataSet(startTime, endTime, sensorList)
        return obj

    def nextRecord(self, datarec):
        """
        Extracts the next data record from the data logger of all sensors linked to this
        object.

        @param datarec : array of floating point numbers, that will be filled by the
                function with the timestamp of the measure in first position,
                followed by the measured value in next positions.

        @return an integer in the range 0 to 100 (percentage of completion),
                or a negative error code in case of failure.

        On failure, throws an exception or returns a negative error code.
        """
        # s
        # idx
        # sensor
        # newdataset
        # globprogress
        # currprogress
        # currnexttim
        # newvalue
        measures = []
        # nexttime
        # //
        # // Ensure the dataset have been retrieved
        # //
        if self._nsensors == -1:
            self._nsensors = len(self._sensors)
            del self._datasets[:]
            del self._progresss[:]
            del self._nextidx[:]
            del self._nexttim[:]
            s = 0
            while s < self._nsensors:
                sensor = self._sensors[s]
                newdataset = sensor.get_recordedData(self._start, self._end)
                self._datasets.append(newdataset)
                self._progresss.append(0)
                self._nextidx.append(0)
                self._nexttim.append(0.0)
                s = s + 1
        del datarec[:]
        # //
        # // Find next timestamp to process
        # //
        nexttime = 0
        s = 0
        while s < self._nsensors:
            currnexttim = self._nexttim[s]
            if currnexttim == 0:
                idx = self._nextidx[s]
                measures = self._datasets[s].get_measures()
                currprogress = self._progresss[s]
                while (idx >= len(measures)) and (currprogress < 100):
                    currprogress = self._datasets[s].loadMore()
                    if currprogress < 0:
                        currprogress = 100
                    self._progresss[s] = currprogress
                    measures = self._datasets[s].get_measures()
                if idx < len(measures):
                    currnexttim = measures[idx].get_endTimeUTC()
                    self._nexttim[s] = currnexttim
            if currnexttim > 0:
                if (nexttime == 0) or (nexttime > currnexttim):
                    nexttime = currnexttim
            s = s + 1
        if nexttime == 0:
            return 100
        # //
        # // Extract data for this timestamp
        # //
        del datarec[:]
        datarec.append(nexttime)
        globprogress = 0
        s = 0
        while s < self._nsensors:
            if self._nexttim[s] == nexttime:
                idx = self._nextidx[s]
                measures = self._datasets[s].get_measures()
                newvalue = measures[idx].get_averageValue()
                datarec.append(newvalue)
                self._nexttim[s] = 0.0
                self._nextidx[s] = idx+1
            else:
                datarec.append(float('nan'))
            currprogress = self._progresss[s]
            globprogress = globprogress + currprogress
            s = s + 1
        if globprogress > 0:
            globprogress = int((globprogress) / (self._nsensors))
            if globprogress > 99:
                globprogress = 99

        return globprogress

#--- (end of generated code: YConsolidatedDataSet implementation)

# --- (generated code: YConsolidatedDataSet functions)
#--- (end of generated code: YConsolidatedDataSet functions)

# ------------------------------------------------------------------------------------
# YDevice
# ------------------------------------------------------------------------------------

# noinspection PyProtectedMember
class YDevice:
    def __init__(self, devdesc):
        self._devdescr = devdesc
        self._cacheStamp = datetime.datetime(year=1970, month=1, day=1)
        self._cacheJson = None
        self._functions = []
        self._rootdevice = ""
        self._subpath = ""
        self._subpathinit = False

    def __del__(self):
        if self._cacheJson is not None:
            del self._cacheJson
        self._cacheJson = None

    @staticmethod
    def getDevice(devdescr):
        for idx in range(len(YAPI.YDevice_devCache)):
            if YAPI.YDevice_devCache[idx]._devdescr == devdescr:
                return YAPI.YDevice_devCache[idx]

        dev = YDevice(devdescr)
        YAPI.YDevice_devCache.append(dev)
        return dev

    @staticmethod
    def PlugDevice(devdescr):
        for idx in range(len(YAPI.YDevice_devCache)):
            if YAPI.YDevice_devCache[idx]._devdescr == devdescr:
                YAPI.YDevice_devCache[idx].clearCache()
                YAPI.YDevice_devCache[idx]._subpathinit = False

    def _HTTPRequestPrepare(self, request):
        errbuf = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        root = ctypes.create_string_buffer(YAPI.YOCTO_SERIAL_LEN)

        if not self._subpathinit:
            neededsize = ctypes.c_int()
            # noinspection PyUnresolvedReferences
            res = YAPI._yapiGetDevicePath(self._devdescr, root, None, 0, ctypes.byref(neededsize), errbuf)
            if YAPI.YISERR(res):
                return res, YByte2String(errbuf.value)
                # noinspection PyUnresolvedReferences
            b = ctypes.create_string_buffer(neededsize.value)
            tmp = ctypes.c_int()
            # noinspection PyUnresolvedReferences
            res = YAPI._yapiGetDevicePath(self._devdescr, root, b, neededsize.value, ctypes.byref(tmp), errbuf)
            if YAPI.YISERR(res):
                return res, YByte2String(errbuf.value)
            self._rootdevice = YByte2String(root.value)
            self._subpath = YByte2String(b.value)
            self._subpathinit = True

        # request can be a purely binary buffer or a text string
        if isinstance(request, bytearray):
            request = bytes(request)
        elif not isinstance(request, bytes):
            request = YString2Byte(request)
            # first / is expected within very first characters of the query
        p = 0
        while p < 10 and YGetByte(request, p) != 47:  # chr(47) = '/'
            p += 1
        newrequest = request[0:p] + self._subpath.encode("ASCII") + request[p + 1:]
        return YAPI.SUCCESS, newrequest

    # noinspection PyUnresolvedReferences,PyUnusedLocal
    def HTTPRequestAsync(self, request, callback, context, errmsgRef=None):
        errbuf = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # invalidate cache
        self._cacheStamp = YAPI.GetTickCount()
        (res, newrequest) = self._HTTPRequestPrepare(request)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = newrequest
            return res
        res = YAPI._yapiHTTPRequestAsync(ctypes.create_string_buffer(self._rootdevice.encode("ASCII")),
                                         ctypes.create_string_buffer(newrequest), None, None, errbuf)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = YByte2String(errbuf.value)
            return res
        return YAPI.SUCCESS

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    def HTTPRequest(self, request, bufferRef, errmsgRef=None):
        (res, newrequest) = self._HTTPRequestPrepare(request)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = newrequest
            return res
        iohdl = ctypes.create_string_buffer(YAPI.YIOHDL_SIZE)
        errbuf = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        root_c = ctypes.create_string_buffer(self._rootdevice.encode("ASCII"))
        newrequest_c = ctypes.create_string_buffer(newrequest)
        reply_c = POINTER(ctypes.c_ubyte)()
        neededsize_c = ctypes.c_int(0)
        res = YAPI._yapiHTTPRequestSyncStartEx(iohdl, root_c, newrequest_c, len(newrequest), ctypes.byref(reply_c),
                                               ctypes.byref(neededsize_c), errbuf)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = YByte2String(errbuf.value)
            return res
        reply_size = neededsize_c.value
        bb = YString2Byte("")
        # (xrange not supported in 2.5.x)
        for i in range(reply_size):
            bb = YAddByte(bb, reply_c[i])
        bufferRef.value = bb
        res = YAPI._yapiHTTPRequestSyncDone(iohdl, errbuf)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = YByte2String(errbuf.value)
            return res
        return YAPI.SUCCESS

    def requestAPI(self, apiresRef, errmsgRef=None):

        http_data = YRefParam()

        # Check if we have a valid cache value
        if self._cacheStamp > YAPI.GetTickCount():
            apiresRef.value = self._cacheJson
            return YAPI.SUCCESS
        request = "GET /api.json"
        if self._cacheJson is not None:
            fwrelease = self._cacheJson.getYJSONObject("module").getString("firmwareRelease")
            fwrelease = YFunction._escapeAttr(fwrelease)
            request += "?fw=" + fwrelease
            # print("JZON:"+ request)

        res = self.HTTPRequest(request + " \r\n\r\n", http_data, errmsgRef)
        if YAPI.YISERR(res):
            # make sure a device scan does not solve the issue
            res = YAPI.yapiUpdateDeviceList(1, errmsgRef)
            if YAPI.YISERR(res):
                if not YAPI.ExceptionsDisabled:
                    raise YAPI.YAPI_Exception(res, errmsgRef.value)
                return res

            res = self.HTTPRequest(request + " \r\n\r\n", http_data, errmsgRef)
            if YAPI.YISERR(res):
                if not YAPI.ExceptionsDisabled:
                    raise YAPI.YAPI_Exception(res, errmsgRef.value)
                return res

        buffer = YByte2String(http_data.value)
        (httpcode, http_headerlen, errmsg) = YAPI.parseHTTP(buffer, 0, len(buffer))
        if httpcode != 200:
            errmsgRef.value = "Unexpected HTTP return code:%s" % httpcode
            if not YAPI.ExceptionsDisabled:
                raise YAPI.YAPI_Exception(res, errmsgRef.value)
            return YAPI.IO_ERROR
        try:
            apires = YJSONObject(buffer, http_headerlen, len(buffer))
            apires.parseWithRef(self._cacheJson)
        except YAPI_Exception as ex:
            self._cacheJson = None
            if errmsgRef is not None:
                errmsgRef.value = "JSON error: " + ex.errorMessage
            if not YAPI.ExceptionsDisabled:
                raise YAPI.YAPI_Exception(res, errmsgRef.value)
            return YAPI.IO_ERROR
        # store result in cache
        self._cacheJson = apires
        apiresRef.value = apires
        self._cacheStamp = YAPI.GetTickCount() + YAPI.DefaultCacheValidity

        return YAPI.SUCCESS

    def clearCache(self):
        self._cacheJson = None
        self._cacheStamp = datetime.datetime(year=1970, month=1, day=1)

    # noinspection PyTypeChecker,PyTypeChecker,PyTypeChecker
    def getFunctions(self, functionsRef, errmsgRef=None):

        neededsize = YRefParam()
        if not len(self._functions):
            res = YAPI.apiGetFunctionsByDevice(self._devdescr, 0, None, 64, neededsize, errmsgRef)
            if YAPI.YISERR(res):
                return res

            count = int(neededsize.value / YAPI.C_INTSIZE)
            # noinspection PyCallingNonCallable
            p = (ctypes.c_int * count)()

            res = YAPI.apiGetFunctionsByDevice(self._devdescr, 0, p, 64, neededsize, errmsgRef)
            if YAPI.YISERR(res):
                return res

            for i in range(count):
                self._functions.append(p[i])

        functionsRef.value = self._functions
        return YAPI.SUCCESS


# - keeps a reference to our callbacks, to  protect them from GC
# noinspection PyProtectedMember
native_yLogFunctionAnchor = YAPI._yapiLogFunc(YAPI.native_yLogFunction)
# noinspection PyProtectedMember
native_yFunctionUpdateAnchor = YAPI._yapiFunctionUpdateFunc(YAPI.native_yFunctionUpdateCallback)
# noinspection PyProtectedMember
native_yTimedReportAnchor = YAPI._yapiTimedReportFunc(YAPI.native_yTimedReportCallback)
# noinspection PyProtectedMember
native_yDeviceArrivalAnchor = YAPI._yapiDeviceUpdateFunc(YAPI.native_yDeviceArrivalCallback)
# noinspection PyProtectedMember
native_yDeviceRemovalAnchor = YAPI._yapiDeviceUpdateFunc(YAPI.native_yDeviceRemovalCallback)
# noinspection PyProtectedMember
native_yDeviceChangeAnchor = YAPI._yapiDeviceUpdateFunc(YAPI.native_yDeviceChangeCallback)
# noinspection PyProtectedMember
native_yDeviceConfigChangeAnchor = YAPI._yapiDeviceUpdateFunc(YAPI.native_yDeviceConfigChangeCallback)
# noinspection PyProtectedMember
native_yBeaconChangeCallbackAnchor = YAPI._yapiBeaconUpdateFunc(YAPI.native_yBeaconChangeCallback)
# noinspection PyProtectedMember
native_yHubDiscoveryAnchor = YAPI._yapiHubDiscoveryCallback(YAPI.native_HubDiscoveryCallback)
# noinspection PyProtectedMember
native_yDeviceLogAnchor = YAPI._yapiDeviceLogCallback(YAPI.native_DeviceLogCallback)


# --- (generated code: YFunction class start)
#noinspection PyProtectedMember
class YFunction(object):
    """
    This is the parent class for all public objects representing device functions documented in
    the high-level programming API. This abstract class does all the real job, but without
    knowledge of the specific function attributes.

    Instantiating a child class of YFunction does not cause any communication.
    The instance simply keeps track of its function identifier, and will dynamically bind
    to a matching device at the time it is really being used to read or set an attribute.
    In order to allow true hot-plug replacement of one device by another, the binding stay
    dynamic through the life of the object.

    The YFunction class implements a generic high-level cache for the attribute values of
    the specified function, pre-parsed from the REST API string.

    """
    #--- (end of generated code: YFunction class start)
    _cache = {}
    _FunctionCallbacks = []
    _TimedReportCallbackList = []
    _CalibHandlers = {}

    FUNCTIONDESCRIPTOR_INVALID = -1
    HARDWAREID_INVALID = YAPI.INVALID_STRING
    FUNCTIONID_INVALID = YAPI.INVALID_STRING
    FRIENDLYNAME_INVALID = YAPI.INVALID_STRING
    # --- (generated code: YFunction definitions)
    LOGICALNAME_INVALID = YAPI.INVALID_STRING
    ADVERTISEDVALUE_INVALID = YAPI.INVALID_STRING
    #--- (end of generated code: YFunction definitions)

    def __init__(self, func):
        self._className = 'Function'
        self._func = func
        self._lastErrorType = YAPI.SUCCESS
        self._lastErrorMsg = ""
        self._fundescr = YFunction.FUNCTIONDESCRIPTOR_INVALID
        self._userData = None
        self._genCallback = None
        self._dataStreams = dict()
        # --- (generated code: YFunction attributes)
        self._callback = None
        self._logicalName = YFunction.LOGICALNAME_INVALID
        self._advertisedValue = YFunction.ADVERTISEDVALUE_INVALID
        self._valueCallbackFunction = None
        self._cacheExpiration = datetime.datetime.fromtimestamp(86400)
        self._serial = ''
        self._funId = ''
        self._hwId = ''
        #--- (end of generated code: YFunction attributes)

    @staticmethod
    def _FindFromCache(class_name, func):
        key = class_name + "_" + func
        if key in YFunction._cache:
            return YFunction._cache[key]
        return None

    @staticmethod
    def _AddToCache(class_name, func, obj):
        YFunction._cache[class_name + "_" + func] = obj

    @staticmethod
    def _ClearCache():
        YFunction._cache.clear()

    @staticmethod
    def _UpdateValueCallbackList(func, add):
        if add:
            func.isOnline()
            if func not in YFunction._FunctionCallbacks:
                YFunction._FunctionCallbacks.append(func)
        else:
            if func in YFunction._FunctionCallbacks:
                index = YFunction._FunctionCallbacks.index(func)
                del YFunction._FunctionCallbacks[index]

    @staticmethod
    def _UpdateTimedReportCallbackList(func, add):
        if add:
            func.isOnline()
            if func not in YFunction._TimedReportCallbackList:
                YFunction._TimedReportCallbackList.append(func)
        else:
            if func in YFunction._TimedReportCallbackList:
                index = YFunction._TimedReportCallbackList.index(func)
                del YFunction._TimedReportCallbackList[index]

    def _throw(self, errType, errorMessage):
        self._lastErrorType = errType
        self._lastErrorMsg = errorMessage
        if not YAPI.ExceptionsDisabled:
            raise YAPI.YAPI_Exception(errType, "YoctoApi error : " + errorMessage)

    # Method used to resolve our name to our unique function descriptor (may trigger a hub scan)
    def _getDescriptor(self, fundescrRef, errmsgRef=None):
        tmp_fundescr = YAPI.yapiGetFunction(self._className, self._func, errmsgRef)
        if YAPI.YISERR(tmp_fundescr):
            res = YAPI.yapiUpdateDeviceList(1, errmsgRef)
            if YAPI.YISERR(res):
                return res
        tmp_fundescr = YAPI.yapiGetFunction(self._className, self._func, errmsgRef)
        if YAPI.YISERR(tmp_fundescr):
            return tmp_fundescr

        self._fundescr = tmp_fundescr
        fundescrRef.value = tmp_fundescr
        return YAPI.SUCCESS

        # Return a pointer to our device caching object (may trigger a hub scan)

    def _getDevice(self, devRef, errmsgRef=None):
        fundescrRef = YRefParam()
        # Resolve function name
        # Resolve function name
        res = self._getDescriptor(fundescrRef, errmsgRef)
        if YAPI.YISERR(res):
            return res

        # Get device descriptor
        devdescr = YAPI.yapiGetDeviceByFunction(fundescrRef.value, errmsgRef)
        if YAPI.YISERR(devdescr):
            return devdescr

        # Get device object
        devRef.value = YDevice.getDevice(devdescr)
        return YAPI.SUCCESS

    # Return the next known function of current class listed in the yellow pages
    def _nextFunction(self, hwidRef):
        fundescrRef = YRefParam()
        devdescrRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        neededsizeRef = YRefParam()
        errmsgRef = YRefParam()
        n_element = 1

        res = self._getDescriptor(fundescrRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        maxsize = n_element * YAPI.C_INTSIZE
        # noinspection PyCallingNonCallable,PyTypeChecker
        p = (ctypes.c_int * n_element)()

        res = YAPI.apiGetFunctionsByClass(self._className, fundescrRef.value, p, maxsize, neededsizeRef, errmsgRef)

        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        # noinspection PyTypeChecker
        count = neededsizeRef.value / YAPI.C_INTSIZE
        if not count:
            hwidRef.value = ""
            return YAPI.SUCCESS

        res = YAPI.yapiGetFunctionInfo(p[0], devdescrRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return YAPI.SUCCESS

        hwidRef.value = serialRef.value + "." + funcIdRef.value
        return YAPI.SUCCESS

    @staticmethod
    def _escapeAttr(changeval):
        uchangeval = ""
        ofs = 0
        nb_bytes = len(changeval)
        while ofs < nb_bytes:
            c = changeval[ofs]
            if c <= ' ' or \
                    (c > 'z' and c != '~') or c == '"' or c == '%' or c == '&' or c == '+' or \
                    c == '<' or c == '=' or c == '>' or c == '\\' or c == '^' or c == '`':
                c_ord = ord(c)
                if ((c_ord == 0xc2 or c_ord == 0xc3) and (ofs + 1 < nb_bytes) and (
                        ord(changeval[ofs + 1]) & 0xc0) == 0x80):
                    # UTF8-encoded ISO-8859-1 character: translate to plain ISO-8859-1
                    c_ord = (c_ord & 1) * 0x40
                    ofs += 1
                    c_ord += ord(changeval[ofs])
                uchangeval += "%" + ('%02X' % c_ord)
            else:
                uchangeval += c
            ofs += 1
        return uchangeval

    def _buildSetRequest(self, changeattr, changeval, requestRef, errmsgRef=None):
        fundescRef = YRefParam()
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        if YAPI.YISERR(res):
            return res
        devdesc = ctypes.c_int()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), None, funcid, None, None, None,
                                          errbuff)
        if YAPI.YISERR(res):
            if errmsgRef is not None:
                errmsgRef.value = YByte2String(errbuff.value)
            self._throw(res, errmsgRef.value)
            return res
        requestRef.value = "GET /api/" + YByte2String(funcid.value) + "/"
        if changeattr != "":
            requestRef.value += changeattr + "?" + changeattr + "=" + self._escapeAttr(changeval)
        requestRef.value += "&. \r\n\r\n"
        return YAPI.SUCCESS

    def _parse(self, j):
        self._parseAttr(j)
        self._parserHelper()
        return 0

    # Set an attribute in the function, and parse the resulting new function state
    def _setAttr(self, attrname, newvalue):
        errmsgRef = YRefParam()
        requestRef = YRefParam()
        devRef = YRefParam()

        #  Execute http request
        res = self._buildSetRequest(attrname, newvalue, requestRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        # Get device Object
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        res = devRef.value.HTTPRequestAsync(requestRef.value, None, None, errmsgRef)
        if YAPI.YISERR(res):
            # make sure a device scan does not solve the issue
            res = YAPI.yapiUpdateDeviceList(1, errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return res

            res = devRef.value.HTTPRequestAsync(requestRef.value, None, None, errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return res

        if self._cacheExpiration != datetime.datetime.fromtimestamp(86400):
            self._cacheExpiration = YAPI.GetTickCount()

        return YAPI.SUCCESS

    def _request(self, request):
        errmsgRef = YRefParam()
        httpbuffer = YRefParam()
        devRef = YRefParam()
        # Get device Object
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, request)
            return b""
        res = devRef.value.HTTPRequest(request, httpbuffer, errmsgRef)
        if YAPI.YISERR(res):
            # make sure a device scan does not solve the issue
            res = YAPI.yapiUpdateDeviceList(1, errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return b""
            res = devRef.value.HTTPRequest(request, httpbuffer, errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return b""
        if len(httpbuffer.value) >= 4:
            check = httpbuffer.value[0:4].decode("latin1")
            if check == "OK\r\n":
                return httpbuffer.value
            if len(httpbuffer.value) >= 17:
                check = httpbuffer.value[0:17].decode("latin1")
                if check == "HTTP/1.1 200 OK\r\n":
                    return httpbuffer.value
        self._throw(YAPI.IO_ERROR, "http request failed")
        return b""

    def _upload(self, path, content):
        tmpbuffer = self._uploadEx(path, content)
        if len(tmpbuffer) == 0:
            return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def _uploadEx(self, path, content):
        body = "Content-Disposition: form-data; name=\"" + path + "\"; filename=\"api\"\r\n"
        body += "Content-Type: application/octet-stream\r\n"
        body += "Content-Transfer-Encoding: binary\r\n\r\n"
        if isinstance(content, bytearray):
            content = bytes(content)
        elif not isinstance(content, bytes):
            if isinstance(content, array.array):
                content = content.tostring()
            else:
                content = content.encode("latin1")
        body = body.encode("ASCII") + content
        boundary = "Zz%06xzZ" % (random.randint(0, 0xffffff))
        request = "POST /upload.html HTTP/1.1\r\n"
        request += "Content-Type: multipart/form-data, boundary=" + boundary + "\r\n"
        request += "\r\n--" + boundary + "\r\n"
        request = request.encode("ASCII") + body + str("\r\n--" + boundary + "--\r\n").encode("ASCII")
        tmpbuffer = self._request(request)
        return self._strip_http_header(tmpbuffer)

    def _download(self, url):
        request = "GET /" + url + " HTTP/1.1\r\n\r\n"
        result_buffer = self._request(request)
        return self._strip_http_header(result_buffer)

    def _strip_http_header(self, result_buffer):
        found = 0
        while found <= len(result_buffer) - 4:
            if YGetByte(result_buffer, found) == 13 \
                    and YGetByte(result_buffer, found + 1) == 10 \
                    and YGetByte(result_buffer, found + 2) == 13 \
                    and YGetByte(result_buffer, found + 3) == 10:
                break
            found += 1
        if found > len(result_buffer) - 4:
            self._throw(YAPI.IO_ERROR, "http request failed")
            return ''
        return result_buffer[found + 4:]

    # noinspection PyMethodMayBeStatic
    def _json_get_key(self, json, key):
        json_str = YByte2String(json)
        obj = YJSONObject(json_str, 0, len(json_str))
        obj.parse()
        if obj.has(key):
            val = obj.getString(key)
            if val is None:
                return obj.toString()
            return val
        raise YAPI.YAPI_Exception(YAPI.IO_ERROR, "No key %s in JSON struct" % key)

    # noinspection PyMethodMayBeStatic
    def _json_get_array(self, json):
        json_str = YByte2String(json)
        arr = YJSONArray(json_str, 0, len(json_str))
        arr.parse()
        lis = []
        for i in range(0, arr.length()):
            o = arr.get(i)
            lis.append(o.toJSON())
        return lis

    # noinspection PyMethodMayBeStatic
    def _json_get_string(self, json):
        json_str = YByte2String(json)
        jstring = YJSONString(json_str, 0, len(json_str))
        jstring.parse()
        return jstring.getString()

    # noinspection PyMethodMayBeStatic
    def _get_json_path(self, json, path):
        errbuf = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        path_data = ctypes.create_string_buffer(YString2Byte(path))
        json_data = ctypes.create_string_buffer(YString2Byte(json))
        reply_c = POINTER(ctypes.c_ubyte)()
        res = YAPI._yapiJsonGetPath(path_data, json_data, len(json), ctypes.byref(reply_c), errbuf)
        if res > 0:
            bb = YString2Byte("")
            # (xrange not supported in 2.5.x)
            for i in range(res):
                bb = YAddByte(bb, reply_c[i])
            YAPI._yapiFreeMem(reply_c)
            return YByte2String(bb)
        return ""

    def _decode_json_string(self, json):
        if isinstance(json, str):
            json = YString2Byte(json)
        json_data = ctypes.create_string_buffer(json)
        buffer = ctypes.create_string_buffer(len(json))
        res = YAPI._yapiJsonDecodeString(json_data, buffer)
        return YByte2String(buffer.value)

    # Method used to cache DataStream objects (new DataLogger)
    def _findDataStream(self, dataset, definition):
        key = dataset.get_functionId() + ":" + definition
        if key in self._dataStreams:
            return self._dataStreams[key]
        words = YAPI._decodeWords(definition)
        if len(words) < 14:
            return self._throw(YAPI.VERSION_MISMATCH, "device firmware is too old")
        newDataStream = YDataStream(self, dataset, words)
        self._dataStreams[key] = newDataStream
        return newDataStream

    # Method used to clear cache of DataStream object (undocumented)
    def _clearDataStreamCache(self):
        self._dataStreams.clear()

    # --- (generated code: YFunction implementation)
    def _parseAttr(self, json_val):
        if json_val.has("logicalName"):
            self._logicalName = json_val.getString("logicalName")
        if json_val.has("advertisedValue"):
            self._advertisedValue = json_val.getString("advertisedValue")
        return 0

    def get_logicalName(self):
        """
        Returns the logical name of the function.

        @return a string corresponding to the logical name of the function

        On failure, throws an exception or returns YFunction.LOGICALNAME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YFunction.LOGICALNAME_INVALID
        res = self._logicalName
        return res

    def set_logicalName(self, newval):
        """
        Changes the logical name of the function. You can use yCheckLogicalName()
        prior to this call to make sure that your parameter is valid.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the logical name of the function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not YAPI.CheckLogicalName(newval):
            self._throw(YAPI.INVALID_ARGUMENT, "Invalid name :" + newval)
            return YAPI.INVALID_ARGUMENT
        rest_val = newval
        return self._setAttr("logicalName", rest_val)

    def get_advertisedValue(self):
        """
        Returns a short string representing the current state of the function.

        @return a string corresponding to a short string representing the current state of the function

        On failure, throws an exception or returns YFunction.ADVERTISEDVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YFunction.ADVERTISEDVALUE_INVALID
        res = self._advertisedValue
        return res

    def set_advertisedValue(self, newval):
        rest_val = newval
        return self._setAttr("advertisedValue", rest_val)

    @staticmethod
    def FindFunction(func):
        """
        Retrieves a function for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the function is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YFunction.isOnline() to test if the function is
        indeed online at a given time. In case of ambiguity when looking for
        a function by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the function, for instance
                MyDevice..

        @return a YFunction object allowing you to drive the function.
        """
        # obj
        obj = YFunction._FindFromCache("Function", func)
        if obj is None:
            obj = YFunction(func)
            YFunction._AddToCache("Function", func, obj)
        return obj

    def registerValueCallback(self, callback):
        """
        Registers the callback function that is invoked on every change of advertised value.
        The callback is invoked only during the execution of ySleep or yHandleEvents.
        This provides control over the time when the callback is triggered. For good responsiveness, remember to call
        one of these two functions periodically. To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to call, or a None pointer. The callback function should take two
                arguments: the function object of which the value has changed, and the character string describing
                the new advertised value.
        @noreturn
        """
        # val
        if callback is not None:
            YFunction._UpdateValueCallbackList(self, True)
        else:
            YFunction._UpdateValueCallbackList(self, False)
        self._valueCallbackFunction = callback
        # // Immediately invoke value callback with current value
        if callback is not None and self.isOnline():
            val = self._advertisedValue
            if not (val == ""):
                self._invokeValueCallback(val)
        return 0

    def _invokeValueCallback(self, value):
        if self._valueCallbackFunction is not None:
            self._valueCallbackFunction(self, value)
        return 0

    def muteValueCallbacks(self):
        """
        Disables the propagation of every new advertised value to the parent hub.
        You can use this function to save bandwidth and CPU on computers with limited
        resources, or to prevent unwanted invocations of the HTTP callback.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_advertisedValue("SILENT")

    def unmuteValueCallbacks(self):
        """
        Re-enables the propagation of every new advertised value to the parent hub.
        This function reverts the effect of a previous call to muteValueCallbacks().
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_advertisedValue("")

    def loadAttribute(self, attrName):
        """
        Returns the current value of a single function attribute, as a text string, as quickly as
        possible but without using the cached value.

        @param attrName : the name of the requested attribute

        @return a string with the value of the the attribute

        On failure, throws an exception or returns an empty string.
        """
        # url
        # attrVal
        url = "api/" + self.get_functionId() + "/" + attrName
        attrVal = self._download(url)
        return YByte2String(attrVal)

    def isReadOnly(self):
        """
        Test if the function is readOnly. Return true if the function is write protected
        or that the function is not available.

        @return true if the function is readOnly or not online.
        """
        # serial
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # res
        try:
            serial = self.get_serialNumber()
        except:
            return True
        res = YAPI._yapiIsModuleWritable(ctypes.create_string_buffer(YString2Byte(serial)), errmsg)
        if res > 0:
            return False
        return True

    def get_serialNumber(self):
        """
        Returns the serial number of the module, as set by the factory.

        @return a string corresponding to the serial number of the module, as set by the factory.

        On failure, throws an exception or returns YModule.SERIALNUMBER_INVALID.
        """
        # m
        m = self.get_module()
        return m.get_serialNumber()

    def _parserHelper(self):
        return 0

    def nextFunction(self):
        """
        comment from .yc definition
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YFunction.FindFunction(hwidRef.value)

#--- (end of generated code: YFunction implementation)

    def get_hardwareId(self):
        """
        Returns the unique hardware identifier of the function in the form SERIAL.FUNCTIONID.
        The unique hardware identifier is composed of the device serial
        number and of the hardware identifier of the function (for example RELAYLO1-123456.relay1).

        @return a string that uniquely identifies the function (ex: RELAYLO1-123456.relay1)

        On failure, throws an exception or returns  YFunction.HARDWAREID_INVALID.
        """
        errmsgRef = YRefParam()
        fundescRef = YRefParam()
        snum = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return self.HARDWAREID_INVALID
        devdesc = ctypes.c_int()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), snum, funcid, None, None, None,
                                          errbuff)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return self.HARDWAREID_INVALID
        return YByte2String(snum.value) + "." + YByte2String(funcid.value)

    def get_functionId(self):
        """
        Returns the hardware identifier of the function, without reference to the module. For example
        relay1

        @return a string that identifies the function (ex: relay1)

        On failure, throws an exception or returns  YFunction.FUNCTIONID_INVALID.
        """
        errmsgRef = YRefParam()
        fundescRef = YRefParam()
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return self.FUNCTIONID_INVALID
        devdesc = ctypes.c_int()
        # noinspection PyUnresolvedReferences
        res = YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), None, funcid, None, None, None,
                                          errbuff)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return self.FUNCTIONID_INVALID
        return YByte2String(funcid.value)

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    def get_friendlyName(self):
        """
        Returns a global identifier of the function in the format MODULE_NAME&#46;FUNCTION_NAME.
        The returned string uses the logical names of the module and of the function if they are defined,
        otherwise the serial number of the module and the hardware identifier of the function
        (for example: MyCustomName.relay1)

        @return a string that uniquely identifies the function using logical names
                (ex: MyCustomName.relay1)

        On failure, throws an exception or returns  YFunction.FRIENDLYNAME_INVALID.
        """
        errmsgRef = YRefParam()
        fundescRef = YRefParam()
        fname = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        snum = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        devdesc = ctypes.c_int()
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        if not YAPI.YISERR(res) and not YAPI.YISERR(
                YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), snum, funcid, None, fname, None,
                                            errbuff)):
            if YByte2String(fname.value) != "":
                funcid = fname
            dname = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
            moddescr = YAPI.yapiGetFunction("Module", YByte2String(snum.value), errmsgRef)
            if not YAPI.YISERR(moddescr) and not YAPI.YISERR(
                    YAPI._yapiGetFunctionInfoEx(moddescr, ctypes.byref(devdesc), None, None, None, dname, None,
                                                errbuff)):
                if YByte2String(dname.value) != "":
                    return "%s.%s" % (YByte2String(dname.value), YByte2String(funcid.value))
            return "%s.%s" % (YByte2String(snum.value), YByte2String(funcid.value))
        self._throw(YAPI.DEVICE_NOT_FOUND, errmsgRef.value)
        return self.FRIENDLYNAME_INVALID

    def describe(self):
        """
        Returns a short text that describes unambiguously the instance of the function in the form
        TYPE(NAME)=SERIAL&#46;FUNCTIONID.
        More precisely,
        TYPE       is the type of the function,
        NAME       it the name used for the first access to the function,
        SERIAL     is the serial number of the module if the module is connected or "unresolved", and
        FUNCTIONID is  the hardware identifier of the function if the module is connected.
        For example, this method returns Relay(MyCustomName.relay1)=RELAYLO1-123456.relay1 if the
        module is already connected or Relay(BadCustomeName.relay1)=unresolved if the module has
        not yet been connected. This method does not trigger any USB or TCP transaction and can therefore be used in
        a debugger.

        @return a string that describes the function
                (ex: Relay(MyCustomName.relay1)=RELAYLO1-123456.relay1)
        """
        errmsgRef = YRefParam()
        fundescRef = YRefParam()
        snum = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        devdesc = ctypes.c_int()
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        # noinspection PyUnresolvedReferences
        if not YAPI.YISERR(res) and not YAPI.YISERR(
                YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), snum, funcid, None, None, None,
                                            errbuff)):
            return self._className + "(" + self._func + ")=" + YByte2String(snum.value) + "." + YByte2String(
                funcid.value)
        return self._className + "(" + self._func + ")=unresolved"

    def __str__(self):
        return self.describe()

    def get_errorType(self):
        """
        Returns the numerical error code of the latest error with the function.
        This method is mostly useful when using the Yoctopuce library with
        exceptions disabled.

        @return a number corresponding to the code of the latest error that occurred while
                using the function object
        """
        return self._lastErrorType

    def errorType(self):
        return self._lastErrorType

    def errType(self):
        return self._lastErrorType

    def get_errorMessage(self):
        """
        Returns the error message of the latest error with the function.
        This method is mostly useful when using the Yoctopuce library with
        exceptions disabled.

        @return a string corresponding to the latest error message that occured while
                using the function object
        """
        return self._lastErrorMsg

    def errorMessage(self):
        return self._lastErrorMsg

    def errMessage(self):
        return self._lastErrorMsg

    def isOnline(self):
        """
        Checks if the function is currently reachable, without raising any error.
        If there is a cached value for the function in cache, that has not yet
        expired, the device is considered reachable.
        No exception is raised if there is an error while trying to contact the
        device hosting the function.

        @return true if the function can be reached, and false otherwise
        """

        devRef = YRefParam()
        errmsgRef = YRefParam()
        apiresRef = YRefParam()

        #  A valid value in cache means that the device is online
        if self._cacheExpiration > YAPI.GetTickCount():
            return True

        # Check that the function is available, without throwing exceptions
        if YAPI.YISERR(self._getDevice(devRef, errmsgRef)):
            return False
        try:
            # Try to execute a function request to be positively sure that the device is ready
            if YAPI.YISERR(devRef.value.requestAPI(apiresRef, errmsgRef)):
                return False
            self.load(YAPI.DefaultCacheValidity)
        except YAPI_Exception:
            return False
        return True

    def load(self, msValidity):
        """
        Preloads the function cache with a specified validity duration.
        By default, whenever accessing a device, all function attributes
        are kept in cache for the standard duration (5 ms). This method can be
        used to temporarily mark the cache as valid for a longer period, in order
        to reduce network traffic for instance.

        @param msValidity : an integer corresponding to the validity attributed to the
                loaded function parameters, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        devRef = YRefParam()
        errmsgRef = YRefParam()
        apiresRef = YRefParam()
        funcIdRef = YRefParam()
        devdescRef = YRefParam()
        serialRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()

        # Resolve our reference to our device, load REST API
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        res = devRef.value.requestAPI(apiresRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        # Get our function Id
        fundescr = YAPI.yapiGetFunction(self._className, self._func, errmsgRef)
        if YAPI.YISERR(fundescr):
            self._throw(res, errmsgRef.value)
            return fundescr

        res = YAPI.yapiGetFunctionInfo(fundescr, devdescRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res
        if type(msValidity) == type(int()):
            msValidity = datetime.timedelta(milliseconds=msValidity)
        self._cacheExpiration = YAPI.GetTickCount() + msValidity
        self._serial = str(serialRef.value)
        self._funId = str(funcIdRef.value)
        self._hwId = self._serial + '.' + self._funId

        node = apiresRef.value.getYJSONObject(self._funId)
        if node is None:
            self._throw(YAPI.IO_ERROR, "unexpected JSON structure: missing function " + self._funId)
            return YAPI.IO_ERROR

        self._parse(node)
        return YAPI.SUCCESS

    def clearCache(self):
        """
        Invalidates the cache. Invalidates the cache of the function attributes. Forces the
        next call to get_xxx() or loadxxx() to use values that come from the device.

        @noreturn
        """
        devRef = YRefParam()
        errmsgRef = YRefParam()
        apiresRef = YRefParam()
        funcIdRef = YRefParam()
        devdescRef = YRefParam()
        serialRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()

        # Resolve our reference to our device, load REST API
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            return
        devRef.value.clearCache()
        self._cacheExpiration = YAPI.GetTickCount()

    def get_module(self):
        """
        Gets the YModule object for the device on which the function is located.
        If the function cannot be located on any module, the returned instance of
        YModule is not shown as on-line.

        @return an instance of YModule
        """
        devdescrRef = YRefParam()
        errmsgRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValueRef = YRefParam()

        fundescr = YAPI.yapiGetFunction(self._className, self._func, errmsgRef)
        if not YAPI.YISERR(fundescr):
            if not YAPI.YISERR(
                    YAPI.yapiGetFunctionInfo(fundescr, devdescrRef, serialRef, funcIdRef, funcNameRef, funcValueRef,
                                             errmsgRef)):
                return YModule.FindModule(serialRef.value + ".module")

        # return a true YModule object even if it is not a module valid for communicating
        return YModule.FindModule("module_of_" + self._className + "_" + self._func)

    def module(self):
        return self.get_module()

    def get_functionDescriptor(self):
        """
        Returns a unique identifier of type YFUN_DESCR corresponding to the function.
        This identifier can be used to test if two instances of YFunction reference the same
        physical function on the same physical device.

        @return an identifier of type YFUN_DESCR.

        If the function has never been contacted, the returned value is YFunction.FUNCTIONDESCRIPTOR_INVALID.
        """
        return self._fundescr

    def functionDescriptor(self):
        return self.get_functionDescriptor()

    def get_userData(self):
        """
        Returns the value of the userData attribute, as previously stored using method
        set_userData.
        This attribute is never touched directly by the API, and is at disposal of the caller to
        store a context.

        @return the object stored previously by the caller.
        """
        return self._userData

    def userData(self):
        return self.get_userData()

    def set_userData(self, data):
        """
        Stores a user context provided as argument in the userData attribute of the function.
        This attribute is never touched by the API, and is at disposal of the caller to store a context.

        @param data : any kind of object to be stored
        @noreturn
        """
        self._userData = data

    def setUserData(self, data):
        self.set_userData(data)

    # --- (generated code: YFunction functions)

    @staticmethod
    def FirstFunction():
        """
        comment from .yc definition
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
        err = YAPI.apiGetFunctionsByClass("Function", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YFunction.FindFunction(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YFunction functions)


# --- (generated code: YModule class start)
#noinspection PyProtectedMember
class YModule(YFunction):
    """
    The YModule class can be used with all Yoctopuce USB devices.
    It can be used to control the module global parameters, and
    to enumerate the functions provided by each module.

    """
    #--- (end of generated code: YModule class start)

    _moduleCallbackList = {}

    # --- (generated code: YModule definitions)
    PRODUCTNAME_INVALID = YAPI.INVALID_STRING
    SERIALNUMBER_INVALID = YAPI.INVALID_STRING
    PRODUCTID_INVALID = YAPI.INVALID_UINT
    PRODUCTRELEASE_INVALID = YAPI.INVALID_UINT
    FIRMWARERELEASE_INVALID = YAPI.INVALID_STRING
    LUMINOSITY_INVALID = YAPI.INVALID_UINT
    UPTIME_INVALID = YAPI.INVALID_LONG
    USBCURRENT_INVALID = YAPI.INVALID_UINT
    REBOOTCOUNTDOWN_INVALID = YAPI.INVALID_INT
    USERVAR_INVALID = YAPI.INVALID_INT
    PERSISTENTSETTINGS_LOADED = 0
    PERSISTENTSETTINGS_SAVED = 1
    PERSISTENTSETTINGS_MODIFIED = 2
    PERSISTENTSETTINGS_INVALID = -1
    BEACON_OFF = 0
    BEACON_ON = 1
    BEACON_INVALID = -1
    #--- (end of generated code: YModule definitions)

    def __init__(self, func):
        super(YModule, self).__init__(func)
        self._className = "Module"
        # --- (generated code: YModule attributes)
        self._callback = None
        self._productName = YModule.PRODUCTNAME_INVALID
        self._serialNumber = YModule.SERIALNUMBER_INVALID
        self._productId = YModule.PRODUCTID_INVALID
        self._productRelease = YModule.PRODUCTRELEASE_INVALID
        self._firmwareRelease = YModule.FIRMWARERELEASE_INVALID
        self._persistentSettings = YModule.PERSISTENTSETTINGS_INVALID
        self._luminosity = YModule.LUMINOSITY_INVALID
        self._beacon = YModule.BEACON_INVALID
        self._upTime = YModule.UPTIME_INVALID
        self._usbCurrent = YModule.USBCURRENT_INVALID
        self._rebootCountdown = YModule.REBOOTCOUNTDOWN_INVALID
        self._userVar = YModule.USERVAR_INVALID
        self._logCallback = None
        self._confChangeCallback = None
        self._beaconCallback = None
        #--- (end of generated code: YModule attributes)

    @staticmethod
    def _updateModuleCallbackList(modul, add):
        if add:
            modul.isOnline()
            if modul not in YModule._moduleCallbackList:
                YModule._moduleCallbackList[modul] = 1
            else:
                YModule._moduleCallbackList[modul] += 1
        else:
            if modul in YModule._moduleCallbackList and YModule._moduleCallbackList[modul] > 1:
                YModule._moduleCallbackList[modul] -= 1

    # --- (generated code: YModule implementation)
    def _parseAttr(self, json_val):
        if json_val.has("productName"):
            self._productName = json_val.getString("productName")
        if json_val.has("serialNumber"):
            self._serialNumber = json_val.getString("serialNumber")
        if json_val.has("productId"):
            self._productId = json_val.getInt("productId")
        if json_val.has("productRelease"):
            self._productRelease = json_val.getInt("productRelease")
        if json_val.has("firmwareRelease"):
            self._firmwareRelease = json_val.getString("firmwareRelease")
        if json_val.has("persistentSettings"):
            self._persistentSettings = json_val.getInt("persistentSettings")
        if json_val.has("luminosity"):
            self._luminosity = json_val.getInt("luminosity")
        if json_val.has("beacon"):
            self._beacon = (json_val.getInt("beacon") > 0 if 1 else 0)
        if json_val.has("upTime"):
            self._upTime = json_val.getLong("upTime")
        if json_val.has("usbCurrent"):
            self._usbCurrent = json_val.getInt("usbCurrent")
        if json_val.has("rebootCountdown"):
            self._rebootCountdown = json_val.getInt("rebootCountdown")
        if json_val.has("userVar"):
            self._userVar = json_val.getInt("userVar")
        super(YModule, self)._parseAttr(json_val)

    def get_productName(self):
        """
        Returns the commercial name of the module, as set by the factory.

        @return a string corresponding to the commercial name of the module, as set by the factory

        On failure, throws an exception or returns YModule.PRODUCTNAME_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.PRODUCTNAME_INVALID
        res = self._productName
        return res

    def get_serialNumber(self):
        """
        Returns the serial number of the module, as set by the factory.

        @return a string corresponding to the serial number of the module, as set by the factory

        On failure, throws an exception or returns YModule.SERIALNUMBER_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.SERIALNUMBER_INVALID
        res = self._serialNumber
        return res

    def get_productId(self):
        """
        Returns the USB device identifier of the module.

        @return an integer corresponding to the USB device identifier of the module

        On failure, throws an exception or returns YModule.PRODUCTID_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.PRODUCTID_INVALID
        res = self._productId
        return res

    def get_productRelease(self):
        """
        Returns the release number of the module hardware, preprogrammed at the factory.
        The original hardware release returns value 1, revision B returns value 2, etc.

        @return an integer corresponding to the release number of the module hardware, preprogrammed at the factory

        On failure, throws an exception or returns YModule.PRODUCTRELEASE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.PRODUCTRELEASE_INVALID
        res = self._productRelease
        return res

    def get_firmwareRelease(self):
        """
        Returns the version of the firmware embedded in the module.

        @return a string corresponding to the version of the firmware embedded in the module

        On failure, throws an exception or returns YModule.FIRMWARERELEASE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.FIRMWARERELEASE_INVALID
        res = self._firmwareRelease
        return res

    def get_persistentSettings(self):
        """
        Returns the current state of persistent module settings.

        @return a value among YModule.PERSISTENTSETTINGS_LOADED, YModule.PERSISTENTSETTINGS_SAVED and
        YModule.PERSISTENTSETTINGS_MODIFIED corresponding to the current state of persistent module settings

        On failure, throws an exception or returns YModule.PERSISTENTSETTINGS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.PERSISTENTSETTINGS_INVALID
        res = self._persistentSettings
        return res

    def set_persistentSettings(self, newval):
        rest_val = str(newval)
        return self._setAttr("persistentSettings", rest_val)

    def get_luminosity(self):
        """
        Returns the luminosity of the  module informative LEDs (from 0 to 100).

        @return an integer corresponding to the luminosity of the  module informative LEDs (from 0 to 100)

        On failure, throws an exception or returns YModule.LUMINOSITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.LUMINOSITY_INVALID
        res = self._luminosity
        return res

    def set_luminosity(self, newval):
        """
        Changes the luminosity of the module informative leds. The parameter is a
        value between 0 and 100.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the luminosity of the module informative leds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("luminosity", rest_val)

    def get_beacon(self):
        """
        Returns the state of the localization beacon.

        @return either YModule.BEACON_OFF or YModule.BEACON_ON, according to the state of the localization beacon

        On failure, throws an exception or returns YModule.BEACON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.BEACON_INVALID
        res = self._beacon
        return res

    def set_beacon(self, newval):
        """
        Turns on or off the module localization beacon.

        @param newval : either YModule.BEACON_OFF or YModule.BEACON_ON

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("beacon", rest_val)

    def get_upTime(self):
        """
        Returns the number of milliseconds spent since the module was powered on.

        @return an integer corresponding to the number of milliseconds spent since the module was powered on

        On failure, throws an exception or returns YModule.UPTIME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.UPTIME_INVALID
        res = self._upTime
        return res

    def get_usbCurrent(self):
        """
        Returns the current consumed by the module on the USB bus, in milli-amps.

        @return an integer corresponding to the current consumed by the module on the USB bus, in milli-amps

        On failure, throws an exception or returns YModule.USBCURRENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.USBCURRENT_INVALID
        res = self._usbCurrent
        return res

    def get_rebootCountdown(self):
        """
        Returns the remaining number of seconds before the module restarts, or zero when no
        reboot has been scheduled.

        @return an integer corresponding to the remaining number of seconds before the module restarts, or zero when no
                reboot has been scheduled

        On failure, throws an exception or returns YModule.REBOOTCOUNTDOWN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.REBOOTCOUNTDOWN_INVALID
        res = self._rebootCountdown
        return res

    def set_rebootCountdown(self, newval):
        rest_val = str(newval)
        return self._setAttr("rebootCountdown", rest_val)

    def get_userVar(self):
        """
        Returns the value previously stored in this attribute.
        On startup and after a device reboot, the value is always reset to zero.

        @return an integer corresponding to the value previously stored in this attribute

        On failure, throws an exception or returns YModule.USERVAR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YModule.USERVAR_INVALID
        res = self._userVar
        return res

    def set_userVar(self, newval):
        """
        Stores a 32 bit value in the device RAM. This attribute is at programmer disposal,
        should he need to store a state variable.
        On startup and after a device reboot, the value is always reset to zero.

        @param newval : an integer

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("userVar", rest_val)

    @staticmethod
    def FindModule(func):
        """
        Allows you to find a module from its serial number or from its logical name.

        This function does not require that the module is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YModule.isOnline() to test if the module is
        indeed online at a given time. In case of ambiguity when looking for
        a module by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.


        If a call to this object's is_online() method returns FALSE although
        you are certain that the device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string containing either the serial number or
                the logical name of the desired module

        @return a YModule object allowing you to drive the module
                or get additional information on the module.
        """
        # obj
        # cleanHwId
        # modpos
        cleanHwId = func
        modpos = func.find(".module")
        if modpos != (len(func) - 7):
            cleanHwId = func + ".module"
        obj = YFunction._FindFromCache("Module", cleanHwId)
        if obj is None:
            obj = YModule(cleanHwId)
            YFunction._AddToCache("Module", cleanHwId, obj)
        return obj

    def get_productNameAndRevision(self):
        # prodname
        # prodrel
        # fullname

        prodname = self.get_productName()
        prodrel = self.get_productRelease()
        if prodrel > 1:
            fullname = "" + prodname + " rev. " + str(chr(64+prodrel))
        else:
            fullname = prodname
        return fullname

    def saveToFlash(self):
        """
        Saves current settings in the nonvolatile memory of the module.
        Warning: the number of allowed save operations during a module life is
        limited (about 100000 cycles). Do not call this function within a loop.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_persistentSettings(YModule.PERSISTENTSETTINGS_SAVED)

    def revertFromFlash(self):
        """
        Reloads the settings stored in the nonvolatile memory, as
        when the module is powered on.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_persistentSettings(YModule.PERSISTENTSETTINGS_LOADED)

    def reboot(self, secBeforeReboot):
        """
        Schedules a simple module reboot after the given number of seconds.

        @param secBeforeReboot : number of seconds before rebooting

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_rebootCountdown(secBeforeReboot)

    def triggerFirmwareUpdate(self, secBeforeReboot):
        """
        Schedules a module reboot into special firmware update mode.

        @param secBeforeReboot : number of seconds before rebooting

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_rebootCountdown(-secBeforeReboot)

    def _startStopDevLog(self, serial, start):
        # i_start
        if start:
            i_start = 1
        else:
            i_start = 0

        YAPI._yapiStartStopDeviceLogCallback(ctypes.create_string_buffer(YString2Byte(serial)), i_start)

    def registerLogCallback(self, callback):
        """
        Registers a device log callback function. This callback will be called each time
        that a module sends a new log message. Mostly useful to debug a Yoctopuce module.

        @param callback : the callback function to call, or a None pointer. The callback function should take two
                arguments: the module object that emitted the log message, and the character string containing the log.
                On failure, throws an exception or returns a negative error code.
        """
        # serial

        serial = self.get_serialNumber()
        if serial == YAPI.INVALID_STRING:
            return YAPI.DEVICE_NOT_FOUND
        self._logCallback = callback
        self._startStopDevLog(serial, callback is not None)
        return 0

    def get_logCallback(self):
        return self._logCallback

    def registerConfigChangeCallback(self, callback):
        """
        Register a callback function, to be called when a persistent settings in
        a device configuration has been changed (e.g. change of unit, etc).

        @param callback : a procedure taking a YModule parameter, or None
                to unregister a previously registered  callback.
        """
        if callback is not None:
            YModule._updateModuleCallbackList(self, True)
        else:
            YModule._updateModuleCallbackList(self, False)
        self._confChangeCallback = callback
        return 0

    def _invokeConfigChangeCallback(self):
        if self._confChangeCallback is not None:
            self._confChangeCallback(self)
        return 0

    def registerBeaconCallback(self, callback):
        """
        Register a callback function, to be called when the localization beacon of the module
        has been changed. The callback function should take two arguments: the YModule object of
        which the beacon has changed, and an integer describing the new beacon state.

        @param callback : The callback function to call, or None to unregister a
                previously registered callback.
        """
        if callback is not None:
            YModule._updateModuleCallbackList(self, True)
        else:
            YModule._updateModuleCallbackList(self, False)
        self._beaconCallback = callback
        return 0

    def _invokeBeaconCallback(self, beaconState):
        if self._beaconCallback is not None:
            self._beaconCallback(self, beaconState)
        return 0

    def triggerConfigChangeCallback(self):
        """
        Triggers a configuration change callback, to check if they are supported or not.
        """
        self._setAttr("persistentSettings", "2")
        return 0

    def checkFirmware(self, path, onlynew):
        """
        Tests whether the byn file is valid for this module. This method is useful to test if the module
        needs to be updated.
        It is possible to pass a directory as argument instead of a file. In this case, this method returns
        the path of the most recent
        appropriate .byn file. If the parameter onlynew is true, the function discards firmwares that are older or
        equal to the installed firmware.

        @param path : the path of a byn file or a directory that contains byn files
        @param onlynew : returns only files that are strictly newer

        @return the path of the byn file to use or a empty string if no byn files matches the requirement

        On failure, throws an exception or returns a string that start with "error:".
        """
        # serial
        # release
        # tmp_res
        if onlynew:
            release = YAPI._atoi(self.get_firmwareRelease())
        else:
            release = 0
        # //may throw an exception
        serial = self.get_serialNumber()
        tmp_res = YFirmwareUpdate.CheckFirmware(serial, path, release)
        if tmp_res.find("error:") == 0:
            self._throw(YAPI.INVALID_ARGUMENT, tmp_res)
        return tmp_res

    def updateFirmwareEx(self, path, force):
        """
        Prepares a firmware update of the module. This method returns a YFirmwareUpdate object which
        handles the firmware update process.

        @param path : the path of the .byn file to use.
        @param force : true to force the firmware update even if some prerequisites appear not to be met

        @return a YFirmwareUpdate object or None on error.
        """
        # serial
        # settings

        serial = self.get_serialNumber()
        settings = self.get_allSettings()
        if len(settings) == 0:
            self._throw(YAPI.IO_ERROR, "Unable to get device settings")
            settings = YString2Byte("error:Unable to get device settings")
        return YFirmwareUpdate(serial, path, settings, force)

    def updateFirmware(self, path):
        """
        Prepares a firmware update of the module. This method returns a YFirmwareUpdate object which
        handles the firmware update process.

        @param path : the path of the .byn file to use.

        @return a YFirmwareUpdate object or None on error.
        """
        return self.updateFirmwareEx(path, False)

    def get_allSettings(self):
        """
        Returns all the settings and uploaded files of the module. Useful to backup all the
        logical names, calibrations parameters, and uploaded files of a device.

        @return a binary buffer with all the settings.

        On failure, throws an exception or returns an binary object of size 0.
        """
        # settings
        # json
        # res
        # sep
        # name
        # item
        # t_type
        # id
        # url
        # file_data
        # file_data_bin
        # temp_data_bin
        # ext_settings
        filelist = []
        templist = []

        settings = self._download("api.json")
        if len(settings) == 0:
            return settings
        ext_settings = ", \"extras\":["
        templist = self.get_functionIds("Temperature")
        sep = ""
        for y in templist:
            if YAPI._atoi(self.get_firmwareRelease()) > 9000:
                url = "api/" + y + "/sensorType"
                t_type = YByte2String(self._download(url))
                if t_type == "RES_NTC" or t_type == "RES_LINEAR":
                    id = (y)[11: 11 + len(y) - 11]
                    if id == "":
                        id = "1"
                    temp_data_bin = self._download("extra.json?page=" + id)
                    if len(temp_data_bin) > 0:
                        item = "" + sep + "{\"fid\":\"" + y + "\", \"json\":" + YByte2String(temp_data_bin) + "}\n"
                        ext_settings = ext_settings + item
                        sep = ","
        ext_settings = ext_settings + "],\n\"files\":["
        if self.hasFunction("files"):
            json = self._download("files.json?a=dir&f=")
            if len(json) == 0:
                return json
            filelist = self._json_get_array(json)
            sep = ""
            for y in filelist:
                name = self._json_get_key(YString2Byte(y), "name")
                if (len(name) > 0) and not (name == "startupConf.json"):
                    file_data_bin = self._download(self._escapeAttr(name))
                    file_data = YAPI._bytesToHexStr(file_data_bin)
                    item = "" + sep + "{\"name\":\"" + name + "\", \"data\":\"" + file_data + "\"}\n"
                    ext_settings = ext_settings + item
                    sep = ","
        res = YString2Byte("{ \"api\":" + YByte2String(settings) + ext_settings + "]}")
        return res

    def loadThermistorExtra(self, funcId, jsonExtra):
        values = []
        # url
        # curr
        # currTemp
        # ofs
        # size
        url = "api/" + funcId + ".json?command=Z"

        self._download(url)
        # // add records in growing resistance value
        values = self._json_get_array(YString2Byte(jsonExtra))
        ofs = 0
        size = len(values)
        while ofs + 1 < size:
            curr = values[ofs]
            currTemp = values[ofs + 1]
            url = "api/" + funcId + ".json?command=m" + curr + ":" + currTemp
            self._download(url)
            ofs = ofs + 2
        return YAPI.SUCCESS

    def set_extraSettings(self, jsonExtra):
        extras = []
        # functionId
        # data
        extras = self._json_get_array(YString2Byte(jsonExtra))
        for y in extras:
            functionId = self._get_json_path(y, "fid")
            functionId = self._decode_json_string(functionId)
            data = self._get_json_path(y, "json")
            if self.hasFunction(functionId):
                self.loadThermistorExtra(functionId, data)
        return YAPI.SUCCESS

    def set_allSettingsAndFiles(self, settings):
        """
        Restores all the settings and uploaded files to the module.
        This method is useful to restore all the logical names and calibrations parameters,
        uploaded files etc. of a device from a backup.
        Remember to call the saveToFlash() method of the module if the
        modifications must be kept.

        @param settings : a binary buffer with all the settings.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # down
        # json
        # json_api
        # json_files
        # json_extra
        json = YByte2String(settings)
        json_api = self._get_json_path(json, "api")
        if json_api == "":
            return self.set_allSettings(settings)
        json_extra = self._get_json_path(json, "extras")
        if not (json_extra == ""):
            self.set_extraSettings(json_extra)
        self.set_allSettings(YString2Byte(json_api))
        if self.hasFunction("files"):
            files = []
            # res
            # name
            # data
            down = self._download("files.json?a=format")
            res = self._get_json_path(YByte2String(down), "res")
            res = self._decode_json_string(res)
            if not (res == "ok"):
                self._throw(YAPI.IO_ERROR, "format failed")
                return YAPI.IO_ERROR
            json_files = self._get_json_path(json, "files")
            files = self._json_get_array(YString2Byte(json_files))
            for y in files:
                name = self._get_json_path(y, "name")
                name = self._decode_json_string(name)
                data = self._get_json_path(y, "data")
                data = self._decode_json_string(data)
                self._upload(name, YAPI._hexStrToBin(data))
        # // Apply settings a second time for file-dependent settings and dynamic sensor nodes
        return self.set_allSettings(YString2Byte(json_api))

    def hasFunction(self, funcId):
        """
        Tests if the device includes a specific function. This method takes a function identifier
        and returns a boolean.

        @param funcId : the requested function identifier

        @return true if the device has the function identifier
        """
        # count
        # i
        # fid

        count = self.functionCount()
        i = 0
        while i < count:
            fid = self.functionId(i)
            if fid == funcId:
                return True
            i = i + 1
        return False

    def get_functionIds(self, funType):
        """
        Retrieve all hardware identifier that match the type passed in argument.

        @param funType : The type of function (Relay, LightSensor, Voltage,...)

        @return an array of strings.
        """
        # count
        # i
        # ftype
        res = []

        count = self.functionCount()
        i = 0

        while i < count:
            ftype = self.functionType(i)
            if ftype == funType:
                res.append(self.functionId(i))
            else:
                ftype = self.functionBaseType(i)
                if ftype == funType:
                    res.append(self.functionId(i))
            i = i + 1

        return res

    def _flattenJsonStruct(self, jsoncomplex):
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        smallbuff = ctypes.create_string_buffer(1024)
        # bigbuff
        # buffsize
        fullsize = ctypes.c_int()
        # res
        # jsonflat
        # jsoncomplexstr
        fullsize.value = 0
        jsoncomplexstr = YByte2String(jsoncomplex)
        res = YAPI._yapiGetAllJsonKeys(ctypes.create_string_buffer(YString2Byte(jsoncomplexstr)), smallbuff, 1024, ctypes.byref(fullsize), errmsg)
        if res < 0:
            self._throw(YAPI.INVALID_ARGUMENT, YByte2String(errmsg.value))
            jsonflat = "error:" + YByte2String(errmsg.value)
            return YString2Byte(jsonflat)
        if fullsize.value <= 1024:
            jsonflat = YByte2String(smallbuff.value)
        else:
            fullsize.value = fullsize.value * 2
            buffsize = fullsize.value
            bigbuff = ctypes.create_string_buffer(buffsize)
            res = YAPI._yapiGetAllJsonKeys(ctypes.create_string_buffer(YString2Byte(jsoncomplexstr)), bigbuff, buffsize, ctypes.byref(fullsize), errmsg)
            if res < 0:
                self._throw(YAPI.INVALID_ARGUMENT, YByte2String(errmsg.value))
                jsonflat = "error:" + YByte2String(errmsg.value)
            else:
                jsonflat = YByte2String(bigbuff.value)
            bigbuff = None
        return YString2Byte(jsonflat)

    def calibVersion(self, cparams):
        if cparams == "0,":
            return 3
        if cparams.find(",") >= 0:
            if cparams.find(" ") > 0:
                return 3
            else:
                return 1
        if cparams == "" or cparams == "0":
            return 1
        if (len(cparams) < 2) or (cparams.find(".") >= 0):
            return 0
        else:
            return 2

    def calibScale(self, unit_name, sensorType):
        if unit_name == "g" or unit_name == "gauss" or unit_name == "W":
            return 1000
        if unit_name == "C":
            if sensorType == "":
                return 16
            if YAPI._atoi(sensorType) < 8:
                return 16
            else:
                return 100
        if unit_name == "m" or unit_name == "deg":
            return 10
        return 1

    def calibOffset(self, unit_name):
        if unit_name == "% RH" or unit_name == "mbar" or unit_name == "lx":
            return 0
        return 32767

    def calibConvert(self, param, currentFuncValue, unit_name, sensorType):
        # paramVer
        # funVer
        # funScale
        # funOffset
        # paramScale
        # paramOffset
        words = []
        words_str = []
        calibData = []
        iCalib = []
        # calibType
        # i
        # maxSize
        # ratio
        # nPoints
        # wordVal
        # // Initial guess for parameter encoding
        paramVer = self.calibVersion(param)
        funVer = self.calibVersion(currentFuncValue)
        funScale = self.calibScale(unit_name, sensorType)
        funOffset = self.calibOffset(unit_name)
        paramScale = funScale
        paramOffset = funOffset
        if funVer < 3:
            # // Read the effective device scale if available
            if funVer == 2:
                words = YAPI._decodeWords(currentFuncValue)
                if (words[0] == 1366) and (words[1] == 12500):
                    # // Yocto-3D RefFrame used a special encoding
                    funScale = 1
                    funOffset = 0
                else:
                    funScale = words[1]
                    funOffset = words[0]
            else:
                if funVer == 1:
                    if currentFuncValue == "" or (YAPI._atoi(currentFuncValue) > 10):
                        funScale = 0
        del calibData[:]
        calibType = 0
        if paramVer < 3:
            # // Handle old 16 bit parameters formats
            if paramVer == 2:
                words = YAPI._decodeWords(param)
                if (words[0] == 1366) and (words[1] == 12500):
                    # // Yocto-3D RefFrame used a special encoding
                    paramScale = 1
                    paramOffset = 0
                else:
                    paramScale = words[1]
                    paramOffset = words[0]
                if (len(words) >= 3) and (words[2] > 0):
                    maxSize = 3 + 2 * ((words[2]) % (10))
                    if maxSize > len(words):
                        maxSize = len(words)
                    i = 3
                    while i < maxSize:
                        calibData.append(int(words[i]))
                        i = i + 1
            else:
                if paramVer == 1:
                    words_str = (param).split(',')
                    for y in words_str:
                        words.append(YAPI._atoi(y))
                    if param == "" or (words[0] > 10):
                        paramScale = 0
                    if (len(words) > 0) and (words[0] > 0):
                        maxSize = 1 + 2 * ((words[0]) % (10))
                        if maxSize > len(words):
                            maxSize = len(words)
                        i = 1
                        while i < maxSize:
                            calibData.append(int(words[i]))
                            i = i + 1
                else:
                    if paramVer == 0:
                        ratio = float(param)
                        if ratio > 0:
                            calibData.append(0.0)
                            calibData.append(0.0)
                            calibData.append(round(65535 / ratio))
                            calibData.append(65535.0)
            i = 0
            while i < len(calibData):
                if paramScale > 0:
                    # // scalar decoding
                    calibData[i] = (calibData[i] - paramOffset) / paramScale
                else:
                    # // floating-point decoding
                    calibData[i] = YAPI._decimalToDouble(int(round(calibData[i])))
                i = i + 1
        else:
            # // Handle latest 32bit parameter format
            iCalib = YAPI._decodeFloats(param)
            calibType = int(round(iCalib[0] / 1000.0))
            if calibType >= 30:
                calibType = calibType - 30
            i = 1
            while i < len(iCalib):
                calibData.append(iCalib[i] / 1000.0)
                i = i + 1
        if funVer >= 3:
            # // Encode parameters in new format
            if len(calibData) == 0:
                param = "0,"
            else:
                param = str(30 + calibType)
                i = 0
                while i < len(calibData):
                    if ((i) & (1)) > 0:
                        param = param + ":"
                    else:
                        param = param + " "
                    param = param + str(int(round(calibData[i] * 1000.0 / 1000.0)))
                    i = i + 1
                param = param + ","
        else:
            if funVer >= 1:
                # // Encode parameters for older devices
                nPoints = int((len(calibData)) / (2))
                param = str(nPoints)
                i = 0
                while i < 2 * nPoints:
                    if funScale == 0:
                        wordVal = YAPI._doubleToDecimal(int(round(calibData[i])))
                    else:
                        wordVal = calibData[i] * funScale + funOffset
                    param = param + "," + str(round(wordVal))
                    i = i + 1
            else:
                # // Initial V0 encoding used for old Yocto-Light
                if len(calibData) == 4:
                    param = str(round(1000 * (calibData[3] - calibData[1]) / calibData[2] - calibData[0]))
        return param

    def _tryExec(self, url):
        # res
        # done
        res = YAPI.SUCCESS
        done = 1
        try:
            self._download(url)
        except:
            done = 0
        if done == 0:
            # // retry silently after a short wait
            try:
                YAPI.Sleep(500)
                self._download(url)
            except:
                # // second failure, return error code
                res = self.get_errorType()
        return res

    def set_allSettings(self, settings):
        """
        Restores all the settings of the device. Useful to restore all the logical names and calibrations parameters
        of a module from a backup.Remember to call the saveToFlash() method of the module if the
        modifications must be kept.

        @param settings : a binary buffer with all the settings.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        restoreLast = []
        # old_json_flat
        old_dslist = []
        old_jpath = []
        old_jpath_len = []
        old_val_arr = []
        # actualSettings
        new_dslist = []
        new_jpath = []
        new_jpath_len = []
        new_val_arr = []
        # cpos
        # eqpos
        # leng
        # i
        # j
        # subres
        # res
        # njpath
        # jpath
        # fun
        # attr
        # value
        # url
        # tmp
        # new_calib
        # sensorType
        # unit_name
        # newval
        # oldval
        # old_calib
        # each_str
        # do_update
        # found
        res = YAPI.SUCCESS
        tmp = YByte2String(settings)
        tmp = self._get_json_path(tmp, "api")
        if not (tmp == ""):
            settings = YString2Byte(tmp)
        oldval = ""
        newval = ""
        old_json_flat = self._flattenJsonStruct(settings)
        old_dslist = self._json_get_array(old_json_flat)



        for y in old_dslist:
            each_str = self._json_get_string(YString2Byte(y))
            # // split json path and attr
            leng = len(each_str)
            eqpos = each_str.find("=")
            if (eqpos < 0) or (leng == 0):
                self._throw(YAPI.INVALID_ARGUMENT, "Invalid settings")
                return YAPI.INVALID_ARGUMENT
            jpath = (each_str)[0: 0 + eqpos]
            eqpos = eqpos + 1
            value = (each_str)[eqpos: eqpos + leng - eqpos]
            old_jpath.append(jpath)
            old_jpath_len.append(len(jpath))
            old_val_arr.append(value)




        try:
            actualSettings = self._download("api.json")
        except:
            # // retry silently after a short wait
            YAPI.Sleep(500)
            actualSettings = self._download("api.json")
        actualSettings = self._flattenJsonStruct(actualSettings)
        new_dslist = self._json_get_array(actualSettings)



        for y in new_dslist:
            # // remove quotes
            each_str = self._json_get_string(YString2Byte(y))
            # // split json path and attr
            leng = len(each_str)
            eqpos = each_str.find("=")
            if (eqpos < 0) or (leng == 0):
                self._throw(YAPI.INVALID_ARGUMENT, "Invalid settings")
                return YAPI.INVALID_ARGUMENT
            jpath = (each_str)[0: 0 + eqpos]
            eqpos = eqpos + 1
            value = (each_str)[eqpos: eqpos + leng - eqpos]
            new_jpath.append(jpath)
            new_jpath_len.append(len(jpath))
            new_val_arr.append(value)




        i = 0
        while i < len(new_jpath):
            njpath = new_jpath[i]
            leng = len(njpath)
            cpos = njpath.find("/")
            if (cpos < 0) or (leng == 0):
                continue
            fun = (njpath)[0: 0 + cpos]
            cpos = cpos + 1
            attr = (njpath)[cpos: cpos + leng - cpos]
            do_update = True
            if fun == "services":
                do_update = False
            if (do_update) and (attr == "firmwareRelease"):
                do_update = False
            if (do_update) and (attr == "usbCurrent"):
                do_update = False
            if (do_update) and (attr == "upTime"):
                do_update = False
            if (do_update) and (attr == "persistentSettings"):
                do_update = False
            if (do_update) and (attr == "adminPassword"):
                do_update = False
            if (do_update) and (attr == "userPassword"):
                do_update = False
            if (do_update) and (attr == "rebootCountdown"):
                do_update = False
            if (do_update) and (attr == "advertisedValue"):
                do_update = False
            if (do_update) and (attr == "poeCurrent"):
                do_update = False
            if (do_update) and (attr == "readiness"):
                do_update = False
            if (do_update) and (attr == "ipAddress"):
                do_update = False
            if (do_update) and (attr == "subnetMask"):
                do_update = False
            if (do_update) and (attr == "router"):
                do_update = False
            if (do_update) and (attr == "linkQuality"):
                do_update = False
            if (do_update) and (attr == "ssid"):
                do_update = False
            if (do_update) and (attr == "channel"):
                do_update = False
            if (do_update) and (attr == "security"):
                do_update = False
            if (do_update) and (attr == "message"):
                do_update = False
            if (do_update) and (attr == "signalValue"):
                do_update = False
            if (do_update) and (attr == "currentValue"):
                do_update = False
            if (do_update) and (attr == "currentRawValue"):
                do_update = False
            if (do_update) and (attr == "currentRunIndex"):
                do_update = False
            if (do_update) and (attr == "pulseTimer"):
                do_update = False
            if (do_update) and (attr == "lastTimePressed"):
                do_update = False
            if (do_update) and (attr == "lastTimeReleased"):
                do_update = False
            if (do_update) and (attr == "filesCount"):
                do_update = False
            if (do_update) and (attr == "freeSpace"):
                do_update = False
            if (do_update) and (attr == "timeUTC"):
                do_update = False
            if (do_update) and (attr == "rtcTime"):
                do_update = False
            if (do_update) and (attr == "unixTime"):
                do_update = False
            if (do_update) and (attr == "dateTime"):
                do_update = False
            if (do_update) and (attr == "rawValue"):
                do_update = False
            if (do_update) and (attr == "lastMsg"):
                do_update = False
            if (do_update) and (attr == "delayedPulseTimer"):
                do_update = False
            if (do_update) and (attr == "rxCount"):
                do_update = False
            if (do_update) and (attr == "txCount"):
                do_update = False
            if (do_update) and (attr == "msgCount"):
                do_update = False
            if (do_update) and (attr == "rxMsgCount"):
                do_update = False
            if (do_update) and (attr == "txMsgCount"):
                do_update = False
            if do_update:
                do_update = False
                newval = new_val_arr[i]
                j = 0
                found = False
                while (j < len(old_jpath)) and not (found):
                    if (new_jpath_len[i] == old_jpath_len[j]) and (new_jpath[i] == old_jpath[j]):
                        found = True
                        oldval = old_val_arr[j]
                        if not (newval == oldval):
                            do_update = True
                    j = j + 1
            if do_update:
                if attr == "calibrationParam":
                    old_calib = ""
                    unit_name = ""
                    sensorType = ""
                    new_calib = newval
                    j = 0
                    found = False
                    while (j < len(old_jpath)) and not (found):
                        if (new_jpath_len[i] == old_jpath_len[j]) and (new_jpath[i] == old_jpath[j]):
                            found = True
                            old_calib = old_val_arr[j]
                        j = j + 1
                    tmp = fun + "/unit"
                    j = 0
                    found = False
                    while (j < len(new_jpath)) and not (found):
                        if tmp == new_jpath[j]:
                            found = True
                            unit_name = new_val_arr[j]
                        j = j + 1
                    tmp = fun + "/sensorType"
                    j = 0
                    found = False
                    while (j < len(new_jpath)) and not (found):
                        if tmp == new_jpath[j]:
                            found = True
                            sensorType = new_val_arr[j]
                        j = j + 1
                    newval = self.calibConvert(old_calib, new_val_arr[i], unit_name, sensorType)
                    url = "api/" + fun + ".json?" + attr + "=" + self._escapeAttr(newval)
                    subres = self._tryExec(url)
                    if (res == YAPI.SUCCESS) and (subres != YAPI.SUCCESS):
                        res = subres
                else:
                    url = "api/" + fun + ".json?" + attr + "=" + self._escapeAttr(oldval)
                    if attr == "resolution":
                        restoreLast.append(url)
                    else:
                        subres = self._tryExec(url)
                        if (res == YAPI.SUCCESS) and (subres != YAPI.SUCCESS):
                            res = subres
            i = i + 1

        for y in restoreLast:
            subres = self._tryExec(y)
            if (res == YAPI.SUCCESS) and (subres != YAPI.SUCCESS):
                res = subres
        self.clearCache()
        return res

    def get_hardwareId(self):
        """
        Returns the unique hardware identifier of the module.
        The unique hardware identifier is made of the device serial
        number followed by string ".module".

        @return a string that uniquely identifies the module
        """
        # serial

        serial = self.get_serialNumber()
        return serial + ".module"

    def download(self, pathname):
        """
        Downloads the specified built-in file and returns a binary buffer with its content.

        @param pathname : name of the new file to load

        @return a binary buffer with the file content

        On failure, throws an exception or returns  YAPI.INVALID_STRING.
        """
        return self._download(pathname)

    def get_icon2d(self):
        """
        Returns the icon of the module. The icon is a PNG image and does not
        exceeds 1536 bytes.

        @return a binary buffer with module icon, in png format.
                On failure, throws an exception or returns  YAPI.INVALID_STRING.
        """
        return self._download("icon2d.png")

    def get_lastLogs(self):
        """
        Returns a string with last logs of the module. This method return only
        logs that are still in the module.

        @return a string with last logs of the module.
                On failure, throws an exception or returns  YAPI.INVALID_STRING.
        """
        # content

        content = self._download("logs.txt")
        return YByte2String(content)

    def log(self, text):
        """
        Adds a text message to the device logs. This function is useful in
        particular to trace the execution of HTTP callbacks. If a newline
        is desired after the message, it must be included in the string.

        @param text : the string to append to the logs.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self._upload("logs.txt", YString2Byte(text))

    def get_subDevices(self):
        """
        Returns a list of all the modules that are plugged into the current module.
        This method only makes sense when called for a YoctoHub/VirtualHub.
        Otherwise, an empty array will be returned.

        @return an array of strings containing the sub modules.
        """
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        smallbuff = ctypes.create_string_buffer(1024)
        # bigbuff
        # buffsize
        fullsize = ctypes.c_int()
        # yapi_res
        # subdevice_list
        subdevices = []
        # serial

        serial = self.get_serialNumber()
        fullsize.value = 0
        yapi_res = YAPI._yapiGetSubdevices(ctypes.create_string_buffer(YString2Byte(serial)), smallbuff, 1024, ctypes.byref(fullsize), errmsg)
        if yapi_res < 0:
            return subdevices
        if fullsize.value <= 1024:
            subdevice_list = YByte2String(smallbuff.value)
        else:
            buffsize = fullsize.value
            bigbuff = ctypes.create_string_buffer(buffsize)
            yapi_res = YAPI._yapiGetSubdevices(ctypes.create_string_buffer(YString2Byte(serial)), bigbuff, buffsize, ctypes.byref(fullsize), errmsg)
            if yapi_res < 0:
                bigbuff = None
                return subdevices
            else:
                subdevice_list = YByte2String(bigbuff.value)
            bigbuff = None
        if not (subdevice_list == ""):
            subdevices = (subdevice_list).split(',')
        return subdevices

    def get_parentHub(self):
        """
        Returns the serial number of the YoctoHub on which this module is connected.
        If the module is connected by USB, or if the module is the root YoctoHub, an
        empty string is returned.

        @return a string with the serial number of the YoctoHub or an empty string
        """
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        hubserial = ctypes.create_string_buffer(YAPI.YOCTO_SERIAL_LEN)
        pathsize = ctypes.c_int()
        # yapi_res
        # serial

        serial = self.get_serialNumber()
        # // retrieve device object
        pathsize.value = 0
        yapi_res = YAPI._yapiGetDevicePathEx(ctypes.create_string_buffer(YString2Byte(serial)), hubserial, None, 0, ctypes.byref(pathsize), errmsg)
        if yapi_res < 0:
            return ""
        return YByte2String(hubserial.value)

    def get_url(self):
        """
        Returns the URL used to access the module. If the module is connected by USB, the
        string 'usb' is returned.

        @return a string with the URL of the module.
        """
        errmsg = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        path = ctypes.create_string_buffer(1024)
        pathsize = ctypes.c_int()
        # yapi_res
        # serial

        serial = self.get_serialNumber()
        # // retrieve device object
        pathsize.value = 0
        yapi_res = YAPI._yapiGetDevicePathEx(ctypes.create_string_buffer(YString2Byte(serial)), None, path, 1024, ctypes.byref(pathsize), errmsg)
        if yapi_res < 0:
            return ""
        return YByte2String(path.value)

    def nextModule(self):
        """
        Continues the module enumeration started using yFirstModule().
        Caution: You can't make any assumption about the returned modules order.
        If you want to find a specific module, use Module.findModule()
        and a hardwareID or a logical name.

        @return a pointer to a YModule object, corresponding to
                the next module found, or a None pointer
                if there are no more modules to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YModule.FindModule(hwidRef.value)

#--- (end of generated code: YModule implementation)

    def get_friendlyName(self):
        errmsgRef = YRefParam()
        fundescRef = YRefParam()
        fname = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        snum = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        funcid = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
        errbuff = ctypes.create_string_buffer(YAPI.YOCTO_ERRMSG_LEN)
        devdesc = ctypes.c_int()
        # Resolve the function name
        res = self._getDescriptor(fundescRef, errmsgRef)
        # noinspection PyUnresolvedReferences
        if not YAPI.YISERR(res) and not YAPI.YISERR(
                YAPI._yapiGetFunctionInfoEx(fundescRef.value, ctypes.byref(devdesc), snum, funcid, None, fname, None,
                                            errbuff)):
            dname = ctypes.create_string_buffer(YAPI.YOCTO_FUNCTION_LEN)
            moddescr = YAPI.yapiGetFunction("Module", YByte2String(snum.value), errmsgRef)
            # noinspection PyUnresolvedReference,PyUnresolvedReferences
            if not YAPI.YISERR(moddescr) and not YAPI.YISERR(
                    YAPI._yapiGetFunctionInfoEx(moddescr, ctypes.byref(devdesc), None, None, None, dname, None,
                                                errbuff)):
                if YByte2String(dname.value) != "":
                    return "%s" % (YByte2String(dname.value))
            return "%s" % (YByte2String(snum.value))
        self._throw(YAPI.DEVICE_NOT_FOUND, errmsgRef.value)
        return self.FRIENDLYNAME_INVALID

    def setImmutableAttributes(self, infosRef):
        self._serialNumber = YByte2String(infosRef.serial)
        self._productName = YByte2String(infosRef.productname)
        self._productId = int(infosRef.deviceid)
        self._cacheExpiration = YAPI.GetTickCount()

    # Return the properties of the nth function of our device
    def _getFunction(self, idx, serialRef, funcIdRef, baseType, funcNameRef, funcValRef, errmsgRef):
        functionsRef = YRefParam()
        devRef = YRefParam()
        devdescrRef = YRefParam()

        # retrieve device object
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        # get reference to all functions from the device
        res = devRef.value.getFunctions(functionsRef, errmsgRef)
        if YAPI.YISERR(res):
            return res

        # get latest function info from yellow pages
        fundescr = int(functionsRef.value[idx])

        res = YAPI.yapiGetFunctionInfoEx(fundescr, devdescrRef, serialRef, funcIdRef, baseType,
                                         funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            return res

        return YAPI.SUCCESS

    def functionCount(self):
        """
        Returns the number of functions (beside the "module" interface) available on the module.

        @return the number of functions on the module

        On failure, throws an exception or returns a negative error code.
        """
        functionsRef = YRefParam()
        devRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        res = devRef.value.getFunctions(functionsRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res

        return len(functionsRef.value)

    def functionId(self, functionIndex):
        """
        Retrieves the hardware identifier of the <i>n</i>th function on the module.

        @param functionIndex : the index of the function for which the information is desired, starting at
        0 for the first function.

        @return a string corresponding to the unambiguous hardware identifier of the requested module function

        On failure, throws an exception or returns an empty string.
        """
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        baseTypeRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getFunction(functionIndex, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return YAPI.INVALID_STRING

        return funcIdRef.value

    def functionType(self, functionIndex):
        """
        Retrieves the type of the <i>n</i>th function on the module.

        @param functionIndex : the index of the function for which the information is desired, starting at
        0 for the first function.

        @return a string corresponding to the type of the function

        On failure, throws an exception or returns an empty string.
        """
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        baseTypeRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getFunction(functionIndex, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return YAPI.INVALID_STRING

        funid = funcIdRef.value
        i = len(funid)
        while i > 0 and '0' <= funid[i-1] <= '9':
            i -= 1
        res = funid[1:i]
        return funid[0].upper() + res

    def functionBaseType(self, functionIndex):
        """
        Retrieves the base type of the <i>n</i>th function on the module.
        For instance, the base type of all measuring functions is "Sensor".

        @param functionIndex : the index of the function for which the information is desired, starting at
        0 for the first function.

        @return a string corresponding to the base type of the function

        On failure, throws an exception or returns an empty string.
        """
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        baseTypeRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getFunction(functionIndex, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef, errmsgRef)

        return baseTypeRef.value

    def functionName(self, functionIndex):
        """
        Retrieves the logical name of the <i>n</i>th function on the module.

        @param functionIndex : the index of the function for which the information is desired, starting at
        0 for the first function.

        @return a string corresponding to the logical name of the requested module function

        On failure, throws an exception or returns an empty string.
        """
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        baseTypeRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getFunction(functionIndex, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return YAPI.INVALID_STRING

        return funcNameRef.value

    def functionValue(self, functionIndex):
        """
        Retrieves the advertised value of the <i>n</i>th function on the module.

        @param functionIndex : the index of the function for which the information is desired, starting at
        0 for the first function.

        @return a short string (up to 6 characters) corresponding to the advertised value of the requested
        module function

        On failure, throws an exception or returns an empty string.
        """
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        baseTypeRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()

        res = self._getFunction(functionIndex, serialRef, funcIdRef, baseTypeRef, funcNameRef, funcValRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return YAPI.INVALID_STRING

        return funcValRef.value

    # --- (generated code: YModule functions)

    @staticmethod
    def FirstModule():
        """
        Starts the enumeration of modules currently accessible.
        Use the method YModule.nextModule() to iterate on the
        next modules.

        @return a pointer to a YModule object, corresponding to
                the first module currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Module", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YModule.FindModule(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YModule functions)


# --- (generated code: YSensor class start)
#noinspection PyProtectedMember
class YSensor(YFunction):
    """
    The YSensor class is the parent class for all Yoctopuce sensor types. It can be
    used to read the current value and unit of any sensor, read the min/max
    value, configure autonomous recording frequency and access recorded data.
    It also provide a function to register a callback invoked each time the
    observed value changes, or at a predefined interval. Using this class rather
    than a specific subclass makes it possible to create generic applications
    that work with any Yoctopuce sensor, even those that do not yet exist.
    Note: The YAnButton class is the only analog input which does not inherit
    from YSensor.

    """
    #--- (end of generated code: YSensor class start)
    # --- (generated code: YSensor return codes)
    #--- (end of generated code: YSensor return codes)
    # --- (generated code: YSensor definitions)
    UNIT_INVALID = YAPI.INVALID_STRING
    CURRENTVALUE_INVALID = YAPI.INVALID_DOUBLE
    LOWESTVALUE_INVALID = YAPI.INVALID_DOUBLE
    HIGHESTVALUE_INVALID = YAPI.INVALID_DOUBLE
    CURRENTRAWVALUE_INVALID = YAPI.INVALID_DOUBLE
    LOGFREQUENCY_INVALID = YAPI.INVALID_STRING
    REPORTFREQUENCY_INVALID = YAPI.INVALID_STRING
    CALIBRATIONPARAM_INVALID = YAPI.INVALID_STRING
    RESOLUTION_INVALID = YAPI.INVALID_DOUBLE
    SENSORSTATE_INVALID = YAPI.INVALID_INT
    ADVMODE_IMMEDIATE = 0
    ADVMODE_PERIOD_AVG = 1
    ADVMODE_PERIOD_MIN = 2
    ADVMODE_PERIOD_MAX = 3
    ADVMODE_INVALID = -1
    #--- (end of generated code: YSensor definitions)

    def __init__(self, func):
        super(YSensor, self).__init__(func)
        self._className = "Sensor"
        # --- (generated code: YSensor attributes)
        self._callback = None
        self._unit = YSensor.UNIT_INVALID
        self._currentValue = YSensor.CURRENTVALUE_INVALID
        self._lowestValue = YSensor.LOWESTVALUE_INVALID
        self._highestValue = YSensor.HIGHESTVALUE_INVALID
        self._currentRawValue = YSensor.CURRENTRAWVALUE_INVALID
        self._logFrequency = YSensor.LOGFREQUENCY_INVALID
        self._reportFrequency = YSensor.REPORTFREQUENCY_INVALID
        self._advMode = YSensor.ADVMODE_INVALID
        self._calibrationParam = YSensor.CALIBRATIONPARAM_INVALID
        self._resolution = YSensor.RESOLUTION_INVALID
        self._sensorState = YSensor.SENSORSTATE_INVALID
        self._timedReportCallbackSensor = None
        self._prevTimedReport = 0
        self._iresol = 0
        self._offset = 0
        self._scale = 0
        self._decexp = 0
        self._caltyp = 0
        self._calpar = []
        self._calraw = []
        self._calref = []
        self._calhdl = None
        #--- (end of generated code: YSensor attributes)

    # --- (generated code: YSensor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("unit"):
            self._unit = json_val.getString("unit")
        if json_val.has("currentValue"):
            self._currentValue = round(json_val.getDouble("currentValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("lowestValue"):
            self._lowestValue = round(json_val.getDouble("lowestValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("highestValue"):
            self._highestValue = round(json_val.getDouble("highestValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("currentRawValue"):
            self._currentRawValue = round(json_val.getDouble("currentRawValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("logFrequency"):
            self._logFrequency = json_val.getString("logFrequency")
        if json_val.has("reportFrequency"):
            self._reportFrequency = json_val.getString("reportFrequency")
        if json_val.has("advMode"):
            self._advMode = json_val.getInt("advMode")
        if json_val.has("calibrationParam"):
            self._calibrationParam = json_val.getString("calibrationParam")
        if json_val.has("resolution"):
            self._resolution = round(json_val.getDouble("resolution") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("sensorState"):
            self._sensorState = json_val.getInt("sensorState")
        super(YSensor, self)._parseAttr(json_val)

    def get_unit(self):
        """
        Returns the measuring unit for the measure.

        @return a string corresponding to the measuring unit for the measure

        On failure, throws an exception or returns YSensor.UNIT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.UNIT_INVALID
        res = self._unit
        return res

    def get_currentValue(self):
        """
        Returns the current value of the measure, in the specified unit, as a floating point number.
        Note that a get_currentValue() call will *not* start a measure in the device, it
        will just return the last measure that occurred in the device. Indeed, internally, each Yoctopuce
        devices is continuously making measurements at a hardware specific frequency.

        If continuously calling  get_currentValue() leads you to performances issues, then
        you might consider to switch to callback programming model. Check the "advanced
        programming" chapter in in your device user manual for more information.

        @return a floating point number corresponding to the current value of the measure, in the specified
        unit, as a floating point number

        On failure, throws an exception or returns YSensor.CURRENTVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.CURRENTVALUE_INVALID
        res = self._applyCalibration(self._currentRawValue)
        if res == YSensor.CURRENTVALUE_INVALID:
            res = self._currentValue
        res = res * self._iresol
        res = round(res) / self._iresol
        return res

    def set_lowestValue(self, newval):
        """
        Changes the recorded minimal value observed. Can be used to reset the value returned
        by get_lowestValue().

        @param newval : a floating point number corresponding to the recorded minimal value observed

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("lowestValue", rest_val)

    def get_lowestValue(self):
        """
        Returns the minimal value observed for the measure since the device was started.
        Can be reset to an arbitrary value thanks to set_lowestValue().

        @return a floating point number corresponding to the minimal value observed for the measure since
        the device was started

        On failure, throws an exception or returns YSensor.LOWESTVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.LOWESTVALUE_INVALID
        res = self._lowestValue * self._iresol
        res = round(res) / self._iresol
        return res

    def set_highestValue(self, newval):
        """
        Changes the recorded maximal value observed. Can be used to reset the value returned
        by get_lowestValue().

        @param newval : a floating point number corresponding to the recorded maximal value observed

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("highestValue", rest_val)

    def get_highestValue(self):
        """
        Returns the maximal value observed for the measure since the device was started.
        Can be reset to an arbitrary value thanks to set_highestValue().

        @return a floating point number corresponding to the maximal value observed for the measure since
        the device was started

        On failure, throws an exception or returns YSensor.HIGHESTVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.HIGHESTVALUE_INVALID
        res = self._highestValue * self._iresol
        res = round(res) / self._iresol
        return res

    def get_currentRawValue(self):
        """
        Returns the uncalibrated, unrounded raw value returned by the
        sensor, in the specified unit, as a floating point number.

        @return a floating point number corresponding to the uncalibrated, unrounded raw value returned by the
                sensor, in the specified unit, as a floating point number

        On failure, throws an exception or returns YSensor.CURRENTRAWVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.CURRENTRAWVALUE_INVALID
        res = self._currentRawValue
        return res

    def get_logFrequency(self):
        """
        Returns the datalogger recording frequency for this function, or "OFF"
        when measures are not stored in the data logger flash memory.

        @return a string corresponding to the datalogger recording frequency for this function, or "OFF"
                when measures are not stored in the data logger flash memory

        On failure, throws an exception or returns YSensor.LOGFREQUENCY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.LOGFREQUENCY_INVALID
        res = self._logFrequency
        return res

    def set_logFrequency(self, newval):
        """
        Changes the datalogger recording frequency for this function.
        The frequency can be specified as samples per second,
        as sample per minute (for instance "15/m") or in samples per
        hour (eg. "4/h"). To disable recording for this function, use
        the value "OFF". Note that setting the  datalogger recording frequency
        to a greater value than the sensor native sampling frequency is useless,
        and even counterproductive: those two frequencies are not related.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a string corresponding to the datalogger recording frequency for this function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("logFrequency", rest_val)

    def get_reportFrequency(self):
        """
        Returns the timed value notification frequency, or "OFF" if timed
        value notifications are disabled for this function.

        @return a string corresponding to the timed value notification frequency, or "OFF" if timed
                value notifications are disabled for this function

        On failure, throws an exception or returns YSensor.REPORTFREQUENCY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.REPORTFREQUENCY_INVALID
        res = self._reportFrequency
        return res

    def set_reportFrequency(self, newval):
        """
        Changes the timed value notification frequency for this function.
        The frequency can be specified as samples per second,
        as sample per minute (for instance "15/m") or in samples per
        hour (e.g. "4/h"). To disable timed value notifications for this
        function, use the value "OFF". Note that setting the  timed value
        notification frequency to a greater value than the sensor native
        sampling frequency is unless, and even counterproductive: those two
        frequencies are not related.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a string corresponding to the timed value notification frequency for this function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("reportFrequency", rest_val)

    def get_advMode(self):
        """
        Returns the measuring mode used for the advertised value pushed to the parent hub.

        @return a value among YSensor.ADVMODE_IMMEDIATE, YSensor.ADVMODE_PERIOD_AVG,
        YSensor.ADVMODE_PERIOD_MIN and YSensor.ADVMODE_PERIOD_MAX corresponding to the measuring mode used
        for the advertised value pushed to the parent hub

        On failure, throws an exception or returns YSensor.ADVMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.ADVMODE_INVALID
        res = self._advMode
        return res

    def set_advMode(self, newval):
        """
        Changes the measuring mode used for the advertised value pushed to the parent hub.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a value among YSensor.ADVMODE_IMMEDIATE, YSensor.ADVMODE_PERIOD_AVG,
        YSensor.ADVMODE_PERIOD_MIN and YSensor.ADVMODE_PERIOD_MAX corresponding to the measuring mode used
        for the advertised value pushed to the parent hub

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("advMode", rest_val)

    def get_calibrationParam(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.CALIBRATIONPARAM_INVALID
        res = self._calibrationParam
        return res

    def set_calibrationParam(self, newval):
        rest_val = newval
        return self._setAttr("calibrationParam", rest_val)

    def set_resolution(self, newval):
        """
        Changes the resolution of the measured physical values. The resolution corresponds to the numerical precision
        when displaying value. It does not change the precision of the measure itself.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @param newval : a floating point number corresponding to the resolution of the measured physical values

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("resolution", rest_val)

    def get_resolution(self):
        """
        Returns the resolution of the measured values. The resolution corresponds to the numerical precision
        of the measures, which is not always the same as the actual precision of the sensor.
        Remember to call the saveToFlash() method of the module if the modification must be kept.

        @return a floating point number corresponding to the resolution of the measured values

        On failure, throws an exception or returns YSensor.RESOLUTION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.RESOLUTION_INVALID
        res = self._resolution
        return res

    def get_sensorState(self):
        """
        Returns the sensor health state code, which is zero when there is an up-to-date measure
        available or a positive code if the sensor is not able to provide a measure right now.

        @return an integer corresponding to the sensor health state code, which is zero when there is an
        up-to-date measure
                available or a positive code if the sensor is not able to provide a measure right now

        On failure, throws an exception or returns YSensor.SENSORSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSensor.SENSORSTATE_INVALID
        res = self._sensorState
        return res

    @staticmethod
    def FindSensor(func):
        """
        Retrieves a sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSensor.isOnline() to test if the sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the sensor, for instance
                MyDevice..

        @return a YSensor object allowing you to drive the sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Sensor", func)
        if obj is None:
            obj = YSensor(func)
            YFunction._AddToCache("Sensor", func, obj)
        return obj

    def _parserHelper(self):
        # position
        # maxpos
        iCalib = []
        # iRaw
        # iRef
        # fRaw
        # fRef
        self._caltyp = -1
        self._scale = -1
        del self._calpar[:]
        del self._calraw[:]
        del self._calref[:]
        # // Store inverted resolution, to provide better rounding
        if self._resolution > 0:
            self._iresol = round(1.0 / self._resolution)
        else:
            self._iresol = 10000
            self._resolution = 0.0001
        # // Old format: supported when there is no calibration
        if self._calibrationParam == "" or self._calibrationParam == "0":
            self._caltyp = 0
            return 0
        if self._calibrationParam.find(",") >= 0:
            # // Plain text format
            iCalib = YAPI._decodeFloats(self._calibrationParam)
            self._caltyp = int((iCalib[0]) / (1000))
            if self._caltyp > 0:
                if self._caltyp < YAPI.YOCTO_CALIB_TYPE_OFS:
                    # // Unknown calibration type: calibrated value will be provided by the device
                    self._caltyp = -1
                    return 0
                self._calhdl = YAPI._getCalibrationHandler(self._caltyp)
                if not (self._calhdl is not None):
                    # // Unknown calibration type: calibrated value will be provided by the device
                    self._caltyp = -1
                    return 0
            # // New 32 bits text format
            self._offset = 0
            self._scale = 1000
            maxpos = len(iCalib)
            del self._calpar[:]
            position = 1
            while position < maxpos:
                self._calpar.append(iCalib[position])
                position = position + 1
            del self._calraw[:]
            del self._calref[:]
            position = 1
            while position + 1 < maxpos:
                fRaw = iCalib[position]
                fRaw = fRaw / 1000.0
                fRef = iCalib[position + 1]
                fRef = fRef / 1000.0
                self._calraw.append(fRaw)
                self._calref.append(fRef)
                position = position + 2
        else:
            # // Recorder-encoded format, including encoding
            iCalib = YAPI._decodeWords(self._calibrationParam)
            # // In case of unknown format, calibrated value will be provided by the device
            if len(iCalib) < 2:
                self._caltyp = -1
                return 0
            # // Save variable format (scale for scalar, or decimal exponent)
            self._offset = 0
            self._scale = 1
            self._decexp = 1.0
            position = iCalib[0]
            while position > 0:
                self._decexp = self._decexp * 10
                position = position - 1
            # // Shortcut when there is no calibration parameter
            if len(iCalib) == 2:
                self._caltyp = 0
                return 0
            self._caltyp = iCalib[2]
            self._calhdl = YAPI._getCalibrationHandler(self._caltyp)
            # // parse calibration points
            if self._caltyp <= 10:
                maxpos = self._caltyp
            else:
                if self._caltyp <= 20:
                    maxpos = self._caltyp - 10
                else:
                    maxpos = 5
            maxpos = 3 + 2 * maxpos
            if maxpos > len(iCalib):
                maxpos = len(iCalib)
            del self._calpar[:]
            del self._calraw[:]
            del self._calref[:]
            position = 3
            while position + 1 < maxpos:
                iRaw = iCalib[position]
                iRef = iCalib[position + 1]
                self._calpar.append(iRaw)
                self._calpar.append(iRef)
                self._calraw.append(YAPI._decimalToDouble(iRaw))
                self._calref.append(YAPI._decimalToDouble(iRef))
                position = position + 2
        return 0

    def isSensorReady(self):
        """
        Checks if the sensor is currently able to provide an up-to-date measure.
        Returns false if the device is unreachable, or if the sensor does not have
        a current measure to transmit. No exception is raised if there is an error
        while trying to contact the device hosting $THEFUNCTION$.

        @return true if the sensor can provide an up-to-date measure, and false otherwise
        """
        if not (self.isOnline()):
            return False
        if not (self._sensorState == 0):
            return False
        return True

    def get_dataLogger(self):
        """
        Returns the YDatalogger object of the device hosting the sensor. This method returns an object
        that can control global parameters of the data logger. The returned object
        should not be freed.

        @return an YDatalogger object, or None on error.
        """
        # logger
        # modu
        # serial
        # hwid

        modu = self.get_module()
        serial = modu.get_serialNumber()
        if serial == YAPI.INVALID_STRING:
            return None
        hwid = serial + ".dataLogger"
        logger = YDataLogger.FindDataLogger(hwid)
        return logger

    def startDataLogger(self):
        """
        Starts the data logger on the device. Note that the data logger
        will only save the measures on this sensor if the logFrequency
        is not set to "OFF".

        @return YAPI.SUCCESS if the call succeeds.
        """
        # res

        res = self._download("api/dataLogger/recording?recording=1")
        if not (len(res)>0):
            self._throw(YAPI.IO_ERROR, "unable to start datalogger")
            return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def stopDataLogger(self):
        """
        Stops the datalogger on the device.

        @return YAPI.SUCCESS if the call succeeds.
        """
        # res

        res = self._download("api/dataLogger/recording?recording=0")
        if not (len(res)>0):
            self._throw(YAPI.IO_ERROR, "unable to stop datalogger")
            return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def get_recordedData(self, startTime, endTime):
        """
        Retrieves a YDataSet object holding historical data for this
        sensor, for a specified time interval. The measures will be
        retrieved from the data logger, which must have been turned
        on at the desired time. See the documentation of the YDataSet
        class for information on how to get an overview of the
        recorded data, and how to load progressively a large set
        of measures from the data logger.

        This function only works if the device uses a recent firmware,
        as YDataSet objects are not supported by firmwares older than
        version 13000.

        @param startTime : the start of the desired measure time interval,
                as a Unix timestamp, i.e. the number of seconds since
                January 1, 1970 UTC. The special value 0 can be used
                to include any measure, without initial limit.
        @param endTime : the end of the desired measure time interval,
                as a Unix timestamp, i.e. the number of seconds since
                January 1, 1970 UTC. The special value 0 can be used
                to include any measure, without ending limit.

        @return an instance of YDataSet, providing access to historical
                data. Past measures can be loaded progressively
                using methods from the YDataSet object.
        """
        # funcid
        # funit

        funcid = self.get_functionId()
        funit = self.get_unit()
        return YDataSet(self, funcid, funit, startTime, endTime)

    def registerTimedReportCallback(self, callback):
        """
        Registers the callback function that is invoked on every periodic timed notification.
        The callback is invoked only during the execution of ySleep or yHandleEvents.
        This provides control over the time when the callback is triggered. For good responsiveness, remember to call
        one of these two functions periodically. To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to call, or a None pointer. The callback function should take two
                arguments: the function object of which the value has changed, and an YMeasure object describing
                the new advertised value.
        @noreturn
        """
        # sensor
        sensor = self
        if callback is not None:
            YFunction._UpdateTimedReportCallbackList(sensor, True)
        else:
            YFunction._UpdateTimedReportCallbackList(sensor, False)
        self._timedReportCallbackSensor = callback
        return 0

    def _invokeTimedReportCallback(self, value):
        if self._timedReportCallbackSensor is not None:
            self._timedReportCallbackSensor(self, value)
        return 0

    def calibrateFromPoints(self, rawValues, refValues):
        """
        Configures error correction data points, in particular to compensate for
        a possible perturbation of the measure caused by an enclosure. It is possible
        to configure up to five correction points. Correction points must be provided
        in ascending order, and be in the range of the sensor. The device will automatically
        perform a linear interpolation of the error correction between specified
        points. Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        For more information on advanced capabilities to refine the calibration of
        sensors, please contact support@yoctopuce.com.

        @param rawValues : array of floating point numbers, corresponding to the raw
                values returned by the sensor for the correction points.
        @param refValues : array of floating point numbers, corresponding to the corrected
                values for the correction points.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # rest_val
        # res

        rest_val = self._encodeCalibrationPoints(rawValues, refValues)
        res = self._setAttr("calibrationParam", rest_val)
        return res

    def loadCalibrationPoints(self, rawValues, refValues):
        """
        Retrieves error correction data points previously entered using the method
        calibrateFromPoints.

        @param rawValues : array of floating point numbers, that will be filled by the
                function with the raw sensor values for the correction points.
        @param refValues : array of floating point numbers, that will be filled by the
                function with the desired values for the correction points.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        del rawValues[:]
        del refValues[:]
        # // Load function parameters if not yet loaded
        if self._scale == 0:
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
        if self._caltyp < 0:
            self._throw(YAPI.NOT_SUPPORTED, "Calibration parameters format mismatch. Please upgrade your library or firmware.")
            return YAPI.NOT_SUPPORTED
        del rawValues[:]
        del refValues[:]
        for y in self._calraw:
            rawValues.append(y)
        for y in self._calref:
            refValues.append(y)
        return YAPI.SUCCESS

    def _encodeCalibrationPoints(self, rawValues, refValues):
        # res
        # npt
        # idx
        npt = len(rawValues)
        if npt != len(refValues):
            self._throw(YAPI.INVALID_ARGUMENT, "Invalid calibration parameters (size mismatch)")
            return YAPI.INVALID_STRING
        # // Shortcut when building empty calibration parameters
        if npt == 0:
            return "0"
        # // Load function parameters if not yet loaded
        if self._scale == 0:
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAPI.INVALID_STRING
        # // Detect old firmware
        if (self._caltyp < 0) or (self._scale < 0):
            self._throw(YAPI.NOT_SUPPORTED, "Calibration parameters format mismatch. Please upgrade your library or firmware.")
            return "0"
        # // 32-bit fixed-point encoding
        res = "" + str(int(YAPI.YOCTO_CALIB_TYPE_OFS))
        idx = 0
        while idx < npt:
            res = "" + res + "," + str(rawValues[idx]) + "," + str(refValues[idx])
            idx = idx + 1
        return res

    def _applyCalibration(self, rawValue):
        if rawValue == YSensor.CURRENTVALUE_INVALID:
            return YSensor.CURRENTVALUE_INVALID
        if self._caltyp == 0:
            return rawValue
        if self._caltyp < 0:
            return YSensor.CURRENTVALUE_INVALID
        if not (self._calhdl is not None):
            return YSensor.CURRENTVALUE_INVALID
        return self._calhdl(rawValue, self._caltyp, self._calpar, self._calraw, self._calref)

    def _decodeTimedReport(self, timestamp, duration, report):
        # i
        # byteVal
        # poww
        # minRaw
        # avgRaw
        # maxRaw
        # sublen
        # difRaw
        # startTime
        # endTime
        # minVal
        # avgVal
        # maxVal
        if duration > 0:
            startTime = timestamp - duration
        else:
            startTime = self._prevTimedReport
        endTime = timestamp
        self._prevTimedReport = endTime
        if startTime == 0:
            startTime = endTime
        # // 32 bits timed report format
        if len(report) <= 5:
            # // sub-second report, 1-4 bytes
            poww = 1
            avgRaw = 0
            byteVal = 0
            i = 1
            while i < len(report):
                byteVal = report[i]
                avgRaw = avgRaw + poww * byteVal
                poww = poww * 0x100
                i = i + 1
            if ((byteVal) & (0x80)) != 0:
                avgRaw = avgRaw - poww
            avgVal = avgRaw / 1000.0
            if self._caltyp != 0:
                if self._calhdl is not None:
                    avgVal = self._calhdl(avgVal, self._caltyp, self._calpar, self._calraw, self._calref)
            minVal = avgVal
            maxVal = avgVal
        else:
            # // averaged report: avg,avg-min,max-avg
            sublen = 1 + ((report[1]) & (3))
            poww = 1
            avgRaw = 0
            byteVal = 0
            i = 2
            while (sublen > 0) and (i < len(report)):
                byteVal = report[i]
                avgRaw = avgRaw + poww * byteVal
                poww = poww * 0x100
                i = i + 1
                sublen = sublen - 1
            if ((byteVal) & (0x80)) != 0:
                avgRaw = avgRaw - poww
            sublen = 1 + ((((report[1]) >> (2))) & (3))
            poww = 1
            difRaw = 0
            while (sublen > 0) and (i < len(report)):
                byteVal = report[i]
                difRaw = difRaw + poww * byteVal
                poww = poww * 0x100
                i = i + 1
                sublen = sublen - 1
            minRaw = avgRaw - difRaw
            sublen = 1 + ((((report[1]) >> (4))) & (3))
            poww = 1
            difRaw = 0
            while (sublen > 0) and (i < len(report)):
                byteVal = report[i]
                difRaw = difRaw + poww * byteVal
                poww = poww * 0x100
                i = i + 1
                sublen = sublen - 1
            maxRaw = avgRaw + difRaw
            avgVal = avgRaw / 1000.0
            minVal = minRaw / 1000.0
            maxVal = maxRaw / 1000.0
            if self._caltyp != 0:
                if self._calhdl is not None:
                    avgVal = self._calhdl(avgVal, self._caltyp, self._calpar, self._calraw, self._calref)
                    minVal = self._calhdl(minVal, self._caltyp, self._calpar, self._calraw, self._calref)
                    maxVal = self._calhdl(maxVal, self._caltyp, self._calpar, self._calraw, self._calref)
        return YMeasure(startTime, endTime, minVal, avgVal, maxVal)

    def _decodeVal(self, w):
        # val
        val = w if w <= 0x7fffffff else -0x100000000 + w
        if self._caltyp != 0:
            if self._calhdl is not None:
                val = self._calhdl(val, self._caltyp, self._calpar, self._calraw, self._calref)
        return val

    def _decodeAvg(self, dw):
        # val
        val = dw if dw <= 0x7fffffff else -0x100000000 + dw
        if self._caltyp != 0:
            if self._calhdl is not None:
                val = self._calhdl(val, self._caltyp, self._calpar, self._calraw, self._calref)
        return val

    def nextSensor(self):
        """
        Continues the enumeration of sensors started using yFirstSensor().
        Caution: You can't make any assumption about the returned sensors order.
        If you want to find a specific a sensor, use Sensor.findSensor()
        and a hardwareID or a logical name.

        @return a pointer to a YSensor object, corresponding to
                a sensor currently online, or a None pointer
                if there are no more sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YSensor.FindSensor(hwidRef.value)

#--- (end of generated code: YSensor implementation)

    # --- (generated code: YSensor functions)

    @staticmethod
    def FirstSensor():
        """
        Starts the enumeration of sensors currently accessible.
        Use the method YSensor.nextSensor() to iterate on
        next sensors.

        @return a pointer to a YSensor object, corresponding to
                the first sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Sensor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YSensor.FindSensor(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YSensor functions)


# --- (generated code: YDataLogger class start)
#noinspection PyProtectedMember
class YDataLogger(YFunction):
    """
    A non-volatile memory for storing ongoing measured data is available on most Yoctopuce
    sensors. Recording can happen automatically, without requiring a permanent
    connection to a computer.
    The YDataLogger class controls the global parameters of the internal data
    logger. Recording control (start/stop) as well as data retreival is done at
    sensor objects level.

    """
    #--- (end of generated code: YDataLogger class start)

    Y_DATA_INVALID = YAPI.INVALID_DOUBLE

    # --- (generated code: YDataLogger definitions)
    CURRENTRUNINDEX_INVALID = YAPI.INVALID_UINT
    TIMEUTC_INVALID = YAPI.INVALID_LONG
    USAGE_INVALID = YAPI.INVALID_UINT
    RECORDING_OFF = 0
    RECORDING_ON = 1
    RECORDING_PENDING = 2
    RECORDING_INVALID = -1
    AUTOSTART_OFF = 0
    AUTOSTART_ON = 1
    AUTOSTART_INVALID = -1
    BEACONDRIVEN_OFF = 0
    BEACONDRIVEN_ON = 1
    BEACONDRIVEN_INVALID = -1
    CLEARHISTORY_FALSE = 0
    CLEARHISTORY_TRUE = 1
    CLEARHISTORY_INVALID = -1
    #--- (end of generated code: YDataLogger definitions)

    def __init__(self, func):
        super(YDataLogger, self).__init__(func)
        self._className = "DataLogger"
        # --- (generated code: YDataLogger attributes)
        self._callback = None
        self._currentRunIndex = YDataLogger.CURRENTRUNINDEX_INVALID
        self._timeUTC = YDataLogger.TIMEUTC_INVALID
        self._recording = YDataLogger.RECORDING_INVALID
        self._autoStart = YDataLogger.AUTOSTART_INVALID
        self._beaconDriven = YDataLogger.BEACONDRIVEN_INVALID
        self._usage = YDataLogger.USAGE_INVALID
        self._clearHistory = YDataLogger.CLEARHISTORY_INVALID
        #--- (end of generated code: YDataLogger attributes)
        self._dataLoggerURL = ""

    # --- (generated code: YDataLogger implementation)
    def _parseAttr(self, json_val):
        if json_val.has("currentRunIndex"):
            self._currentRunIndex = json_val.getInt("currentRunIndex")
        if json_val.has("timeUTC"):
            self._timeUTC = json_val.getLong("timeUTC")
        if json_val.has("recording"):
            self._recording = json_val.getInt("recording")
        if json_val.has("autoStart"):
            self._autoStart = (json_val.getInt("autoStart") > 0 if 1 else 0)
        if json_val.has("beaconDriven"):
            self._beaconDriven = (json_val.getInt("beaconDriven") > 0 if 1 else 0)
        if json_val.has("usage"):
            self._usage = json_val.getInt("usage")
        if json_val.has("clearHistory"):
            self._clearHistory = (json_val.getInt("clearHistory") > 0 if 1 else 0)
        super(YDataLogger, self)._parseAttr(json_val)

    def get_currentRunIndex(self):
        """
        Returns the current run number, corresponding to the number of times the module was
        powered on with the dataLogger enabled at some point.

        @return an integer corresponding to the current run number, corresponding to the number of times the module was
                powered on with the dataLogger enabled at some point

        On failure, throws an exception or returns YDataLogger.CURRENTRUNINDEX_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.CURRENTRUNINDEX_INVALID
        res = self._currentRunIndex
        return res

    def get_timeUTC(self):
        """
        Returns the Unix timestamp for current UTC time, if known.

        @return an integer corresponding to the Unix timestamp for current UTC time, if known

        On failure, throws an exception or returns YDataLogger.TIMEUTC_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.TIMEUTC_INVALID
        res = self._timeUTC
        return res

    def set_timeUTC(self, newval):
        """
        Changes the current UTC time reference used for recorded data.

        @param newval : an integer corresponding to the current UTC time reference used for recorded data

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("timeUTC", rest_val)

    def get_recording(self):
        """
        Returns the current activation state of the data logger.

        @return a value among YDataLogger.RECORDING_OFF, YDataLogger.RECORDING_ON and
        YDataLogger.RECORDING_PENDING corresponding to the current activation state of the data logger

        On failure, throws an exception or returns YDataLogger.RECORDING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.RECORDING_INVALID
        res = self._recording
        return res

    def set_recording(self, newval):
        """
        Changes the activation state of the data logger to start/stop recording data.

        @param newval : a value among YDataLogger.RECORDING_OFF, YDataLogger.RECORDING_ON and
        YDataLogger.RECORDING_PENDING corresponding to the activation state of the data logger to
        start/stop recording data

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("recording", rest_val)

    def get_autoStart(self):
        """
        Returns the default activation state of the data logger on power up.

        @return either YDataLogger.AUTOSTART_OFF or YDataLogger.AUTOSTART_ON, according to the default
        activation state of the data logger on power up

        On failure, throws an exception or returns YDataLogger.AUTOSTART_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.AUTOSTART_INVALID
        res = self._autoStart
        return res

    def set_autoStart(self, newval):
        """
        Changes the default activation state of the data logger on power up.
        Do not forget to call the saveToFlash() method of the module to save the
        configuration change.  Note: if the device doesn't have any time source at his disposal when
        starting up, it will wait for ~8 seconds before automatically starting to record  with
        an arbitrary timestamp

        @param newval : either YDataLogger.AUTOSTART_OFF or YDataLogger.AUTOSTART_ON, according to the
        default activation state of the data logger on power up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("autoStart", rest_val)

    def get_beaconDriven(self):
        """
        Returns true if the data logger is synchronised with the localization beacon.

        @return either YDataLogger.BEACONDRIVEN_OFF or YDataLogger.BEACONDRIVEN_ON, according to true if
        the data logger is synchronised with the localization beacon

        On failure, throws an exception or returns YDataLogger.BEACONDRIVEN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.BEACONDRIVEN_INVALID
        res = self._beaconDriven
        return res

    def set_beaconDriven(self, newval):
        """
        Changes the type of synchronisation of the data logger.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : either YDataLogger.BEACONDRIVEN_OFF or YDataLogger.BEACONDRIVEN_ON, according to
        the type of synchronisation of the data logger

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("beaconDriven", rest_val)

    def get_usage(self):
        """
        Returns the percentage of datalogger memory in use.

        @return an integer corresponding to the percentage of datalogger memory in use

        On failure, throws an exception or returns YDataLogger.USAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.USAGE_INVALID
        res = self._usage
        return res

    def get_clearHistory(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDataLogger.CLEARHISTORY_INVALID
        res = self._clearHistory
        return res

    def set_clearHistory(self, newval):
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("clearHistory", rest_val)

    @staticmethod
    def FindDataLogger(func):
        """
        Retrieves a data logger for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the data logger is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDataLogger.isOnline() to test if the data logger is
        indeed online at a given time. In case of ambiguity when looking for
        a data logger by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the data logger, for instance
                Y3DMK002.dataLogger.

        @return a YDataLogger object allowing you to drive the data logger.
        """
        # obj
        obj = YFunction._FindFromCache("DataLogger", func)
        if obj is None:
            obj = YDataLogger(func)
            YFunction._AddToCache("DataLogger", func, obj)
        return obj

    def forgetAllDataStreams(self):
        """
        Clears the data logger memory and discards all recorded data streams.
        This method also resets the current run index to zero.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_clearHistory(YDataLogger.CLEARHISTORY_TRUE)

    def get_dataSets(self):
        """
        Returns a list of YDataSet objects that can be used to retrieve
        all measures stored by the data logger.

        This function only works if the device uses a recent firmware,
        as YDataSet objects are not supported by firmwares older than
        version 13000.

        @return a list of YDataSet object.

        On failure, throws an exception or returns an empty list.
        """
        return self.parse_dataSets(self._download("logger.json"))

    def parse_dataSets(self, json):
        dslist = []
        # dataset
        res = []

        dslist = self._json_get_array(json)
        del res[:]
        for y in dslist:
            dataset = YDataSet(self)
            dataset._parse(y)
            res.append(dataset)
        return res

    def nextDataLogger(self):
        """
        Continues the enumeration of data loggers started using yFirstDataLogger().
        Caution: You can't make any assumption about the returned data loggers order.
        If you want to find a specific a data logger, use DataLogger.findDataLogger()
        and a hardwareID or a logical name.

        @return a pointer to a YDataLogger object, corresponding to
                a data logger currently online, or a None pointer
                if there are no more data loggers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YDataLogger.FindDataLogger(hwidRef.value)

#--- (end of generated code: YDataLogger implementation)

    def getData(self, runIdx, timeIdx, jsondataRef):
        devRef = YRefParam()
        errmsgRef = YRefParam()
        bufferRef = YRefParam()
        if self._dataLoggerURL == "":
            self._dataLoggerURL = "/logger.json"

        # Resolve our reference to our device, load REST API
        res = self._getDevice(devRef, errmsgRef)
        if YAPI.YISERR(res):
            self._throw(res, errmsgRef.value)
            return res
        if timeIdx > 0:
            query = "GET " + self._dataLoggerURL + "?run=" + str(runIdx) + "&time=" + str(timeIdx) + " HTTP/1.1\r\n\r\n"
        else:
            query = "GET " + self._dataLoggerURL + " HTTP/1.1\r\n\r\n"
        res = devRef.value.HTTPRequest(query, bufferRef, errmsgRef)
        if YAPI.YISERR(res):
            res = YAPI.UpdateDeviceList(errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return res
            res = devRef.value.HTTPRequest("GET " + self._dataLoggerURL + " HTTP/1.1\n\r\n\r", bufferRef, errmsgRef)
            if YAPI.YISERR(res):
                self._throw(res, errmsgRef.value)
                return res

        buffer = YByte2String(bufferRef.value)
        (httpcode, http_headerlen, errmsg) = YAPI.parseHTTP(buffer, 0, len(buffer))
        if httpcode != 200:
            errmsgRef.value = "Unexpected HTTP return code:%s" % httpcode
            return YAPI.IO_ERROR

        jsondataRef.value = buffer[http_headerlen:]
        return YAPI.SUCCESS

    # --- (generated code: YDataLogger functions)

    @staticmethod
    def FirstDataLogger():
        """
        Starts the enumeration of data loggers currently accessible.
        Use the method YDataLogger.nextDataLogger() to iterate on
        next data loggers.

        @return a pointer to a YDataLogger object, corresponding to
                the first data logger currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("DataLogger", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YDataLogger.FindDataLogger(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YDataLogger functions)
