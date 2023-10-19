__author__ = 'Falk Ziegler'
__email__ = 'fz@accurion.com'
__maintainer__ = 'Falk Ziegler'

import socket
import struct
from functools import partial

def _pack(data, typecast=True):
    """
    WTF!
    """
    if not typecast:
        data = repr(data) if isinstance(data, str) else str(data)
    if isinstance(data, str):
        data = data.encode('utf-8')
    return struct.pack('>i', len(data)) + data


class IPConnection:
    """
    Class representing the IP connection into the Accurion apps.
    ToDo: Refactoring necessary -> Change protocol!
    """

    class GeneralErrorHandler(Exception):
        def __init__(self, message):
            self.message = message
        def __str__(self):
            return self.message

    def __init__(self, address, port):
        self.__sockets = {}
        self.__sandbox = {}
        self.__connect(address, port)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __connect(self, address, port):
        self.__address = (address, port)
        for i, name in enumerate(('STANDARD', 'INTERRUPT')):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(.1)
                s.connect(self.__address)
                self.__route('python+{0}@127.0.0.1:{1}'.format(name, 2345 + i), header=False, sync=False, sock=s)
                self.__sockets[name] = s
                if not i:
                    for name in self.__route('__init__', sock=s):
                        setattr(self, name, partial(self.__route, name, sock=s))
            except Exception as e:
                s.close()
                raise

    def __route(self, *args, header=True, sync=True, sock=None):
        data = bytes()
        for i, arg in enumerate(args):
            if header and not i:
                # header + packed function name
                data += struct.pack('>IIbb', 123, 123, 1, 1) + _pack(arg)
            else:
                data += _pack(arg, typecast = False)
        # send packed data now
        data = sock.sendall(_pack(data))
        # data receive in case of synchronous message
        if sync:
            i = 0
            data = ''
            while True:
                try:
                    if not i:
                        payload = struct.unpack('>I', sock.recv(4))[0]
                    if i < payload:
                        data += sock.recv(1).decode('utf-8')
                        i += 1
                    else:
                        break
                except socket.timeout:
                    continue
            # we skip the complete header here
            status, source, data = eval(data[10:], {'__builtins__' : None}, self.__sandbox)
            if status:
                raise IPConnection.GeneralErrorHandler(source)
            return data

    def close(self):
        s = self.__sockets.get('INTERRUPT')
#        if s is not None:       #UNCOMMENTED BECAUSE OF INTERRUPT ISSUSE
#           self.__route('__close__', sync=False, sock=s)         #UNCOMMENTED BECAUSE OF INTERRUPT ISSUSE
        for name in list(self.__sockets.keys()):
            s = self.__sockets.pop(name)
            try:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
            except:
                pass
