# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_audioout.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindAudioOut(), the high-level API for AudioOut functions
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


#--- (YAudioOut class start)
#noinspection PyProtectedMember
class YAudioOut(YFunction):
    """
    The YAudioOut class allows you to configure the volume of an audio output.

    """
    #--- (end of YAudioOut class start)
    #--- (YAudioOut return codes)
    #--- (end of YAudioOut return codes)
    #--- (YAudioOut dlldef)
    #--- (end of YAudioOut dlldef)
    #--- (YAudioOut yapiwrapper)
    #--- (end of YAudioOut yapiwrapper)
    #--- (YAudioOut definitions)
    VOLUME_INVALID = YAPI.INVALID_UINT
    VOLUMERANGE_INVALID = YAPI.INVALID_STRING
    SIGNAL_INVALID = YAPI.INVALID_INT
    NOSIGNALFOR_INVALID = YAPI.INVALID_INT
    MUTE_FALSE = 0
    MUTE_TRUE = 1
    MUTE_INVALID = -1
    #--- (end of YAudioOut definitions)

    def __init__(self, func):
        super(YAudioOut, self).__init__(func)
        self._className = 'AudioOut'
        #--- (YAudioOut attributes)
        self._callback = None
        self._volume = YAudioOut.VOLUME_INVALID
        self._mute = YAudioOut.MUTE_INVALID
        self._volumeRange = YAudioOut.VOLUMERANGE_INVALID
        self._signal = YAudioOut.SIGNAL_INVALID
        self._noSignalFor = YAudioOut.NOSIGNALFOR_INVALID
        #--- (end of YAudioOut attributes)

    #--- (YAudioOut implementation)
    def _parseAttr(self, json_val):
        if json_val.has("volume"):
            self._volume = json_val.getInt("volume")
        if json_val.has("mute"):
            self._mute = (json_val.getInt("mute") > 0 if 1 else 0)
        if json_val.has("volumeRange"):
            self._volumeRange = json_val.getString("volumeRange")
        if json_val.has("signal"):
            self._signal = json_val.getInt("signal")
        if json_val.has("noSignalFor"):
            self._noSignalFor = json_val.getInt("noSignalFor")
        super(YAudioOut, self)._parseAttr(json_val)

    def get_volume(self):
        """
        Returns audio output volume, in per cents.

        @return an integer corresponding to audio output volume, in per cents

        On failure, throws an exception or returns YAudioOut.VOLUME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioOut.VOLUME_INVALID
        res = self._volume
        return res

    def set_volume(self, newval):
        """
        Changes audio output volume, in per cents.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to audio output volume, in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("volume", rest_val)

    def get_mute(self):
        """
        Returns the state of the mute function.

        @return either YAudioOut.MUTE_FALSE or YAudioOut.MUTE_TRUE, according to the state of the mute function

        On failure, throws an exception or returns YAudioOut.MUTE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioOut.MUTE_INVALID
        res = self._mute
        return res

    def set_mute(self, newval):
        """
        Changes the state of the mute function. Remember to call the matching module
        saveToFlash() method to save the setting permanently.

        @param newval : either YAudioOut.MUTE_FALSE or YAudioOut.MUTE_TRUE, according to the state of the mute function

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("mute", rest_val)

    def get_volumeRange(self):
        """
        Returns the supported volume range. The low value of the
        range corresponds to the minimal audible value. To
        completely mute the sound, use set_mute()
        instead of the set_volume().

        @return a string corresponding to the supported volume range

        On failure, throws an exception or returns YAudioOut.VOLUMERANGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioOut.VOLUMERANGE_INVALID
        res = self._volumeRange
        return res

    def get_signal(self):
        """
        Returns the detected output current level.

        @return an integer corresponding to the detected output current level

        On failure, throws an exception or returns YAudioOut.SIGNAL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioOut.SIGNAL_INVALID
        res = self._signal
        return res

    def get_noSignalFor(self):
        """
        Returns the number of seconds elapsed without detecting a signal.

        @return an integer corresponding to the number of seconds elapsed without detecting a signal

        On failure, throws an exception or returns YAudioOut.NOSIGNALFOR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YAudioOut.NOSIGNALFOR_INVALID
        res = self._noSignalFor
        return res

    @staticmethod
    def FindAudioOut(func):
        """
        Retrieves an audio output for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the audio output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YAudioOut.isOnline() to test if the audio output is
        indeed online at a given time. In case of ambiguity when looking for
        an audio output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the audio output, for instance
                MyDevice.audioOut1.

        @return a YAudioOut object allowing you to drive the audio output.
        """
        # obj
        obj = YFunction._FindFromCache("AudioOut", func)
        if obj is None:
            obj = YAudioOut(func)
            YFunction._AddToCache("AudioOut", func, obj)
        return obj

    def nextAudioOut(self):
        """
        Continues the enumeration of audio outputs started using yFirstAudioOut().
        Caution: You can't make any assumption about the returned audio outputs order.
        If you want to find a specific an audio output, use AudioOut.findAudioOut()
        and a hardwareID or a logical name.

        @return a pointer to a YAudioOut object, corresponding to
                an audio output currently online, or a None pointer
                if there are no more audio outputs to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YAudioOut.FindAudioOut(hwidRef.value)

#--- (end of YAudioOut implementation)

#--- (YAudioOut functions)

    @staticmethod
    def FirstAudioOut():
        """
        Starts the enumeration of audio outputs currently accessible.
        Use the method YAudioOut.nextAudioOut() to iterate on
        next audio outputs.

        @return a pointer to a YAudioOut object, corresponding to
                the first audio output currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("AudioOut", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YAudioOut.FindAudioOut(serialRef.value + "." + funcIdRef.value)

#--- (end of YAudioOut functions)
