"""Python SCPI access to Red Pitaya. The core file contains only the absolutely necessary functionality and libraries."""

import socket
import struct

__author__ = "Luka Golinar, Iztok Jeras, Miha Gjura"
__copyright__ = "Copyright 2025, Red Pitaya"
__OS_version__ = "2.00 and above"            # The core file should be compatible even with older OS versions.

class scpi (object):
    """SCPI class used to access Red Pitaya over an IP network."""
    delimiter = '\r\n'

    def __init__(self, host, timeout=None, port=5000):
        """Initialize object and open IP connection.
        Host IP should be a string in parentheses, like '192.168.1.100' or 'rp-xxxxxx.local'.
        """
        self.host    = host
        self.port    = port
        self.timeout = timeout

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if timeout is not None:
                self._socket.settimeout(timeout)

            self._socket.connect((host, port))

        except socket.error as e:
            print('SCPI >> connect({!s:s}:{:d}) failed: {!s:s}'.format(host, port, e))

    def __del__(self):
        if self._socket is not None:
            self._socket.close()
        self._socket = None

    def close(self):
        """Close IP connection."""
        self.__del__()

    def rx_txt(self, chunksize = 4096):
        """Receive text string and return it after removing the delimiter."""
        msg = ''
        while 1:
            chunk = self._socket.recv(chunksize).decode('utf-8') # Receive chunk size of 2^n preferably
            msg += chunk
            if (len(msg) >= 2 and msg[-2:] == self.delimiter):
                return msg[:-2]

    def rx_txt_check_error(self, chunksize = 4096,stop = True):
        msg = self.rx_txt(chunksize)
        self.check_error(stop)
        return msg

    def rx_arb(self):
        """ Recieve binary data from scpi server"""
        numOfBytes = 0
        data=b''
        while len(data) != 1:
            data = self._socket.recv(1)
        if data != b'#':
            return False
        data=b''

        while len(data) != 1:
            data = self._socket.recv(1)
        numOfNumBytes = int(data)
        if numOfNumBytes <= 0:
            return False
        data=b''

        while len(data) != numOfNumBytes:
            data += (self._socket.recv(1))
        numOfBytes = int(data)
        data=b''

        while len(data) < numOfBytes:
            r_size = min(numOfBytes - len(data),4096)
            data += (self._socket.recv(r_size))

        self._socket.recv(2) # recive \r\n

        return data

    def rx_arb_check_error(self,stop = True):
        data = self.rx_arb()
        self.check_error(stop)
        return data

    def tx_txt(self, msg):
        """Send text string ending and append delimiter."""
        return self._socket.sendall((msg + self.delimiter).encode('utf-8')) # was send(().encode('utf-8'))

    def tx_txt_check_error(self, msg,stop = True):
        self.tx_txt(msg)
        self.check_error(stop)

    def txrx_txt(self, msg):
        """Send/receive text string."""
        self.tx_txt(msg)
        return self.rx_txt()

    def check_error(self,stop = True):
        res = int(self.stb_q())
        if (res & 0x4):
            while 1:
                err = self.err_n()
                if (err.startswith('0,')):
                    break
                print(err)
                n = err.split(",")
                if (len(n) > 0 and stop and int(n[0]) > 9500):
                    exit(1)


# IEEE Mandated Commands

    def cls(self):
        """Clear Status Command"""
        return self.tx_txt('*CLS')

    def ese(self, value: int):
        """Standard Event Status Enable Command"""
        return self.tx_txt(f'*ESE {value}')

    def ese_q(self):
        """Standard Event Status Enable Query"""
        return self.txrx_txt('*ESE?')

    def esr_q(self):
        """Standard Event Status Register Query"""
        return self.txrx_txt('*ESR?')

    def idn_q(self):
        """Identification Query"""
        return self.txrx_txt('*IDN?')

    def opc(self):
        """Operation Complete Command"""
        return self.tx_txt('*OPC')

    def opc_q(self):
        """Operation Complete Query"""
        return self.txrx_txt('*OPC?')

    def rst(self):
        """Reset Command"""
        return self.tx_txt('*RST')

    def sre(self, value: int):
        """Service Request Enable Command"""
        return self.tx_txt('*SRE {value}')

    def sre_q(self):
        """Service Request Enable Query"""
        return self.txrx_txt('*SRE?')

    def stb_q(self):
        """Read Status Byte Query"""
        return self.txrx_txt('*STB?')

# :SYSTem

    def err_c(self):
        """Error count."""
        return self.txrx_txt('SYST:ERR:COUN?')

    def err_n(self):
        """Error next."""
        return self.txrx_txt('SYST:ERR:NEXT?')
