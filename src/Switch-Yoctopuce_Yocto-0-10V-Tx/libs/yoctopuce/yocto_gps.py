# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_gps.py 39658 2020-03-12 15:36:29Z seb $
#
#  Implements yFindGps(), the high-level API for Gps functions
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


#--- (YGps class start)
#noinspection PyProtectedMember
class YGps(YFunction):
    """
    The YGps class allows you to retrieve positioning
    data from a GPS/GNSS sensor. This class can provides
    complete positioning information. However, if you
    wish to define callbacks on position changes or record
    the position in the datalogger, you
    should use the YLatitude et YLongitude classes.

    """
    #--- (end of YGps class start)
    #--- (YGps return codes)
    #--- (end of YGps return codes)
    #--- (YGps dlldef)
    #--- (end of YGps dlldef)
    #--- (YGps yapiwrapper)
    #--- (end of YGps yapiwrapper)
    #--- (YGps definitions)
    SATCOUNT_INVALID = YAPI.INVALID_LONG
    SATPERCONST_INVALID = YAPI.INVALID_LONG
    GPSREFRESHRATE_INVALID = YAPI.INVALID_DOUBLE
    LATITUDE_INVALID = YAPI.INVALID_STRING
    LONGITUDE_INVALID = YAPI.INVALID_STRING
    DILUTION_INVALID = YAPI.INVALID_DOUBLE
    ALTITUDE_INVALID = YAPI.INVALID_DOUBLE
    GROUNDSPEED_INVALID = YAPI.INVALID_DOUBLE
    DIRECTION_INVALID = YAPI.INVALID_DOUBLE
    UNIXTIME_INVALID = YAPI.INVALID_LONG
    DATETIME_INVALID = YAPI.INVALID_STRING
    UTCOFFSET_INVALID = YAPI.INVALID_INT
    COMMAND_INVALID = YAPI.INVALID_STRING
    ISFIXED_FALSE = 0
    ISFIXED_TRUE = 1
    ISFIXED_INVALID = -1
    COORDSYSTEM_GPS_DMS = 0
    COORDSYSTEM_GPS_DM = 1
    COORDSYSTEM_GPS_D = 2
    COORDSYSTEM_INVALID = -1
    CONSTELLATION_GNSS = 0
    CONSTELLATION_GPS = 1
    CONSTELLATION_GLONASS = 2
    CONSTELLATION_GALILEO = 3
    CONSTELLATION_GPS_GLONASS = 4
    CONSTELLATION_GPS_GALILEO = 5
    CONSTELLATION_GLONASS_GALILEO = 6
    CONSTELLATION_INVALID = -1
    #--- (end of YGps definitions)

    def __init__(self, func):
        super(YGps, self).__init__(func)
        self._className = 'Gps'
        #--- (YGps attributes)
        self._callback = None
        self._isFixed = YGps.ISFIXED_INVALID
        self._satCount = YGps.SATCOUNT_INVALID
        self._satPerConst = YGps.SATPERCONST_INVALID
        self._gpsRefreshRate = YGps.GPSREFRESHRATE_INVALID
        self._coordSystem = YGps.COORDSYSTEM_INVALID
        self._constellation = YGps.CONSTELLATION_INVALID
        self._latitude = YGps.LATITUDE_INVALID
        self._longitude = YGps.LONGITUDE_INVALID
        self._dilution = YGps.DILUTION_INVALID
        self._altitude = YGps.ALTITUDE_INVALID
        self._groundSpeed = YGps.GROUNDSPEED_INVALID
        self._direction = YGps.DIRECTION_INVALID
        self._unixTime = YGps.UNIXTIME_INVALID
        self._dateTime = YGps.DATETIME_INVALID
        self._utcOffset = YGps.UTCOFFSET_INVALID
        self._command = YGps.COMMAND_INVALID
        #--- (end of YGps attributes)

    #--- (YGps implementation)
    def _parseAttr(self, json_val):
        if json_val.has("isFixed"):
            self._isFixed = (json_val.getInt("isFixed") > 0 if 1 else 0)
        if json_val.has("satCount"):
            self._satCount = json_val.getLong("satCount")
        if json_val.has("satPerConst"):
            self._satPerConst = json_val.getLong("satPerConst")
        if json_val.has("gpsRefreshRate"):
            self._gpsRefreshRate = round(json_val.getDouble("gpsRefreshRate") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("coordSystem"):
            self._coordSystem = json_val.getInt("coordSystem")
        if json_val.has("constellation"):
            self._constellation = json_val.getInt("constellation")
        if json_val.has("latitude"):
            self._latitude = json_val.getString("latitude")
        if json_val.has("longitude"):
            self._longitude = json_val.getString("longitude")
        if json_val.has("dilution"):
            self._dilution = round(json_val.getDouble("dilution") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("altitude"):
            self._altitude = round(json_val.getDouble("altitude") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("groundSpeed"):
            self._groundSpeed = round(json_val.getDouble("groundSpeed") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("direction"):
            self._direction = round(json_val.getDouble("direction") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("unixTime"):
            self._unixTime = json_val.getLong("unixTime")
        if json_val.has("dateTime"):
            self._dateTime = json_val.getString("dateTime")
        if json_val.has("utcOffset"):
            self._utcOffset = json_val.getInt("utcOffset")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YGps, self)._parseAttr(json_val)

    def get_isFixed(self):
        """
        Returns TRUE if the receiver has found enough satellites to work.

        @return either YGps.ISFIXED_FALSE or YGps.ISFIXED_TRUE, according to TRUE if the receiver has found
        enough satellites to work

        On failure, throws an exception or returns YGps.ISFIXED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.ISFIXED_INVALID
        res = self._isFixed
        return res

    def get_satCount(self):
        """
        Returns the total count of satellites used to compute GPS position.

        @return an integer corresponding to the total count of satellites used to compute GPS position

        On failure, throws an exception or returns YGps.SATCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.SATCOUNT_INVALID
        res = self._satCount
        return res

    def get_satPerConst(self):
        """
        Returns the count of visible satellites per constellation encoded
        on a 32 bit integer: bits 0..5: GPS satellites count,  bits 6..11 : Glonass, bits 12..17 : Galileo.
        this value is refreshed every 5 seconds only.

        @return an integer corresponding to the count of visible satellites per constellation encoded
                on a 32 bit integer: bits 0.

        On failure, throws an exception or returns YGps.SATPERCONST_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.SATPERCONST_INVALID
        res = self._satPerConst
        return res

    def get_gpsRefreshRate(self):
        """
        Returns effective GPS data refresh frequency.
        this value is refreshed every 5 seconds only.

        @return a floating point number corresponding to effective GPS data refresh frequency

        On failure, throws an exception or returns YGps.GPSREFRESHRATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.GPSREFRESHRATE_INVALID
        res = self._gpsRefreshRate
        return res

    def get_coordSystem(self):
        """
        Returns the representation system used for positioning data.

        @return a value among YGps.COORDSYSTEM_GPS_DMS, YGps.COORDSYSTEM_GPS_DM and YGps.COORDSYSTEM_GPS_D
        corresponding to the representation system used for positioning data

        On failure, throws an exception or returns YGps.COORDSYSTEM_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.COORDSYSTEM_INVALID
        res = self._coordSystem
        return res

    def set_coordSystem(self, newval):
        """
        Changes the representation system used for positioning data.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YGps.COORDSYSTEM_GPS_DMS, YGps.COORDSYSTEM_GPS_DM and
        YGps.COORDSYSTEM_GPS_D corresponding to the representation system used for positioning data

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("coordSystem", rest_val)

    def get_constellation(self):
        """
        Returns the the satellites constellation used to compute
        positioning data.

        @return a value among YGps.CONSTELLATION_GNSS, YGps.CONSTELLATION_GPS, YGps.CONSTELLATION_GLONASS,
        YGps.CONSTELLATION_GALILEO, YGps.CONSTELLATION_GPS_GLONASS, YGps.CONSTELLATION_GPS_GALILEO and
        YGps.CONSTELLATION_GLONASS_GALILEO corresponding to the the satellites constellation used to compute
                positioning data

        On failure, throws an exception or returns YGps.CONSTELLATION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.CONSTELLATION_INVALID
        res = self._constellation
        return res

    def set_constellation(self, newval):
        """
        Changes the satellites constellation used to compute
        positioning data. Possible  constellations are GNSS ( = all supported constellations),
        GPS, Glonass, Galileo , and the 3 possible pairs. This setting has  no effect on Yocto-GPS (V1).

        @param newval : a value among YGps.CONSTELLATION_GNSS, YGps.CONSTELLATION_GPS,
        YGps.CONSTELLATION_GLONASS, YGps.CONSTELLATION_GALILEO, YGps.CONSTELLATION_GPS_GLONASS,
        YGps.CONSTELLATION_GPS_GALILEO and YGps.CONSTELLATION_GLONASS_GALILEO corresponding to the
        satellites constellation used to compute
                positioning data

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("constellation", rest_val)

    def get_latitude(self):
        """
        Returns the current latitude.

        @return a string corresponding to the current latitude

        On failure, throws an exception or returns YGps.LATITUDE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.LATITUDE_INVALID
        res = self._latitude
        return res

    def get_longitude(self):
        """
        Returns the current longitude.

        @return a string corresponding to the current longitude

        On failure, throws an exception or returns YGps.LONGITUDE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.LONGITUDE_INVALID
        res = self._longitude
        return res

    def get_dilution(self):
        """
        Returns the current horizontal dilution of precision,
        the smaller that number is, the better .

        @return a floating point number corresponding to the current horizontal dilution of precision,
                the smaller that number is, the better

        On failure, throws an exception or returns YGps.DILUTION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.DILUTION_INVALID
        res = self._dilution
        return res

    def get_altitude(self):
        """
        Returns the current altitude. Beware:  GPS technology
        is very inaccurate regarding altitude.

        @return a floating point number corresponding to the current altitude

        On failure, throws an exception or returns YGps.ALTITUDE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.ALTITUDE_INVALID
        res = self._altitude
        return res

    def get_groundSpeed(self):
        """
        Returns the current ground speed in Km/h.

        @return a floating point number corresponding to the current ground speed in Km/h

        On failure, throws an exception or returns YGps.GROUNDSPEED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.GROUNDSPEED_INVALID
        res = self._groundSpeed
        return res

    def get_direction(self):
        """
        Returns the current move bearing in degrees, zero
        is the true (geographic) north.

        @return a floating point number corresponding to the current move bearing in degrees, zero
                is the true (geographic) north

        On failure, throws an exception or returns YGps.DIRECTION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.DIRECTION_INVALID
        res = self._direction
        return res

    def get_unixTime(self):
        """
        Returns the current time in Unix format (number of
        seconds elapsed since Jan 1st, 1970).

        @return an integer corresponding to the current time in Unix format (number of
                seconds elapsed since Jan 1st, 1970)

        On failure, throws an exception or returns YGps.UNIXTIME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.UNIXTIME_INVALID
        res = self._unixTime
        return res

    def get_dateTime(self):
        """
        Returns the current time in the form "YYYY/MM/DD hh:mm:ss".

        @return a string corresponding to the current time in the form "YYYY/MM/DD hh:mm:ss"

        On failure, throws an exception or returns YGps.DATETIME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.DATETIME_INVALID
        res = self._dateTime
        return res

    def get_utcOffset(self):
        """
        Returns the number of seconds between current time and UTC time (time zone).

        @return an integer corresponding to the number of seconds between current time and UTC time (time zone)

        On failure, throws an exception or returns YGps.UTCOFFSET_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.UTCOFFSET_INVALID
        res = self._utcOffset
        return res

    def set_utcOffset(self, newval):
        """
        Changes the number of seconds between current time and UTC time (time zone).
        The timezone is automatically rounded to the nearest multiple of 15 minutes.
        If current UTC time is known, the current time is automatically be updated according to the selected time zone.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the number of seconds between current time and UTC time (time zone)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("utcOffset", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGps.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindGps(func):
        """
        Retrieves a geolocalization module for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the geolocalization module is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YGps.isOnline() to test if the geolocalization module is
        indeed online at a given time. In case of ambiguity when looking for
        a geolocalization module by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the geolocalization module, for instance
                YGNSSMK2.gps.

        @return a YGps object allowing you to drive the geolocalization module.
        """
        # obj
        obj = YFunction._FindFromCache("Gps", func)
        if obj is None:
            obj = YGps(func)
            YFunction._AddToCache("Gps", func, obj)
        return obj

    def nextGps(self):
        """
        Continues the enumeration of geolocalization modules started using yFirstGps().
        Caution: You can't make any assumption about the returned geolocalization modules order.
        If you want to find a specific a geolocalization module, use Gps.findGps()
        and a hardwareID or a logical name.

        @return a pointer to a YGps object, corresponding to
                a geolocalization module currently online, or a None pointer
                if there are no more geolocalization modules to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YGps.FindGps(hwidRef.value)

#--- (end of YGps implementation)

#--- (YGps functions)

    @staticmethod
    def FirstGps():
        """
        Starts the enumeration of geolocalization modules currently accessible.
        Use the method YGps.nextGps() to iterate on
        next geolocalization modules.

        @return a pointer to a YGps object, corresponding to
                the first geolocalization module currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Gps", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YGps.FindGps(serialRef.value + "." + funcIdRef.value)

#--- (end of YGps functions)
