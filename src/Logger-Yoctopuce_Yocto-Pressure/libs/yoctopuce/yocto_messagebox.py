# -*- coding: utf-8 -*-
#*********************************************************************
#*
#* $Id: yocto_messagebox.py 38913 2019-12-20 18:59:49Z mvuilleu $
#*
#* Implements yFindMessageBox(), the high-level API for MessageBox functions
#*
#* - - - - - - - - - License information: - - - - - - - - -
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (generated code: YSms class start)
#noinspection PyProtectedMember
class YSms(object):
    """
    YSms objects are used to describe an SMS message, received or to be sent.
    These objects are used in particular in conjunction with the YMessageBox class.

    """
    #--- (end of generated code: YSms class start)
    #--- (generated code: YSms return codes)
    #--- (end of generated code: YSms return codes)
    #--- (generated code: YSms dlldef)
    #--- (end of generated code: YSms dlldef)
    #--- (generated code: YSms definitions)
    #--- (end of generated code: YSms definitions)

    def __init__(self, obj_mbox):
        #--- (generated code: YSms attributes)
        self._mbox = None
        self._slot = 0
        self._deliv = 0
        self._smsc = ''
        self._mref = 0
        self._orig = ''
        self._dest = ''
        self._pid = 0
        self._alphab = 0
        self._mclass = 0
        self._stamp = ''
        self._udh = ''
        self._udata = ''
        self._npdu = 0
        self._pdu = ''
        self._parts = []
        self._aggSig = ''
        self._aggIdx = 0
        self._aggCnt = 0
        #--- (end of generated code: YSms attributes)
        self._mbox = obj_mbox

#--- (generated code: YSms implementation)
    def get_slot(self):
        return self._slot

    def get_smsc(self):
        return self._smsc

    def get_msgRef(self):
        return self._mref

    def get_sender(self):
        return self._orig

    def get_recipient(self):
        return self._dest

    def get_protocolId(self):
        return self._pid

    def isReceived(self):
        return self._deliv

    def get_alphabet(self):
        return self._alphab

    def get_msgClass(self):
        if ((self._mclass) & (16)) == 0:
            return -1
        return ((self._mclass) & (3))

    def get_dcs(self):
        return ((self._mclass) | ((((self._alphab) << (2)))))

    def get_timestamp(self):
        return self._stamp

    def get_userDataHeader(self):
        return self._udh

    def get_userData(self):
        return self._udata

    def get_textData(self):
        """
        Returns the content of the message.

        @return  a string with the content of the message.
        """
        # isolatin
        # isosize
        # i
        if self._alphab == 0:
            # // using GSM standard 7-bit alphabet
            return self._mbox.gsm2str(self._udata)
        if self._alphab == 2:
            # // using UCS-2 alphabet
            isosize = ((len(self._udata)) >> (1))
            isolatin = bytearray(isosize)
            i = 0
            while i < isosize:
                isolatin[i] = YGetByte(self._udata, 2*i+1)
                i = i + 1
            return YByte2String(isolatin)
        # // default: convert 8 bit to string as-is
        return YByte2String(self._udata)

    def get_unicodeData(self):
        res = []
        # unisize
        # unival
        # i
        if self._alphab == 0:
            # // using GSM standard 7-bit alphabet
            return self._mbox.gsm2unicode(self._udata)
        if self._alphab == 2:
            # // using UCS-2 alphabet
            unisize = ((len(self._udata)) >> (1))
            del res[:]
            i = 0
            while i < unisize:
                unival = 256*YGetByte(self._udata, 2*i)+YGetByte(self._udata, 2*i+1)
                res.append(unival)
                i = i + 1
        else:
            # // return straight 8-bit values
            unisize = len(self._udata)
            del res[:]
            i = 0
            while i < unisize:
                res.append(YGetByte(self._udata, i)+0)
                i = i + 1

        return res

    def get_partCount(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._npdu

    def get_pdu(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._pdu

    def get_parts(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._parts

    def get_concatSignature(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._aggSig

    def get_concatIndex(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._aggIdx

    def get_concatCount(self):
        if self._npdu == 0:
            self.generatePdu()
        return self._aggCnt

    def set_slot(self, val):
        self._slot = val
        return YAPI.SUCCESS

    def set_received(self, val):
        self._deliv = val
        return YAPI.SUCCESS

    def set_smsc(self, val):
        self._smsc = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_msgRef(self, val):
        self._mref = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_sender(self, val):
        self._orig = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_recipient(self, val):
        self._dest = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_protocolId(self, val):
        self._pid = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_alphabet(self, val):
        self._alphab = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_msgClass(self, val):
        if val == -1:
            self._mclass = 0
        else:
            self._mclass = 16+val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_dcs(self, val):
        self._alphab = (((((val) >> (2)))) & (3))
        self._mclass = ((val) & (16+3))
        self._npdu = 0
        return YAPI.SUCCESS

    def set_timestamp(self, val):
        self._stamp = val
        self._npdu = 0
        return YAPI.SUCCESS

    def set_userDataHeader(self, val):
        self._udh = val
        self._npdu = 0
        self.parseUserDataHeader()
        return YAPI.SUCCESS

    def set_userData(self, val):
        self._udata = val
        self._npdu = 0
        return YAPI.SUCCESS

    def convertToUnicode(self):
        ucs2 = []
        # udatalen
        # i
        # uni
        if self._alphab == 2:
            return YAPI.SUCCESS
        if self._alphab == 0:
            ucs2 = self._mbox.gsm2unicode(self._udata)
        else:
            udatalen = len(self._udata)
            del ucs2[:]
            i = 0
            while i < udatalen:
                uni = YGetByte(self._udata, i)
                ucs2.append(uni)
                i = i + 1
        self._alphab = 2
        self._udata = bytearray(0)
        self.addUnicodeData(ucs2)
        return YAPI.SUCCESS

    def addText(self, val):
        """
        Add a regular text to the SMS. This function support messages
        of more than 160 characters. ISO-latin accented characters
        are supported. For messages with special unicode characters such as asian
        characters and emoticons, use the  addUnicodeData method.

        @param val : the text to be sent in the message

        @return YAPI.SUCCESS when the call succeeds.
        """
        # udata
        # udatalen
        # newdata
        # newdatalen
        # i
        if len(val) == 0:
            return YAPI.SUCCESS
        if self._alphab == 0:
            # // Try to append using GSM 7-bit alphabet
            newdata = self._mbox.str2gsm(val)
            newdatalen = len(newdata)
            if newdatalen == 0:
                # // 7-bit not possible, switch to unicode
                self.convertToUnicode()
                newdata = YString2Byte(val)
                newdatalen = len(newdata)
        else:
            newdata = YString2Byte(val)
            newdatalen = len(newdata)
        udatalen = len(self._udata)
        if self._alphab == 2:
            # // Append in unicode directly
            udata = bytearray(udatalen + 2*newdatalen)
            i = 0
            while i < udatalen:
                udata[i] = YGetByte(self._udata, i)
                i = i + 1
            i = 0
            while i < newdatalen:
                udata[udatalen+1] = YGetByte(newdata, i)
                udatalen = udatalen + 2
                i = i + 1
        else:
            # // Append binary buffers
            udata = bytearray(udatalen+newdatalen)
            i = 0
            while i < udatalen:
                udata[i] = YGetByte(self._udata, i)
                i = i + 1
            i = 0
            while i < newdatalen:
                udata[udatalen] = YGetByte(newdata, i)
                udatalen = udatalen + 1
                i = i + 1
        return self.set_userData(udata)

    def addUnicodeData(self, val):
        """
        Add a unicode text to the SMS. This function support messages
        of more than 160 characters, using SMS concatenation.

        @param val : an array of special unicode characters

        @return YAPI.SUCCESS when the call succeeds.
        """
        # arrlen
        # newdatalen
        # i
        # uni
        # udata
        # udatalen
        # surrogate
        if self._alphab != 2:
            self.convertToUnicode()
        # // compute number of 16-bit code units
        arrlen = len(val)
        newdatalen = arrlen
        i = 0
        while i < arrlen:
            uni = val[i]
            if uni > 65535:
                newdatalen = newdatalen + 1
            i = i + 1
        # // now build utf-16 buffer
        udatalen = len(self._udata)
        udata = bytearray(udatalen+2*newdatalen)
        i = 0
        while i < udatalen:
            udata[i] = YGetByte(self._udata, i)
            i = i + 1
        i = 0
        while i < arrlen:
            uni = val[i]
            if uni >= 65536:
                surrogate = uni - 65536
                uni = (((((surrogate) >> (10))) & (1023))) + 55296
                udata[udatalen] = ((uni) >> (8))
                udata[udatalen+1] = ((uni) & (255))
                udatalen = udatalen + 2
                uni = (((surrogate) & (1023))) + 56320
            udata[udatalen] = ((uni) >> (8))
            udata[udatalen+1] = ((uni) & (255))
            udatalen = udatalen + 2
            i = i + 1
        return self.set_userData(udata)

    def set_pdu(self, pdu):
        self._pdu = pdu
        self._npdu = 1
        return self.parsePdu(pdu)

    def set_parts(self, parts):
        sorted = []
        # partno
        # initpartno
        # i
        # retcode
        # totsize
        # subsms
        # subdata
        # res
        self._npdu = len(parts)
        if self._npdu == 0:
            return YAPI.INVALID_ARGUMENT
        del sorted[:]
        partno = 0
        while partno < self._npdu:
            initpartno = partno
            i = 0
            while i < self._npdu:
                subsms = parts[i]
                if subsms.get_concatIndex() == partno:
                    sorted.append(subsms)
                    partno = partno + 1
                i = i + 1
            if initpartno == partno:
                partno = partno + 1

        self._parts = sorted
        self._npdu = len(sorted)
        # // inherit header fields from first part
        subsms = self._parts[0]
        retcode = self.parsePdu(subsms.get_pdu())
        if retcode != YAPI.SUCCESS:
            return retcode
        # // concatenate user data from all parts
        totsize = 0
        partno = 0
        while partno < len(self._parts):
            subsms = self._parts[partno]
            subdata = subsms.get_userData()
            totsize = totsize + len(subdata)
            partno = partno + 1
        res = bytearray(totsize)
        totsize = 0
        partno = 0
        while partno < len(self._parts):
            subsms = self._parts[partno]
            subdata = subsms.get_userData()
            i = 0
            while i < len(subdata):
                res[totsize] = YGetByte(subdata, i)
                totsize = totsize + 1
                i = i + 1
            partno = partno + 1
        self._udata = res
        return YAPI.SUCCESS

    def encodeAddress(self, addr):
        # bytes
        # srclen
        # numlen
        # i
        # val
        # digit
        # res
        bytes = YString2Byte(addr)
        srclen = len(bytes)
        numlen = 0
        i = 0
        while i < srclen:
            val = YGetByte(bytes, i)
            if (val >= 48) and (val < 58):
                numlen = numlen + 1
            i = i + 1
        if numlen == 0:
            res = bytearray(1)
            res[0] = 0
            return res
        res = bytearray(2+((numlen+1) >> (1)))
        res[0] = numlen
        if YGetByte(bytes, 0) == 43:
            res[1] = 145
        else:
            res[1] = 129
        numlen = 4
        digit = 0
        i = 0
        while i < srclen:
            val = YGetByte(bytes, i)
            if (val >= 48) and (val < 58):
                if ((numlen) & (1)) == 0:
                    digit = val - 48
                else:
                    res[((numlen) >> (1))] = digit + 16*(val-48)
                numlen = numlen + 1
            i = i + 1
        # // pad with F if needed
        if ((numlen) & (1)) != 0:
            res[((numlen) >> (1))] = digit + 240
        return res

    def decodeAddress(self, addr, ofs, siz):
        # addrType
        # gsm7
        # res
        # i
        # rpos
        # carry
        # nbits
        # byt
        if siz == 0:
            return ""
        res = ""
        addrType = ((YGetByte(addr, ofs)) & (112))
        if addrType == 80:
            # // alphanumeric number
            siz = int((4*siz) / (7))
            gsm7 = bytearray(siz)
            rpos = 1
            carry = 0
            nbits = 0
            i = 0
            while i < siz:
                if nbits == 7:
                    gsm7[i] = carry
                    carry = 0
                    nbits = 0
                else:
                    byt = YGetByte(addr, ofs+rpos)
                    rpos = rpos + 1
                    gsm7[i] = ((carry) | ((((((byt) << (nbits)))) & (127))))
                    carry = ((byt) >> ((7 - nbits)))
                    nbits = nbits + 1
                i = i + 1
            return self._mbox.gsm2str(gsm7)
        else:
            # // standard phone number
            if addrType == 16:
                res = "+"
            siz = (((siz+1)) >> (1))
            i = 0
            while i < siz:
                byt = YGetByte(addr, ofs+i+1)
                res = "" + res + "" + ("%x" % ((byt) & (15))) + "" + ("%x" % ((byt) >> (4)))
                i = i + 1
            # // remove padding digit if needed
            if ((YGetByte(addr, ofs+siz)) >> (4)) == 15:
                res = (res)[0: 0 + len(res)-1]
            return res

    def encodeTimeStamp(self, exp):
        # explen
        # i
        # res
        # n
        # expasc
        # v1
        # v2
        explen = len(exp)
        if explen == 0:
            res = bytearray(0)
            return res
        if (exp)[0: 0 + 1] == "+":
            n = YAPI._atoi((exp)[1: 1 + explen-1])
            res = bytearray(1)
            if n > 30*86400:
                n = 192+int(((n+6*86400)) / ((7*86400)))
            else:
                if n > 86400:
                    n = 166+int(((n+86399)) / (86400))
                else:
                    if n > 43200:
                        n = 143+int(((n-43200+1799)) / (1800))
                    else:
                        n = -1+int(((n+299)) / (300))
            if n < 0:
                n = 0
            res[0] = n
            return res
        if (exp)[4: 4 + 1] == "-" or (exp)[4: 4 + 1] == "/":
            # // ignore century
            exp = (exp)[2: 2 + explen-2]
            explen = len(exp)
        expasc = YString2Byte(exp)
        res = bytearray(7)
        n = 0
        i = 0
        while (i+1 < explen) and (n < 7):
            v1 = YGetByte(expasc, i)
            if (v1 >= 48) and (v1 < 58):
                v2 = YGetByte(expasc, i+1)
                if (v2 >= 48) and (v2 < 58):
                    v1 = v1 - 48
                    v2 = v2 - 48
                    res[n] = (((v2) << (4))) + v1
                    n = n + 1
                    i = i + 1
            i = i + 1
        while n < 7:
            res[n] = 0
            n = n + 1
        if i+2 < explen:
            # // convert for timezone in cleartext ISO format +/-nn:nn
            v1 = YGetByte(expasc, i-3)
            v2 = YGetByte(expasc, i)
            if ((v1 == 43) or (v1 == 45)) and (v2 == 58):
                v1 = YGetByte(expasc, i+1)
                v2 = YGetByte(expasc, i+2)
                if (v1 >= 48) and (v1 < 58) and (v1 >= 48) and (v1 < 58):
                    v1 = int(((10*(v1 - 48)+(v2 - 48))) / (15))
                    n = n - 1
                    v2 = 4 * YGetByte(res, n) + v1
                    if YGetByte(expasc, i-3) == 45:
                        v2 += 128
                    res[n] = v2
        return res

    def decodeTimeStamp(self, exp, ofs, siz):
        # n
        # res
        # i
        # byt
        # sign
        # hh
        # ss
        if siz < 1:
            return ""
        if siz == 1:
            n = YGetByte(exp, ofs)
            if n < 144:
                n = n * 300
            else:
                if n < 168:
                    n = (n-143) * 1800
                else:
                    if n < 197:
                        n = (n-166) * 86400
                    else:
                        n = (n-192) * 7 * 86400
            return "+" + str(int(n))
        res = "20"
        i = 0
        while (i < siz) and (i < 6):
            byt = YGetByte(exp, ofs+i)
            res = "" + res + "" + ("%x" % ((byt) & (15))) + "" + ("%x" % ((byt) >> (4)))
            if i < 3:
                if i < 2:
                    res = "" + res + "-"
                else:
                    res = "" + res + " "
            else:
                if i < 5:
                    res = "" + res + ":"
            i = i + 1
        if siz == 7:
            byt = YGetByte(exp, ofs+i)
            sign = "+"
            if ((byt) & (8)) != 0:
                byt = byt - 8
                sign = "-"
            byt = (10*(((byt) & (15)))) + (((byt) >> (4)))
            hh = "" + str(int(((byt) >> (2))))
            ss = "" + str(int(15*(((byt) & (3)))))
            if len(hh)<2:
                hh = "0" + hh
            if len(ss)<2:
                ss = "0" + ss
            res = "" + res + "" + sign + "" + hh + ":" + ss
        return res

    def udataSize(self):
        # res
        # udhsize
        udhsize = len(self._udh)
        res = len(self._udata)
        if self._alphab == 0:
            if udhsize > 0:
                res = res + int(((8 + 8*udhsize + 6)) / (7))
            res = int(((res * 7 + 7)) / (8))
        else:
            if udhsize > 0:
                res = res + 1 + udhsize
        return res

    def encodeUserData(self):
        # udsize
        # udlen
        # udhsize
        # udhlen
        # res
        # i
        # wpos
        # carry
        # nbits
        # thi_b
        # // nbits = number of bits in carry
        udsize = self.udataSize()
        udhsize = len(self._udh)
        udlen = len(self._udata)
        res = bytearray(1+udsize)
        udhlen = 0
        nbits = 0
        carry = 0
        # // 1. Encode UDL
        if self._alphab == 0:
            # // 7-bit encoding
            if udhsize > 0:
                udhlen = int(((8 + 8*udhsize + 6)) / (7))
                nbits = 7*udhlen - 8 - 8*udhsize
            res[0] = udhlen+udlen
        else:
            # // 8-bit encoding
            res[0] = udsize
        # // 2. Encode UDHL and UDL
        wpos = 1
        if udhsize > 0:
            res[wpos] = udhsize
            wpos = wpos + 1
            i = 0
            while i < udhsize:
                res[wpos] = YGetByte(self._udh, i)
                wpos = wpos + 1
                i = i + 1
        # // 3. Encode UD
        if self._alphab == 0:
            # // 7-bit encoding
            i = 0
            while i < udlen:
                if nbits == 0:
                    carry = YGetByte(self._udata, i)
                    nbits = 7
                else:
                    thi_b = YGetByte(self._udata, i)
                    res[wpos] = ((carry) | ((((((thi_b) << (nbits)))) & (255))))
                    wpos = wpos + 1
                    nbits = nbits - 1
                    carry = ((thi_b) >> ((7 - nbits)))
                i = i + 1
            if nbits > 0:
                res[wpos] = carry
        else:
            # // 8-bit encoding
            i = 0
            while i < udlen:
                res[wpos] = YGetByte(self._udata, i)
                wpos = wpos + 1
                i = i + 1
        return res

    def generateParts(self):
        # udhsize
        # udlen
        # mss
        # partno
        # partlen
        # newud
        # newudh
        # newpdu
        # i
        # wpos
        udhsize = len(self._udh)
        udlen = len(self._udata)
        mss = 140 - 1 - 5 - udhsize
        if self._alphab == 0:
            mss = int(((mss * 8 - 6)) / (7))
        self._npdu = int(((udlen+mss-1)) / (mss))
        del self._parts[:]
        partno = 0
        wpos = 0
        while wpos < udlen:
            partno = partno + 1
            newudh = bytearray(5+udhsize)
            newudh[0] = 0
            # // IEI: concatenated message
            newudh[1] = 3
            # // IEDL: 3 bytes
            newudh[2] = self._mref
            newudh[3] = self._npdu
            newudh[4] = partno
            i = 0
            while i < udhsize:
                newudh[5+i] = YGetByte(self._udh, i)
                i = i + 1
            if wpos+mss < udlen:
                partlen = mss
            else:
                partlen = udlen-wpos
            newud = bytearray(partlen)
            i = 0
            while i < partlen:
                newud[i] = YGetByte(self._udata, wpos)
                wpos = wpos + 1
                i = i + 1
            newpdu = YSms(self._mbox)
            newpdu.set_received(self.isReceived())
            newpdu.set_smsc(self.get_smsc())
            newpdu.set_msgRef(self.get_msgRef())
            newpdu.set_sender(self.get_sender())
            newpdu.set_recipient(self.get_recipient())
            newpdu.set_protocolId(self.get_protocolId())
            newpdu.set_dcs(self.get_dcs())
            newpdu.set_timestamp(self.get_timestamp())
            newpdu.set_userDataHeader(newudh)
            newpdu.set_userData(newud)
            self._parts.append(newpdu)
        return YAPI.SUCCESS

    def generatePdu(self):
        # sca
        # hdr
        # addr
        # stamp
        # udata
        # pdutyp
        # pdulen
        # i
        # // Determine if the message can fit within a single PDU
        del self._parts[:]
        if self.udataSize() > 140:
            # // multiple PDU are needed
            self._pdu = bytearray(0)
            return self.generateParts()
        sca = self.encodeAddress(self._smsc)
        if len(sca) > 0:
            sca[0] = len(sca)-1
        stamp = self.encodeTimeStamp(self._stamp)
        udata = self.encodeUserData()
        if self._deliv:
            addr = self.encodeAddress(self._orig)
            hdr = bytearray(1)
            pdutyp = 0
        else:
            addr = self.encodeAddress(self._dest)
            self._mref = self._mbox.nextMsgRef()
            hdr = bytearray(2)
            hdr[1] = self._mref
            pdutyp = 1
            if len(stamp) > 0:
                pdutyp = pdutyp + 16
            if len(stamp) == 7:
                pdutyp = pdutyp + 8
        if len(self._udh) > 0:
            pdutyp = pdutyp + 64
        hdr[0] = pdutyp
        pdulen = len(sca)+len(hdr)+len(addr)+2+len(stamp)+len(udata)
        self._pdu = bytearray(pdulen)
        pdulen = 0
        i = 0
        while i < len(sca):
            self._pdu[pdulen] = YGetByte(sca, i)
            pdulen = pdulen + 1
            i = i + 1
        i = 0
        while i < len(hdr):
            self._pdu[pdulen] = YGetByte(hdr, i)
            pdulen = pdulen + 1
            i = i + 1
        i = 0
        while i < len(addr):
            self._pdu[pdulen] = YGetByte(addr, i)
            pdulen = pdulen + 1
            i = i + 1
        self._pdu[pdulen] = self._pid
        pdulen = pdulen + 1
        self._pdu[pdulen] = self.get_dcs()
        pdulen = pdulen + 1
        i = 0
        while i < len(stamp):
            self._pdu[pdulen] = YGetByte(stamp, i)
            pdulen = pdulen + 1
            i = i + 1
        i = 0
        while i < len(udata):
            self._pdu[pdulen] = YGetByte(udata, i)
            pdulen = pdulen + 1
            i = i + 1
        self._npdu = 1
        return YAPI.SUCCESS

    def parseUserDataHeader(self):
        # udhlen
        # i
        # iei
        # ielen
        # sig
        self._aggSig = ""
        self._aggIdx = 0
        self._aggCnt = 0
        udhlen = len(self._udh)
        i = 0
        while i+1 < udhlen:
            iei = YGetByte(self._udh, i)
            ielen = YGetByte(self._udh, i+1)
            i = i + 2
            if i + ielen <= udhlen:
                if (iei == 0) and (ielen == 3):
                    # // concatenated SMS, 8-bit ref
                    sig = "" + self._orig + "-" + self._dest + "-" + ("%02x" % self._mref) + "-" + ("%02x" % YGetByte(self._udh, i))
                    self._aggSig = sig
                    self._aggCnt = YGetByte(self._udh, i+1)
                    self._aggIdx = YGetByte(self._udh, i+2)
                if (iei == 8) and (ielen == 4):
                    # // concatenated SMS, 16-bit ref
                    sig = "" + self._orig + "-" + self._dest + "-" + ("%02x" % self._mref) + "-" + ("%02x" % YGetByte(self._udh, i)) + "" + ("%02x" % YGetByte(self._udh, i+1))
                    self._aggSig = sig
                    self._aggCnt = YGetByte(self._udh, i+2)
                    self._aggIdx = YGetByte(self._udh, i+3)
            i = i + ielen
        return YAPI.SUCCESS

    def parsePdu(self, pdu):
        # rpos
        # addrlen
        # pdutyp
        # tslen
        # dcs
        # udlen
        # udhsize
        # udhlen
        # i
        # carry
        # nbits
        # thi_b
        self._pdu = pdu
        self._npdu = 1
        # // parse meta-data
        self._smsc = self.decodeAddress(pdu, 1, 2*(YGetByte(pdu, 0)-1))
        rpos = 1+YGetByte(pdu, 0)
        pdutyp = YGetByte(pdu, rpos)
        rpos = rpos + 1
        self._deliv = (((pdutyp) & (3)) == 0)
        if self._deliv:
            addrlen = YGetByte(pdu, rpos)
            rpos = rpos + 1
            self._orig = self.decodeAddress(pdu, rpos, addrlen)
            self._dest = ""
            tslen = 7
        else:
            self._mref = YGetByte(pdu, rpos)
            rpos = rpos + 1
            addrlen = YGetByte(pdu, rpos)
            rpos = rpos + 1
            self._dest = self.decodeAddress(pdu, rpos, addrlen)
            self._orig = ""
            if (((pdutyp) & (16))) != 0:
                if (((pdutyp) & (8))) != 0:
                    tslen = 7
                else:
                    tslen= 1
            else:
                tslen = 0
        rpos = rpos + ((((addrlen+3)) >> (1)))
        self._pid = YGetByte(pdu, rpos)
        rpos = rpos + 1
        dcs = YGetByte(pdu, rpos)
        rpos = rpos + 1
        self._alphab = (((((dcs) >> (2)))) & (3))
        self._mclass = ((dcs) & (16+3))
        self._stamp = self.decodeTimeStamp(pdu, rpos, tslen)
        rpos = rpos + tslen
        # // parse user data (including udh)
        nbits = 0
        carry = 0
        udlen = YGetByte(pdu, rpos)
        rpos = rpos + 1
        if ((pdutyp) & (64)) != 0:
            udhsize = YGetByte(pdu, rpos)
            rpos = rpos + 1
            self._udh = bytearray(udhsize)
            i = 0
            while i < udhsize:
                self._udh[i] = YGetByte(pdu, rpos)
                rpos = rpos + 1
                i = i + 1
            if self._alphab == 0:
                # // 7-bit encoding
                udhlen = int(((8 + 8*udhsize + 6)) / (7))
                nbits = 7*udhlen - 8 - 8*udhsize
                if nbits > 0:
                    thi_b = YGetByte(pdu, rpos)
                    rpos = rpos + 1
                    carry = ((thi_b) >> (nbits))
                    nbits = 8 - nbits
            else:
                # // byte encoding
                udhlen = 1+udhsize
            udlen = udlen - udhlen
        else:
            udhsize = 0
            self._udh = bytearray(0)
        self._udata = bytearray(udlen)
        if self._alphab == 0:
            # // 7-bit encoding
            i = 0
            while i < udlen:
                if nbits == 7:
                    self._udata[i] = carry
                    carry = 0
                    nbits = 0
                else:
                    thi_b = YGetByte(pdu, rpos)
                    rpos = rpos + 1
                    self._udata[i] = ((carry) | ((((((thi_b) << (nbits)))) & (127))))
                    carry = ((thi_b) >> ((7 - nbits)))
                    nbits = nbits + 1
                i = i + 1
        else:
            # // 8-bit encoding
            i = 0
            while i < udlen:
                self._udata[i] = YGetByte(pdu, rpos)
                rpos = rpos + 1
                i = i + 1
        self.parseUserDataHeader()
        return YAPI.SUCCESS

    def send(self):
        """
        Sends the SMS to the recipient. Messages of more than 160 characters are supported
        using SMS concatenation.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # i
        # retcode
        # pdu

        if self._npdu == 0:
            self.generatePdu()
        if self._npdu == 1:
            return self._mbox._upload("sendSMS", self._pdu)
        retcode = YAPI.SUCCESS
        i = 0
        while (i < self._npdu) and (retcode == YAPI.SUCCESS):
            pdu = self._parts[i]
            retcode= pdu.send()
            i = i + 1
        return retcode

    def deleteFromSIM(self):
        # i
        # retcode
        # pdu

        if self._slot > 0:
            return self._mbox.clearSIMSlot(self._slot)
        retcode = YAPI.SUCCESS
        i = 0
        while (i < self._npdu) and (retcode == YAPI.SUCCESS):
            pdu = self._parts[i]
            retcode= pdu.deleteFromSIM()
            i = i + 1
        return retcode

#--- (end of generated code: YSms implementation)

#--- (generated code: YSms functions)
#--- (end of generated code: YSms functions)


#--- (generated code: YMessageBox class start)
#noinspection PyProtectedMember
class YMessageBox(YFunction):
    """
    The YMessageBox class provides SMS sending and receiving capability for
    GSM-enabled Yoctopuce devices.

    """
    #--- (end of generated code: YMessageBox class start)
    #--- (generated code: YMessageBox return codes)
    #--- (end of generated code: YMessageBox return codes)
    #--- (generated code: YMessageBox dlldef)
    #--- (end of generated code: YMessageBox dlldef)
    #--- (generated code: YMessageBox definitions)
    SLOTSINUSE_INVALID = YAPI.INVALID_UINT
    SLOTSCOUNT_INVALID = YAPI.INVALID_UINT
    SLOTSBITMAP_INVALID = YAPI.INVALID_STRING
    PDUSENT_INVALID = YAPI.INVALID_UINT
    PDURECEIVED_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    #--- (end of generated code: YMessageBox definitions)

    def __init__(self, func):
        super(YMessageBox, self).__init__(func)
        self._className = 'MessageBox'
        #--- (generated code: YMessageBox attributes)
        self._callback = None
        self._slotsInUse = YMessageBox.SLOTSINUSE_INVALID
        self._slotsCount = YMessageBox.SLOTSCOUNT_INVALID
        self._slotsBitmap = YMessageBox.SLOTSBITMAP_INVALID
        self._pduSent = YMessageBox.PDUSENT_INVALID
        self._pduReceived = YMessageBox.PDURECEIVED_INVALID
        self._command = YMessageBox.COMMAND_INVALID
        self._nextMsgRef = 0
        self._prevBitmapStr = ''
        self._pdus = []
        self._messages = []
        self._gsm2unicodeReady = 0
        self._gsm2unicode = []
        self._iso2gsm = ''
        #--- (end of generated code: YMessageBox attributes)

    #--- (generated code: YMessageBox implementation)
    def _parseAttr(self, json_val):
        if json_val.has("slotsInUse"):
            self._slotsInUse = json_val.getInt("slotsInUse")
        if json_val.has("slotsCount"):
            self._slotsCount = json_val.getInt("slotsCount")
        if json_val.has("slotsBitmap"):
            self._slotsBitmap = json_val.getString("slotsBitmap")
        if json_val.has("pduSent"):
            self._pduSent = json_val.getInt("pduSent")
        if json_val.has("pduReceived"):
            self._pduReceived = json_val.getInt("pduReceived")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YMessageBox, self)._parseAttr(json_val)

    def get_slotsInUse(self):
        """
        Returns the number of message storage slots currently in use.

        @return an integer corresponding to the number of message storage slots currently in use

        On failure, throws an exception or returns YMessageBox.SLOTSINUSE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.SLOTSINUSE_INVALID
        res = self._slotsInUse
        return res

    def get_slotsCount(self):
        """
        Returns the total number of message storage slots on the SIM card.

        @return an integer corresponding to the total number of message storage slots on the SIM card

        On failure, throws an exception or returns YMessageBox.SLOTSCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.SLOTSCOUNT_INVALID
        res = self._slotsCount
        return res

    def get_slotsBitmap(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.SLOTSBITMAP_INVALID
        res = self._slotsBitmap
        return res

    def get_pduSent(self):
        """
        Returns the number of SMS units sent so far.

        @return an integer corresponding to the number of SMS units sent so far

        On failure, throws an exception or returns YMessageBox.PDUSENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.PDUSENT_INVALID
        res = self._pduSent
        return res

    def set_pduSent(self, newval):
        """
        Changes the value of the outgoing SMS units counter.

        @param newval : an integer corresponding to the value of the outgoing SMS units counter

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("pduSent", rest_val)

    def get_pduReceived(self):
        """
        Returns the number of SMS units received so far.

        @return an integer corresponding to the number of SMS units received so far

        On failure, throws an exception or returns YMessageBox.PDURECEIVED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.PDURECEIVED_INVALID
        res = self._pduReceived
        return res

    def set_pduReceived(self, newval):
        """
        Changes the value of the incoming SMS units counter.

        @param newval : an integer corresponding to the value of the incoming SMS units counter

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("pduReceived", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMessageBox.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindMessageBox(func):
        """
        Retrieves a SMS message box interface for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the SMS message box interface is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMessageBox.isOnline() to test if the SMS message box interface is
        indeed online at a given time. In case of ambiguity when looking for
        a SMS message box interface by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the SMS message box interface, for instance
                YHUBGSM1.messageBox.

        @return a YMessageBox object allowing you to drive the SMS message box interface.
        """
        # obj
        obj = YFunction._FindFromCache("MessageBox", func)
        if obj is None:
            obj = YMessageBox(func)
            YFunction._AddToCache("MessageBox", func, obj)
        return obj

    def nextMsgRef(self):
        self._nextMsgRef = self._nextMsgRef + 1
        return self._nextMsgRef

    def clearSIMSlot(self, slot):
        self._prevBitmapStr = ""
        return self.set_command("DS" + str(int(slot)))

    def fetchPdu(self, slot):
        # binPdu
        arrPdu = []
        # hexPdu
        # sms

        binPdu = self._download("sms.json?pos=" + str(int(slot)) + "&len=1")
        arrPdu = self._json_get_array(binPdu)
        hexPdu = self._decode_json_string(arrPdu[0])
        sms = YSms(self)
        sms.set_slot(slot)
        sms.parsePdu(YAPI._hexStrToBin(hexPdu))
        return sms

    def initGsm2Unicode(self):
        # i
        # uni
        del self._gsm2unicode[:]
        # // 00-07
        self._gsm2unicode.append(64)
        self._gsm2unicode.append(163)
        self._gsm2unicode.append(36)
        self._gsm2unicode.append(165)
        self._gsm2unicode.append(232)
        self._gsm2unicode.append(233)
        self._gsm2unicode.append(249)
        self._gsm2unicode.append(236)
        # // 08-0F
        self._gsm2unicode.append(242)
        self._gsm2unicode.append(199)
        self._gsm2unicode.append(10)
        self._gsm2unicode.append(216)
        self._gsm2unicode.append(248)
        self._gsm2unicode.append(13)
        self._gsm2unicode.append(197)
        self._gsm2unicode.append(229)
        # // 10-17
        self._gsm2unicode.append(916)
        self._gsm2unicode.append(95)
        self._gsm2unicode.append(934)
        self._gsm2unicode.append(915)
        self._gsm2unicode.append(923)
        self._gsm2unicode.append(937)
        self._gsm2unicode.append(928)
        self._gsm2unicode.append(936)
        # // 18-1F
        self._gsm2unicode.append(931)
        self._gsm2unicode.append(920)
        self._gsm2unicode.append(926)
        self._gsm2unicode.append(27)
        self._gsm2unicode.append(198)
        self._gsm2unicode.append(230)
        self._gsm2unicode.append(223)
        self._gsm2unicode.append(201)
        # // 20-7A
        i = 32
        while i <= 122:
            self._gsm2unicode.append(i)
            i = i + 1
        # // exceptions in range 20-7A
        self._gsm2unicode[36] = 164
        self._gsm2unicode[64] = 161
        self._gsm2unicode[91] = 196
        self._gsm2unicode[92] = 214
        self._gsm2unicode[93] = 209
        self._gsm2unicode[94] = 220
        self._gsm2unicode[95] = 167
        self._gsm2unicode[96] = 191
        # // 7B-7F
        self._gsm2unicode.append(228)
        self._gsm2unicode.append(246)
        self._gsm2unicode.append(241)
        self._gsm2unicode.append(252)
        self._gsm2unicode.append(224)

        # // Invert table as well wherever possible
        self._iso2gsm = bytearray(256)
        i = 0
        while i <= 127:
            uni = self._gsm2unicode[i]
            if uni <= 255:
                self._iso2gsm[uni] = i
            i = i + 1
        i = 0
        while i < 4:
            # // mark escape sequences
            self._iso2gsm[91+i] = 27
            self._iso2gsm[123+i] = 27
            i = i + 1
        # // Done
        self._gsm2unicodeReady = True
        return YAPI.SUCCESS

    def gsm2unicode(self, gsm):
        # i
        # gsmlen
        # reslen
        res = []
        # uni
        if not (self._gsm2unicodeReady):
            self.initGsm2Unicode()
        gsmlen = len(gsm)
        reslen = gsmlen
        i = 0
        while i < gsmlen:
            if YGetByte(gsm, i) == 27:
                reslen = reslen - 1
            i = i + 1
        del res[:]
        i = 0
        while i < gsmlen:
            uni = self._gsm2unicode[YGetByte(gsm, i)]
            if (uni == 27) and (i+1 < gsmlen):
                i = i + 1
                uni = YGetByte(gsm, i)
                if uni < 60:
                    if uni < 41:
                        if uni==20:
                            uni=94
                        else:
                            if uni==40:
                                uni=123
                            else:
                                uni=0
                    else:
                        if uni==41:
                            uni=125
                        else:
                            if uni==47:
                                uni=92
                            else:
                                uni=0
                else:
                    if uni < 62:
                        if uni==60:
                            uni=91
                        else:
                            if uni==61:
                                uni=126
                            else:
                                uni=0
                    else:
                        if uni==62:
                            uni=93
                        else:
                            if uni==64:
                                uni=124
                            else:
                                if uni==101:
                                    uni=164
                                else:
                                    uni=0
            if uni > 0:
                res.append(uni)
            i = i + 1

        return res

    def gsm2str(self, gsm):
        # i
        # gsmlen
        # reslen
        # resbin
        # resstr
        # uni
        if not (self._gsm2unicodeReady):
            self.initGsm2Unicode()
        gsmlen = len(gsm)
        reslen = gsmlen
        i = 0
        while i < gsmlen:
            if YGetByte(gsm, i) == 27:
                reslen = reslen - 1
            i = i + 1
        resbin = bytearray(reslen)
        i = 0
        reslen = 0
        while i < gsmlen:
            uni = self._gsm2unicode[YGetByte(gsm, i)]
            if (uni == 27) and (i+1 < gsmlen):
                i = i + 1
                uni = YGetByte(gsm, i)
                if uni < 60:
                    if uni < 41:
                        if uni==20:
                            uni=94
                        else:
                            if uni==40:
                                uni=123
                            else:
                                uni=0
                    else:
                        if uni==41:
                            uni=125
                        else:
                            if uni==47:
                                uni=92
                            else:
                                uni=0
                else:
                    if uni < 62:
                        if uni==60:
                            uni=91
                        else:
                            if uni==61:
                                uni=126
                            else:
                                uni=0
                    else:
                        if uni==62:
                            uni=93
                        else:
                            if uni==64:
                                uni=124
                            else:
                                if uni==101:
                                    uni=164
                                else:
                                    uni=0
            if (uni > 0) and (uni < 256):
                resbin[reslen] = uni
                reslen = reslen + 1
            i = i + 1
        resstr = YByte2String(resbin)
        if len(resstr) > reslen:
            resstr = (resstr)[0: 0 + reslen]
        return resstr

    def str2gsm(self, msg):
        # asc
        # asclen
        # i
        # ch
        # gsm7
        # extra
        # res
        # wpos
        if not (self._gsm2unicodeReady):
            self.initGsm2Unicode()
        asc = YString2Byte(msg)
        asclen = len(asc)
        extra = 0
        i = 0
        while i < asclen:
            ch = YGetByte(asc, i)
            gsm7 = YGetByte(self._iso2gsm, ch)
            if gsm7 == 27:
                extra = extra + 1
            if gsm7 == 0:
                # // cannot use standard GSM encoding
                res = bytearray(0)
                return res
            i = i + 1
        res = bytearray(asclen+extra)
        wpos = 0
        i = 0
        while i < asclen:
            ch = YGetByte(asc, i)
            gsm7 = YGetByte(self._iso2gsm, ch)
            res[wpos] = gsm7
            wpos = wpos + 1
            if gsm7 == 27:
                if ch < 100:
                    if ch<93:
                        if ch<92:
                            gsm7=60
                        else:
                            gsm7=47
                    else:
                        if ch<94:
                            gsm7=62
                        else:
                            gsm7=20
                else:
                    if ch<125:
                        if ch<124:
                            gsm7=40
                        else:
                            gsm7=64
                    else:
                        if ch<126:
                            gsm7=41
                        else:
                            gsm7=61
                res[wpos] = gsm7
                wpos = wpos + 1
            i = i + 1
        return res

    def checkNewMessages(self):
        # bitmapStr
        # prevBitmap
        # newBitmap
        # slot
        # nslots
        # pduIdx
        # idx
        # bitVal
        # prevBit
        # i
        # nsig
        # cnt
        # sig
        newArr = []
        newMsg = []
        newAgg = []
        signatures = []
        # sms

        bitmapStr = self.get_slotsBitmap()
        if bitmapStr == self._prevBitmapStr:
            return YAPI.SUCCESS
        prevBitmap = YAPI._hexStrToBin(self._prevBitmapStr)
        newBitmap = YAPI._hexStrToBin(bitmapStr)
        self._prevBitmapStr = bitmapStr
        nslots = 8*len(newBitmap)
        del newArr[:]
        del newMsg[:]
        del signatures[:]
        nsig = 0
        # // copy known messages
        pduIdx = 0
        while pduIdx < len(self._pdus):
            sms = self._pdus[pduIdx]
            slot = sms.get_slot()
            idx = ((slot) >> (3))
            if idx < len(newBitmap):
                bitVal = ((1) << ((((slot) & (7)))))
                if (((YGetByte(newBitmap, idx)) & (bitVal))) != 0:
                    newArr.append(sms)
                    if sms.get_concatCount() == 0:
                        newMsg.append(sms)
                    else:
                        sig = sms.get_concatSignature()
                        i = 0
                        while (i < nsig) and (len(sig) > 0):
                            if signatures[i] == sig:
                                sig = ""
                            i = i + 1
                        if len(sig) > 0:
                            signatures.append(sig)
                            nsig = nsig + 1
            pduIdx = pduIdx + 1
        # // receive new messages
        slot = 0
        while slot < nslots:
            idx = ((slot) >> (3))
            bitVal = ((1) << ((((slot) & (7)))))
            prevBit = 0
            if idx < len(prevBitmap):
                prevBit = ((YGetByte(prevBitmap, idx)) & (bitVal))
            if (((YGetByte(newBitmap, idx)) & (bitVal))) != 0:
                if prevBit == 0:
                    sms = self.fetchPdu(slot)
                    newArr.append(sms)
                    if sms.get_concatCount() == 0:
                        newMsg.append(sms)
                    else:
                        sig = sms.get_concatSignature()
                        i = 0
                        while (i < nsig) and (len(sig) > 0):
                            if signatures[i] == sig:
                                sig = ""
                            i = i + 1
                        if len(sig) > 0:
                            signatures.append(sig)
                            nsig = nsig + 1
            slot = slot + 1

        self._pdus = newArr
        # // append complete concatenated messages
        i = 0
        while i < nsig:
            sig = signatures[i]
            cnt = 0
            pduIdx = 0
            while pduIdx < len(self._pdus):
                sms = self._pdus[pduIdx]
                if sms.get_concatCount() > 0:
                    if sms.get_concatSignature() == sig:
                        if cnt == 0:
                            cnt = sms.get_concatCount()
                            del newAgg[:]
                        newAgg.append(sms)
                pduIdx = pduIdx + 1
            if (cnt > 0) and (len(newAgg) == cnt):
                sms = YSms(self)
                sms.set_parts(newAgg)
                newMsg.append(sms)
            i = i + 1

        self._messages = newMsg
        return YAPI.SUCCESS

    def get_pdus(self):
        self.checkNewMessages()
        return self._pdus

    def clearPduCounters(self):
        """
        Clear the SMS units counters.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # retcode

        retcode = self.set_pduReceived(0)
        if retcode != YAPI.SUCCESS:
            return retcode
        retcode = self.set_pduSent(0)
        return retcode

    def sendTextMessage(self, recipient, message):
        """
        Sends a regular text SMS, with standard parameters. This function can send messages
        of more than 160 characters, using SMS concatenation. ISO-latin accented characters
        are supported. For sending messages with special unicode characters such as asian
        characters and emoticons, use newMessage to create a new message and define
        the content of using methods addText and addUnicodeData.

        @param recipient : a text string with the recipient phone number, either as a
                national number, or in international format starting with a plus sign
        @param message : the text to be sent in the message

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # sms

        sms = YSms(self)
        sms.set_recipient(recipient)
        sms.addText(message)
        return sms.send()

    def sendFlashMessage(self, recipient, message):
        """
        Sends a Flash SMS (class 0 message). Flash messages are displayed on the handset
        immediately and are usually not saved on the SIM card. This function can send messages
        of more than 160 characters, using SMS concatenation. ISO-latin accented characters
        are supported. For sending messages with special unicode characters such as asian
        characters and emoticons, use newMessage to create a new message and define
        the content of using methods addText et addUnicodeData.

        @param recipient : a text string with the recipient phone number, either as a
                national number, or in international format starting with a plus sign
        @param message : the text to be sent in the message

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # sms

        sms = YSms(self)
        sms.set_recipient(recipient)
        sms.set_msgClass(0)
        sms.addText(message)
        return sms.send()

    def newMessage(self, recipient):
        """
        Creates a new empty SMS message, to be configured and sent later on.

        @param recipient : a text string with the recipient phone number, either as a
                national number, or in international format starting with a plus sign

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # sms
        sms = YSms(self)
        sms.set_recipient(recipient)
        return sms

    def get_messages(self):
        """
        Returns the list of messages received and not deleted. This function
        will automatically decode concatenated SMS.

        @return an YSms object list.

        On failure, throws an exception or returns an empty list.
        """
        self.checkNewMessages()
        return self._messages

    def nextMessageBox(self):
        """
        Continues the enumeration of SMS message box interfaces started using yFirstMessageBox().
        Caution: You can't make any assumption about the returned SMS message box interfaces order.
        If you want to find a specific a SMS message box interface, use MessageBox.findMessageBox()
        and a hardwareID or a logical name.

        @return a pointer to a YMessageBox object, corresponding to
                a SMS message box interface currently online, or a None pointer
                if there are no more SMS message box interfaces to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YMessageBox.FindMessageBox(hwidRef.value)

#--- (end of generated code: YMessageBox implementation)

#--- (generated code: YMessageBox functions)

    @staticmethod
    def FirstMessageBox():
        """
        Starts the enumeration of SMS message box interfaces currently accessible.
        Use the method YMessageBox.nextMessageBox() to iterate on
        next SMS message box interfaces.

        @return a pointer to a YMessageBox object, corresponding to
                the first SMS message box interface currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("MessageBox", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YMessageBox.FindMessageBox(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YMessageBox functions)
