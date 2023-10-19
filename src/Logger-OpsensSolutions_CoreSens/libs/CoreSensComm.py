import io
import struct
from typing import List, Tuple
import socket
import select

class CommandPackage:
    headerFmt = "<HH"

    def __init__(self, command=None):
        self.command = command

    @classmethod
    def fromBytes(cls, bytesToConvert: bytes):
        length = len(bytesToConvert)
        # header is 4 bytes, data must be null-terminated, so at least 5 bytes required
        if length < 5:
            print("Command bytes too short")
            return False
        commandPackage = CommandPackage()
        byteStream = io.BytesIO(bytesToConvert)
        dataType, size = struct.unpack(cls.headerFmt, byteStream.read(4))
        if dataType != 300:
            print("Wrong Data Type.")
            return False
        if size + 4 != length:
            print("Data length does not match expected size")
            return False
        data = byteStream.read()
        if data[-1] != 0:
            print("Data was not null-terminated.")
            return False
        commandPackage.command = data.strip(b'\r\n\x00').decode()
        return commandPackage

    def toBytes(self):
        byteStream = io.BytesIO()
        byteStream.write(struct.pack(self.headerFmt,
                                     300,
                                     len(self.command) + 3))
        byteStream.write(self.command.encode() + b'\r\n\x00')
        return byteStream.getvalue()

class DataPackage:
    headerFmt = "<BBBBI"
    dataFmt = "<Qf"

    def __init__(self):
        self.SystemID = None
        self.ModuleID = None
        self.ChannelID = None
        self.DataType = None
        self.MeasureQuantity = None
        self.Data = None

    @classmethod
    def fromBytes(cls, bytesToConvert: bytes):
        length = len(bytesToConvert)
        # even for zero data poins, header must be 8 bytes at least
        if length < 8:
            print("Package too short")
            return False
        dataPackage = DataPackage()
        # as the number of data points is dynamic, we use a bytestream, so that we can
        # loop over the number of data points and just continue reading from the stream
        byteStream = io.BytesIO(bytesToConvert)
        (dataPackage.SystemID,
         dataPackage.ModuleID,
         dataPackage.ChannelID,
         dataPackage.DataType,
         dataPackage.MeasureQuantity) = struct.unpack(cls.headerFmt, byteStream.read(8))
        # The device sends further charaters (\x00)
        # after the actual data, so the UDP package might be larger than the measurement points
        if length < 8 + 12 * dataPackage.MeasureQuantity:
            print("Package length does not match to MeasureQuantity")
            return False
        dataPackage.Data = []
        for i in range(0, dataPackage.MeasureQuantity):
            MeasurementPoint = struct.unpack(cls.dataFmt, byteStream.read(12))
            dataPackage.Data.append(MeasurementPoint)
        return dataPackage

    def toBytes(self):
        byteStream = io.BytesIO()
        byteStream.write(struct.pack(self.headerFmt,
                                     self.SystemID,
                                     self.ModuleID,
                                     self.ChannelID,
                                     self.DataType,
                                     self.MeasureQuantity))
        for dataPoint in self.Data:
            byteStream.write(struct.pack(self.dataFmt, *dataPoint))
        return byteStream.getvalue()

    @staticmethod
    def fromData(SystemID: int,
                 ModuleID: int,
                 ChannelID: int,
                 DataType: int,
                 Data: List[Tuple[int, float]]):
        dataPackage = DataPackage()
        dataPackage.SystemID = SystemID
        dataPackage.ModuleID = ModuleID
        dataPackage.ChannelID = ChannelID
        dataPackage.DataType = DataType
        dataPackage.MeasureQuantity = len(Data)
        dataPackage.Data = Data
        return dataPackage


dummyData = [
    (1234, 23.5),
    (1235, 25.5),
    (1236, 22.5),
    (1237, -19.3),
]


def getDummyPackage(dummyTime):
    taggedDummyData = [(dummyTime, 5.5)] + dummyData
    package = DataPackage.fromData(50, 13, 1, 2, taggedDummyData)
    enc = package.toBytes()
    return enc
    
class UDPconnection():
    """ Singleton class to handle the UDP communication """
    _instance = None
    
    def __init__(self, IP_server, IP_local):
        
        # this ensures that this class can be called multiple times without performing __init__ every time
        if not hasattr(self, "_is_init_complete"):
            self._is_init_complete = True
            
            self.UDPDataSocket = None  # Data communication socket
            self.UDPCommandSenderSocket = None  # Command communication socket for sending commands
            self.UDPCommandReceiverSocket = None  # Command communication socket for receiving responses to commands

            self.data = None
            self._data_dict = {}

            self.maxPacketSize = 1024
            self.maxBufferSize = 4 * 1024 * 1024 # 4 MB buffer
            
            self.packagesRead = 0 # can be removed later

            if not( all([x.isdigit() for x in IP_server.split(".")]) and len(IP_server.split(".")) == 4 ):
                raise Exception("Server IP address '%s' has incorrect format." % IP_server)
                
            if not( all([x.isdigit() for x in IP_local.split(".")]) and len(IP_local.split(".")) == 4 ):
                raise Exception("Local IP address '%s' has incorrect format." % IP_local)
            
            # self.IP_server = IP_server
            # self.IP_local = IP_local

            self.UDPDataSocket = self.connectReceiver( addressPort=(IP_local, 50911), multicast=True )
            self.UDPCommandReceiverSocket = self.connectReceiver( addressPort=(IP_local, 50910) )
            self.UDPCommandSenderSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            
            self.serverAddressPort = (IP_server, 50910)
            
            self._verbose_mode = False
            
            
    def __new__(class_, *args, **kwargs):
    
        # this ensures that the OptionManager can be called multiple times without creating a new instance
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_)
             
        return class_._instance     
        
    def __del__(self):
        pass
                
                
    @staticmethod
    def getIPSuggestions(targetIP="10.255.255.255"):
        try:
            IP1 = socket.gethostbyname_ex(socket.gethostname())[-1]
            IP2 = socket.gethostbyname_ex(socket.gethostname())[-1]
            alternatives = IP1 + IP2
        except:
            alternatives = []
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((targetIP, 1))
            likelyIP = s.getsockname()[0]
            # alternatives += [likelyIP]
        except:
            likelyIP = ""
        return likelyIP, list(set(alternatives))
        
        
    def connectReceiver(self, addressPort, multicast=False):
        receiver = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
            proto=socket.IPPROTO_UDP if multicast else 0
        )
        receiver.bind(addressPort)
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # multiple applications on the same PC
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.maxBufferSize)  # Buffer size is set here
        buffer_size = receiver.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        if buffer_size < self.maxBufferSize:
            raise Exception("Unable to increase buffer size for UDP communication")
        if multicast:
            mreq = struct.pack("4s4s", socket.inet_aton("239.0.0.1"), socket.inet_aton(addressPort[0]))
            receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return receiver

    def close(self):
    
        if not self.UDPDataSocket is None:
            self.UDPDataSocket.close()     
            self.UDPDataSocket = None
        
        if not self.UDPCommandSenderSocket is None:
            self.UDPCommandSenderSocket.close()
            self.UDPCommandSenderSocket = None
            
        if not self.UDPCommandReceiverSocket is None:
            self.UDPCommandReceiverSocket.close()
            self.UDPCommandReceiverSocket = None
        
                     
    def query(self, cmd, multi_package = False):
        """
        sends a command and returns a list of strings containing the information of the returned packages.

        Parameters:
        cmd: command to be send being a string
        multi_package: bool, if True packages from multiple channels are readout using a timeout
        """
        
        self._last_cmd = cmd
        self.UDPCommandSenderSocket.sendto(CommandPackage(cmd).toBytes(), self.serverAddressPort)
        if self._verbose_mode:
            print()
            print("CoreSens: Send command ->", cmd)
        
        packages = []  # this list will be used to collect all packages
        
        # We immediately check whether the command is returned
        # The first two packages are read with a timeout > 0.0 s
        if self.is_package_ready(self.UDPCommandReceiverSocket, 5.0):
            package = self.read_single_package(self.UDPCommandReceiverSocket)[:-3].decode()
            if self._verbose_mode:
                print("CoreSens: Receive command <-", package)
        else:
            raise Exception("Timeout after sending command to CoreSens device. Please check whether the correct IP address is used or whether a firewall stops communication.")
        
        
        if self.is_package_ready(self.UDPCommandReceiverSocket, 5.0):
            package = self.read_single_package(self.UDPCommandReceiverSocket)[:-4].decode()
            packages.append(package)
            if self._verbose_mode:
                print("CoreSens: Receive response <-", package)
        else:
            raise Exception("Timeout after sending command to CoreSens device. Please check whether the correct IP address is used or whether a firewall stops communication.")

        if package.startswith("Err"):

            error_code = int(package[3:-1].strip())
            
            if error_code in error_codes:
                print("CoreSens:", error_codes[error_code])
            else:
                print("CoreSens: Error code not defined ->", answer)
          
        if multi_package:
            # reading out all remaining packages
            while self.is_package_ready(self.UDPCommandReceiverSocket, 0.3):
                package = self.read_single_package(self.UDPCommandReceiverSocket)[:-3].decode()
                if self._verbose_mode:
                    print("CoreSens: Receive command <-", package)
                
                if self.is_package_ready(self.UDPCommandReceiverSocket, 0.3):
                    package = self.read_single_package(self.UDPCommandReceiverSocket)[:-4].decode()
                    packages.append(package)
                    if self._verbose_mode:
                        print("CoreSens: Receive response <-", package)
                    
                if package.startswith("Err"):

                    error_code = int(package[3:-1].strip())
                    
                    if error_code in error_codes:
                        print("CoreSens:", error_codes[error_code])
                    else:
                        print("CoreSens: Error code not defined ->", answer)
        
        # we return a list of all received packages excludind packages that just return the command
        return packages
    
        
    def is_package_ready(self, receiver, timeout = 0.0):
        ready, _, _ = select.select([receiver], [], [], timeout)
        return not not ready  # first "not" makes a bool, second "not" negates the bool to what is needed

    def read_single_package(self, receiver):
        return receiver.recvfrom(self.maxPacketSize)[0]
       
    def read_all_packages(self, receiver):
    
        data = []
        while self.is_package_ready(receiver):
            data += [self.read_single_package(receiver)]

        return data

    def read_data(self):
        """ reads out the buffer once and splits the data regarding all channels """
        
        while self.is_package_ready(self.UDPDataSocket):
        
            package = self.read_single_package(self.UDPDataSocket)
            
            # print()
            # print("Last data package:")
            # print(package)
            
            dp = DataPackage.fromBytes(package)
            
            if not dp.SystemID in self._data_dict:
                self._data_dict[dp.SystemID] = {}
            if not dp.ModuleID in self._data_dict[dp.SystemID]:
                self._data_dict[dp.SystemID][dp.ModuleID] = {}
            if not dp.ChannelID in self._data_dict[dp.SystemID][dp.ModuleID]:  
                self._data_dict[dp.SystemID][dp.ModuleID][dp.ChannelID] = {"time":[], "value":[]}
               
            time_vals, measure_vals = list(zip(*dp.Data))
            self._data_dict[dp.SystemID][dp.ModuleID][dp.ChannelID]["time"] += [x/10000 for x in time_vals]  # translates integer into seconds since 01.01.1970
            self._data_dict[dp.SystemID][dp.ModuleID][dp.ChannelID]["value"] += measure_vals        

            self.packagesRead += 1
                
        # print(f"Total Packages read: {self.packagesRead}")

    def get_data(self, system:int = 1, slot:int = 1, channel:int = 1):
        """ returns two lists: time and value data series """
        
        if not system in self._data_dict:
            print("UDPcomm: No data for system", repr(system))
            return [],[]
        elif not slot in self._data_dict[system]:
            print("UDPcomm: No data for slot", repr(system), repr(slot))
            return [],[]
        elif not channel in self._data_dict[system][slot]:  
            print("UDPcomm: No data for channel", repr(system), repr(slot), repr(channel))
            return [],[]
                
        time_vals = self._data_dict[system][slot][channel]["time"]
        measure_vals = self._data_dict[system][slot][channel]["value"]
        
        self._data_dict[system][slot][channel]["time"] = []
        self._data_dict[system][slot][channel]["value"] = []
      
        return time_vals, measure_vals
    

error_codes = {       
                   0: "No error",
                -104: "Invalid parameter(s) value",
                -105: "Too many numeric suffixes",
                -110: "No input command to parse",
                -114: "Numeric suffix is invalid",
                -116: "Invalid value in numeric or channel list (out of range)",
                -117: "Invalid number of dimensions in a channel list",
                -110: "No input command to parse",
                -114: "Numeric suffix is invalid",
                -116: "Invalid value in numeric or channel list (out of range)",
                -117: "Invalid number of dimensions in a channel list",
                -120: "Parameter of type numeric value overflowed its storage",
                -130: "Wring units for parameter",
                -140: "Wrong type of parameters",
                -150: "Wrong number of parameters",
                -160: "Unmatched quotation mark (single/double) in parameter",
                -165: "Unmatched bracket",
                -170: "Invalid SCPI command (Command keywords were not recognize)",
                -180: "No entry in list to retrieve",
                -190: "Too many dimensions in entry to be returned in parameters",
                -201: "Acquisition in progress",
                -202: "File acquisition in progress",
                -203: "Module upgrade in progress",
                -204: "Unknown format.",
                -207: "No client connected to receive the data",
                -301: "Sensor list is full",
                -302: "Sensor name is invalid, it must be between 00 and 99 with 2 digits",
                -303: "Sensor name already in use",
                -304: "Sensor type invalid on board",
                -311: "System number is invalid",
                -331: "Channel number is invalid",
                -332: "Sensor number is invalid",
                -333: "Sensor not assigned to a channel",
                -334: "All channel are disabled, can’t start an acquisition",
                -335: "Filter type is invalid",
                -450: "Error while trying to get the current value",
                -451: "Error while setting the current value of the current source",
                -501: "Error, firmware upgrade file is invalid or corrupted",
                -505: "Generic error occurs when upgrading modules or firmware",
                }



if __name__ == '__main__':

    senderPackage = DataPackage.fromData(50, 13, 1, 2, dummyData)
    encoded = senderPackage.toBytes()
    print("Encoded:", encoded)

    receiverPackage = DataPackage.fromBytes(encoded)

    print("Decoded:", vars(receiverPackage))
