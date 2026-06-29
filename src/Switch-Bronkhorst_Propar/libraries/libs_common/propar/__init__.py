__version__ = "1.1.1"

import collections
import serial
import struct
import threading
import time

from . import parameters

# status codes dict, input code, get string
pp_status_codes = { 0: 'PP_STATUS_OK',
                    1: 'PP_STATUS_PROCESS_CLAIMED',
                    2: 'PP_STATUS_COMMAND',
                    3: 'PP_STATUS_PROC_NUMBER',
                    4: 'PP_STATUS_PARM_NUMBER',
                    5: 'PP_STATUS_PARM_TYPE',
                    6: 'PP_STATUS_PARM_VALUE',
                    7: 'PP_STATUS_NETWORK_NOT_ACTIVE',
                    8: 'PP_STATUS_TIMEOUT_START_CHAR',
                    9: 'PP_STATUS_TIMEOUT_SERIAL_LINE',
                   10: 'PP_STATUS_HARDWARE_MEMORY',
                   11: 'PP_STATUS_NODE_NUMBER',
                   12: 'PP_STATUS_GENERAL_COMMUNICATION',
                   13: 'PP_STATUS_READONLY',
                   14: 'PP_STATUS_PC_COMMUNICATION',
                   15: 'PP_STATUS_NO_RS232_CONNECTION',
                   16: 'PP_STATUS_PC_OUT_OF_MEMORY',
                   17: 'PP_STATUS_WRITEONLY',
                   18: 'PP_STATUS_UNKNOWN_CONFIGURATION',
                   19: 'PP_STATUS_NO_FREE_NODE_ADDRESS',
                   20: 'PP_STATUS_WRONG_INTERFACE',
                   21: 'PP_STATUS_ERROR_SERIAL_PORT',
                   22: 'PP_STATUS_OPENING_COMMUNICATION',
                   23: 'PP_STATUS_COMMUNICATION_ERROR',
                   24: 'PP_STATUS_INTERFACE_BUS_MASTER',
                   25: 'PP_STATUS_TIMEOUT_ANSWER',
                   26: 'PP_STATUS_NO_START_CHARACTER',
                   27: 'PP_STATUS_ERROR_FIRST_DIGIT',
                   28: 'PP_STATUS_HOST_BUFFER_OVERFLOW',
                   29: 'PP_STATUS_BUFFER_OVERFLOW',
                   30: 'PP_STATUS_NO_ANSWER_FOUND',
                   31: 'PP_STATUS_ERROR_CLOSE_COMM',
                   32: 'PP_STATUS_SYNC_ERROR',
                   33: 'PP_STATUS_SEND_ERROR',
                   34: 'PP_STATUS_PROTOCOL_ERROR',
                   35: 'PP_STATUS_MODULE_BUFFER_OVERFLOW'}
                   
# propar commands
PP_COMMAND_STATUS                =    0  # status message
PP_COMMAND_SEND_PARM_WITH_ACK    =    1  # send parameter with ack
PP_COMMAND_SEND_PARM             =    2  # send parameter no ack
PP_COMMAND_SEND_PARM_BROADCAST   =    3  # parameter broadcast
PP_COMMAND_REQUEST_PARM          =    4  # request parameter

# propar status codes
PP_STATUS_OK                     =    0  # status ok              
PP_STATUS_PROCESS_CLAIMED        =    1  # process is claimed     
PP_STATUS_COMMAND                =    2  # unknown propar command 
PP_STATUS_PROC_NUMBER            =    3  # unknown process number 
PP_STATUS_PARM_NUMBER            =    4  # unknown param number   
PP_STATUS_PARM_TYPE              =    5  # invalid parameter type 
PP_STATUS_PARM_VALUE             =    6  # invalid parameter value
PP_STATUS_NETWORK_NOT_ACTIVE     =    7  # network not active     
PP_STATUS_TIMEOUT_START_CHAR     =    8  # timeout in start char  
PP_STATUS_TIMEOUT_SERIAL_LINE    =    9  # timeout serial line    
PP_STATUS_HARDWARE_MEMORY        =   10  # hardware memory error  
PP_STATUS_NODE_NUMBER            =   11  # node number error      
PP_STATUS_GENERAL_COMMUNICATION  =   12  # general communication  
PP_STATUS_READONLY               =   13  # parameter is readonly  
PP_STATUS_PC_COMMUNICATION       =   14  # error pc-communication
PP_STATUS_NO_RS232_CONNECTION    =   15  # no rs232 connection    
PP_STATUS_PC_OUT_OF_MEMORY       =   16  # pc out of memory       
PP_STATUS_WRITEONLY              =   17  # parameter is writeonly 
PP_STATUS_UNKNOWN_CONFIGURATION  =   18  # unknown configuration  
PP_STATUS_NO_FREE_NODE_ADDRESS   =   19  # no free node address   
PP_STATUS_WRONG_INTERFACE        =   20  # wrong interface        
PP_STATUS_ERROR_SERIAL_PORT      =   21  # serial port connection 
PP_STATUS_OPENING_COMMUNICATION  =   22  # opening communication  
PP_STATUS_COMMUNICATION_ERROR    =   23  # communication error    
PP_STATUS_INTERFACE_BUS_MASTER   =   24  # interface bus master   
PP_STATUS_TIMEOUT_ANSWER         =   25  # timeout answer         
PP_STATUS_NO_START_CHARACTER     =   26  # no start character     
PP_STATUS_ERROR_FIRST_DIGIT      =   27  # error first digit      
PP_STATUS_HOST_BUFFER_OVERFLOW   =   28  # host buffer overflow   
PP_STATUS_BUFFER_OVERFLOW        =   29  # buffer overflow        
PP_STATUS_NO_ANSWER_FOUND        =   30  # no answer found        
PP_STATUS_ERROR_CLOSE_COMM       =   31  # close comm error       
PP_STATUS_SYNC_ERROR             =   32  # synchronization error  
PP_STATUS_SEND_ERROR             =   33  # send error             
PP_STATUS_PROTOCOL_ERROR         =   34  # propar protocol error  
PP_STATUS_MODULE_BUFFER_OVERFLOW =   35  # buffer overflow        

# propar error codes
PP_ERROR_PROTOCOL_ERROR          =    4  # propar protocol error
PP_ERROR_MESSAGE_REJECTED        =    5  # destination addr reject
PP_ERROR_RESPONSE_TIMEOUT        =    9  # propar response timeout
  
# propar data types  
PP_TYPE_INT8                     = 0x00  # integer,  8 bit
PP_TYPE_INT16                    = 0x20  # integer, 16 bit
PP_TYPE_SINT16                   = 0x21  # regular signed integer, 16 bit, 32767 max, -32767 min
PP_TYPE_BSINT16                  = 0x22  # bronkhorst signed integer, 16 bit, 41942 max, -23593 min
PP_TYPE_INT32                    = 0x40  # integer, 32 bit
PP_TYPE_FLOAT                    = 0x41  # floating point
PP_TYPE_STRING                   = 0x60  # string

# propar communication modes
PP_MODE_BINARY                   =    0  # Binary mode
PP_MODE_ASCII                    =    1  # ASCII mode

# propar max parameter length (strings)
MAX_PP_PARM_LEN                  =   61  # max parameter length  

# List of initialized masters
_PROPAR_MASTERS = {}


class instrument(object):
  """Implements a propar instrument for easy access to instrument parameters. 
  
  The instrument class wraps around a master instance, which is created for the given comport.
  Multiple instruments with the same comport use the same master. 
  
  Args:
    comport (str): COM port on which the instrument is connected (e.g. 'COM1' or '/dev/ttyUSB0').
    address (int, optional): Address of the instrument, default = 128 for local instrument.
    baudrate (int, optional): Baudrate to use for communication.
    channel (int, optional): Channel to use for communication.
    serial_class (obj, optional): Custom serial class to be used for serial communication with the instrument.

  Attributes:
    address (int): Address of the instrument
    comport (str): COM port on which the instrument is connected
    master (obj): Instance of the master class used for communication.
    db (obj): Instance of the propar database, for conversion from DDE number to process, parameter number.
  """

  def __init__(self, comport, address=0x80, baudrate=38400, channel=1, serial_class=serial.Serial):
    self.address = address
    self.comport = comport
    self.channel = channel
    if comport in _PROPAR_MASTERS:    
      # Master already created previously
      self.master = _PROPAR_MASTERS[comport]
    else: 
      # No master, create it and store it
      self.master = master(comport, baudrate, serial_class=serial_class)
      _PROPAR_MASTERS[comport] = self.master
    self.db = self.master.db

  def __modify_parameter_channel(self, parm, channel=None):
    """Adjust the parameter definition for current channel.
    
    Args:
      parm (dict): Parameter to modify.
      channel (int, optional): Channel to use for communication (if none, self.channel is used).

    Returns:
      Modified parameter.
    """
    if channel == None:
      channel = self.channel
    if channel >= 1 and channel <= 16:
      if parm['proc_nr'] in [1, 33, 65, 97, 104]:
        parm = dict(parm)
        parm['proc_nr'] += channel - 1
    return parm

  def readParameter(self, dde_nr, channel=None):
    """Read a single parameter indicated by DDE nr.

    Args:
      dde_nr (int): FlowDDE parameter number.
      channel (int, optional): Channel to use for communication.

    Returns:
      Parameter data if successful, None otherwise.
    """
    try:
      parm = self.db.get_parameter(dde_nr)
    except:
      raise ValueError('DDE parameter number error!')
    resp = self.read_parameters([parm], channel=channel)	
    if resp != None:
      for r in resp:
        return r['data']
    else:
      return None

  def writeParameter(self, dde_nr, data, channel=None):
    """Write a single parameter indicated by DDE nr.

    Args:
      dde_nr (int): FlowDDE parameter number.
      data: Parameter data to write.
      channel (int, optional): Channel to use for communication.

    Returns:
      True if successful, False otherwise.
    """
    try:
      parm = self.db.get_parameter(dde_nr)
    except:
      raise ValueError('DDE parameter number error!')
    parm['data'] = data
    resp = self.write_parameters([parm], channel=channel)
    return (resp == PP_STATUS_OK)

  def read_parameters(self, parameters, callback=None, channel=None):
    """Read multiple parameters.
    
    Args:
      parameters: List of parameter objects.
      callback (function, optional): Function to be called when parameters are received (function will return directly!).
      channel (int, optional): Channel to use for communication.
      
    Returns:
      List with parameters with data if successful, list with one status item otherwise.
    """
    parameters[0]['node'] = self.address
    parameters = [self.__modify_parameter_channel(parm, channel) for parm in parameters]
    return self.master.read_parameters(parameters, callback)

  def write_parameters(self, parameters, command=PP_COMMAND_SEND_PARM_WITH_ACK, callback=None, channel=None):
    """Write multiple parameters.
    
    Args:
      parameters: List of parameter objects, with data.
      command (int, optional): Propar command to use for writing.
      callback (function, optional): Function to be called when parameters are received (function will return directly!).
      channel (int, optional): Channel to use for communication.

    Returns:
      Propar status code (0 if successful).
    """
    parameters[0]['node'] = self.address
    parameters = [self.__modify_parameter_channel(parm, channel) for parm in parameters]
    return self.master.write_parameters(parameters, command, callback)

  def read(self, proc_nr, parm_nr, parm_type):
    """Read a single parameter.
    
    Args:
      proc_nr (int): process number.
      parm_nr (int): parameter number.
      parm_type (int): parameter type.

    Returns:
      Parameter value if successful, None otherwise.
    """
    return self.master.read(self.address, proc_nr, parm_nr, parm_type)

  def write(self, proc_nr, parm_nr, parm_type, data):
    """Write a single parameter.
    
    Args:
      proc_nr (int): process number.
      parm_nr (int): parameter number.
      parm_type (int): parameter type.
      data: parameter data.

    Returns:
      True if successful, False otherwise.
    """
    return self.master.write(self.address, proc_nr, parm_nr, parm_type, data)
  
  def wink(self, time=9):
    """Wink the LEDs on the instrument.
    
    Args:
      time (int, optional): Wink duration 1-9 seconds.    

    Returns:
      True if successful, False otherwise.
    """
    time_char = bytes([0x30+time]).decode('ascii')
    return self.writeParameter(1, time_char)

  @property
  def setpoint(self):
    """Reads the setpoint of the instrument (0-32000 = 0-100%).
    
    Returns:
      Instrument setpoint if successful, None otherwise.
    """
    self._setpoint = self.readParameter(9)
    return self._setpoint

  @setpoint.setter
  def setpoint(self, value):
    """Sets the setpoint of the instrument (0-32000 = 0-100%).

    Returns:
      True if successful, False otherwise.
    """
    return self.writeParameter(9, value)

  @property
  def measure(self):
    """Reads the measure of the instrument (0-32000 = 0-100%).
    
    Returns:
      Instrument measure if successful, None otherwise.
    """
    measure = self.readParameter(8)
    return measure

  @property
  def id(self):
    """Reads the ID parameter of the instrument.
    
    Returns:
      Instrument ID if successful, None otherwise.
    """
    return self.readParameter(1)

        


class master(object):
  """Implements a propar master for communication with Bronkhorst instruments. 
  
    After initializing this can be used to read/write parameters of an instrument. 
    When local host functionality is used (MBC with flowbus), it is also possible to 
    communicate with other nodes on the network.
  
  Args:
    comport (str): COM port on which the instrument is connected (e.g. 'COM1' or '/dev/ttyUSB0').
    baudrate (int, optional): Baudrate to use for communication.
    serial_class (obj, optional): Custom serial class to be used for serial communication with the instrument.

  Attributes:
    address (int): Address of the instrument
    comport (str): COM port on which the instrument is connected
    master (obj): Instance of the master class used for communication.
    db (obj): Instance of the propar database, for conversion from DDE number to process, parameter number.
  """

  def __init__(self, comport, baudrate, serial_class=serial.Serial):
    try:
      # serial propar interface, provides propar message dicts.
      self.propar = _propar_provider(baudrate, comport, serial_class=serial_class)
    except:
      raise

    # propar message builder
    self.propar_builder = _propar_builder()

    # database
    self.db = database()

    # debug flags
    self.debug_requests = False
    self.debug          = False

  	# callback for any propar broadcasts that are received
    self.broadcast_callback = self.__dummy_callback

    # sequence number
    self.seq = 0
    # lock for sequence
    self.seq_lock = threading.Lock()
    
    # list of active messages
    self.__pending_requests   = []    
    self.__processed_requests = []
    
    # 500 ms timeout on all messages
    self.response_timeout = 0.5
    
    # thread for processing propar messages
    self.msg_handler_thread = threading.Thread(target=self.__message_handler_task, args=())
    self.msg_handler_thread.daemon = True
    self.msg_handler_thread.start()    

  def __dummy_callback(self, dummy):
    pass

  def set_baudrate(self, baudrate):
    """Set the baudrate used for communication.
    
    Args:
      baudrate (int): New baudrate.
    """
    self.propar.set_baudrate(baudrate)

  def dump(self, level=1): 
    """Set dump level for debug purposes.

    Dump level 0 = Disable.
    Dump level 1 = Print non-propar communication to console.
    Dump level 2 = Print all communication to console.
    
    Args:
      level (int): New dump level.
    """
    self.propar.dump = level
  
  def stop(self): 
    """Disconnect the comport."""
    self.propar.stop()
    
  def start(self): 
    """Reconnect the comport."""
    self.propar.start()
  
  def get_nodes(self, find_first=True):
    """Get a list of nodes on the network. 
    
    Will scan from 1 to local address to find the first node!
    
    Args:
      find_first (bool, optional): Scan from 1 to local address to find node.

    Returns:
      List with information about the instruments on the network.
    """ 
    scan_address  = 0x80  
    found_nodes   = []
    loop_detected = False

    if find_first:      
      found_first_node = False
      scan_address     = 1     
      local_address    = self.read_parameters([{'node': 0x80, 'proc_nr': 0, 'parm_nr': 1, 'parm_type': PP_TYPE_INT8}])[0]['data']     
      org_timeout = self.response_timeout
      self.response_timeout = 0.05   # scan with small timeout to speed this up.
      while found_first_node == False and scan_address != local_address:
        resp = self.read_parameters([{'node': scan_address, 'proc_nr': 0, 'parm_nr': 1, 'parm_type': PP_TYPE_INT8}])
        if resp[0]['status'] == PP_STATUS_OK:
          found_first_node = True
        else:
          scan_address += 1
      self.response_timeout = org_timeout

    while scan_address != 0 and loop_detected == False:
      parms = [{'node': scan_address, 'proc_nr': 0, 'parm_nr':  1, 'parm_type': PP_TYPE_INT8  },# address of this node
               {'node': scan_address, 'proc_nr': 0, 'parm_nr':  0, 'parm_type': PP_TYPE_STRING},# id
               {'node': scan_address, 'proc_nr': 0, 'parm_nr':  3, 'parm_type': PP_TYPE_INT8  }]# address of the next node

      resp = self.read_parameters(parms)

      if resp[0]['status'] != PP_STATUS_OK:
        if self.debug:
          print("Received status {:}. Retry reading parameters.".format(resp[0]['status']))
        # fall back to single requests for each parameter
        resp = [None, None, None]
        resp[0] = self.read_parameters([parms[0]])[0]
        resp[1] = self.read_parameters([parms[1]])[0]
        resp[2] = self.read_parameters([parms[2]])[0]
        for res, req in zip(resp, parms):
          if res['status'] != PP_STATUS_OK:
            scan_address = 0
            if self.debug:
              print("Received status {:} for parameter {:}. Abort.".format(res['status'], req))

      if scan_address != 0:
        # get serial number from id string
        serial_number = resp[1]['data'][3:]

        if self.debug:
          print("This is node {:>2} ({:}). Next node is {:}".format(resp[0]['data'], serial_number, resp[2]['data']))

        # Try to get device type from device
        dev_resp = self.read_parameters([{'node': scan_address, 'proc_nr': 113, 'parm_nr': 1, 'parm_type': PP_TYPE_STRING}]) # device type
        
        if dev_resp[0]['status'] == PP_STATUS_OK:
          device_type = dev_resp[0]['data']
        else:
          # try to get device type from the database
          db = database()
          # extract device id from id string (first byte)
          device_type = int.from_bytes(bytes(resp[1]['data'][0], encoding='ascii'), byteorder='little')
          options = db.get_parameter_values(175)
          for option in options:          
            if device_type == int(option['value']):
              device_type = option['description'].split(':')[0]

        # Try to get the number of channels from device
        chan_resp = self.read_parameters([{'node': scan_address, 'proc_nr': 0, 'parm_nr': 18, 'parm_type': PP_TYPE_INT8}]) # number of channels
        
        if chan_resp[0]['status'] == PP_STATUS_OK:
          nr_of_channels = chan_resp[0]['data']
        else:
          nr_of_channels = 1

        # Scan address = next address
        scan_address = resp[2]['data']

        # Check if the found node is already in the list.
        # In that case there is a network loop, and we stop looking for nodes.
        for node in found_nodes:
          if scan_address == node['address']:
            loop_detected = True
            if self.debug:
              print('Found network loop on node {:}'.format(resp[0]['data']))

        found_nodes.append({'address': resp[0]['data'], 'type': device_type, 'serial': serial_number, 'id': resp[1]['data'], 'channels': nr_of_channels})        

    return found_nodes


  def __fix_parameters(self, requested, received):
    """Fix parameters by adjusting type of received parameters with requested type."""
    fixed_parameters = []
    for org_parm, recv_parm in zip(requested, received):
      try:
        # fix float
        if org_parm['parm_type'] == PP_TYPE_FLOAT and recv_parm['parm_type'] == PP_TYPE_INT32:
          recv_parm['data'] = struct.unpack('f', struct.pack('I', recv_parm['data']))[0]
          recv_parm['parm_type'] = PP_TYPE_FLOAT
        # fix sint16
        elif org_parm['parm_type'] == PP_TYPE_SINT16 and recv_parm['parm_type'] == PP_TYPE_INT16:
          recv_parm['data'] = struct.unpack('h', struct.pack('H', recv_parm['data']))[0]
          recv_parm['parm_type'] = PP_TYPE_SINT16
        # fix bsint16
        elif org_parm['parm_type'] == PP_TYPE_BSINT16 and recv_parm['parm_type'] == PP_TYPE_INT16:
          if recv_parm['data'] > 0xA3D6: # 41942
            recv_parm['data'] = (0xFFFF - recv_parm['data']) * (-1)
          recv_parm['parm_type'] = PP_TYPE_BSINT16
        # copy over dde_nr and parm_name when present in org_parm
        if 'dde_nr' in org_parm.keys():
          recv_parm['dde_nr'] = org_parm['dde_nr']
        if 'parm_name' in org_parm.keys():
          recv_parm['parm_name'] = org_parm['parm_name']
      except:
        pass
      fixed_parameters.append(recv_parm)
    return fixed_parameters


  def __message_handler_task(self):
    """Handle propar messages (read/write requests) from the message queue in the propar_serial object.
    Read a propar message from self.propar (_propar_provider)
    Could theoretically be any type of message, but here we only process:
      * Status
      * Error
      * Send Parameter
    All received messages can be matched to a request in the self.__pending_requests list.
    Matches are made based on:
      * Sequence Number
      * Node Address
    After processing a callback may be called if it was provided during sending the request.
    For write the callback can acknowledge the write (with status). Status on failure is also possible.
    For read the callback returns the list of parameters with data. Callback is per request, not per parameter.
    """    
    while True:
      # Read new propar message
      propar_message = self.propar.read_propar_message()

      if propar_message == None:
        time.sleep(0.001)
      else:
        # Remove timed out requests based on age, and do callback with timeout when timed out!.
        check_time = time.time() - self.response_timeout
        filtered_requests = []
        for req in self.__pending_requests:
          if check_time <= req['age']:
            filtered_requests.append(req)
          else:
            if req['callback'] != None:
              if req['data'][0] == PP_COMMAND_SEND_PARM:
                req['callback']([{'status': PP_STATUS_TIMEOUT_ANSWER, 'data': None}])
              else:
                req['callback'](PP_STATUS_TIMEOUT_ANSWER)
        self.__pending_requests = filtered_requests

        # Match the propar_message with a sent request (by matching sequence numbers)
        request = None
        for req in self.__pending_requests:
          if req['message']['seq'] == propar_message['seq']:
            request = req
            break

        # Debug info of the match
        if self.debug_requests:
          print("Pending   Requests", len(self.__pending_requests))
          print("Processed Requests", len(self.__processed_requests))
          if request:
            print("Received Message:", propar_message)
            print("Matches  Request:", request)
          else:
            print("Received Unmatched Message:", propar_message)

        # If we dont match, this might be broadcast data
        if request == None:
          if propar_message['data'][0] == PP_COMMAND_SEND_PARM_BROADCAST and self.broadcast_callback:
            try:
              # Read parameter objects from broadcast message
              parameters = self.propar_builder.read_pp_send_parameter_message(propar_message)
			        # Read parameter objects from database (for each parameter in broadcast message)
              org_parameters = []
              for recv_parm in parameters:
                org_parameters.append(self.db.get_propar_parameter(recv_parm['proc_nr'], recv_parm['parm_nr'])[0])
              # Fix types based on requested types
              parameters = self.__fix_parameters(org_parameters, parameters)
              # Call broadcast callback function
              self.broadcast_callback(parameters)
            except:
              pass
        # If we matched to a request
        else:
          parameters = None
          # A status or error message with callback (write ack)
          if propar_message['data'][0] == PP_COMMAND_STATUS and request['callback'] != None:
            # When callback is used, return the status (just the status), else pass a message
            if request['message']['data'][0] == PP_COMMAND_SEND_PARM_WITH_ACK:
              request['callback'](propar_message['data'][1])
            else:
              request['callback']([{'status': propar_message['data'][1], 'data': None}])
          # Read data (response to parameter request)
          elif propar_message['data'][0] == PP_COMMAND_SEND_PARM:
            if request['message']['data'][0] == PP_COMMAND_REQUEST_PARM:
              # read parameter objects from response message
              parameters = self.propar_builder.read_pp_send_parameter_message(propar_message)
              # Update data of received parameters with data type and values of requested parameters
              parameters = self.__fix_parameters(request['parameters'], parameters)
              # Call callback if present
              if request['callback'] != None:
                request['callback'](parameters)
          # The message is now processed (our tx resulting in an rx message)
          # add it to the processed buffer (read from read/write_parameter if no callback used)
          if request['callback'] == None:
            self.__processed_requests.append({'message': propar_message, 'parameters': parameters, 'request': request, 'age': time.time()})

          # delete the now old pending request.
          self.__pending_requests.remove(request)

      
  def __next_seq(self):
    """Get next sequence number"""
    with self.seq_lock:
      self.seq += 1
      if self.seq > 255:
        self.seq = 0
    return self.seq    
      
      
  def __get_size(self, parameter_type):
    """Get size for parameter type"""
    if parameter_type == PP_TYPE_INT8:
      return 1
    elif parameter_type in [PP_TYPE_INT16, PP_TYPE_SINT16, PP_TYPE_BSINT16]:
      return 2
    elif parameter_type in [PP_TYPE_INT32, PP_TYPE_FLOAT]:
      return 4
    else: # PP_TYPE_STRING
      return 0
      
      
  def read(self, address, proc_nr, parm_nr, parm_type):
    """Read a single parameter.
    
    Args:
      address (int): instrument node address.
      proc_nr (int): process number.
      parm_nr (int): parameter number.
      parm_type (int): parameter type.

    Returns:
      Parameter value if successful, None otherwise.
    """
    parm = {}
    parm['node'     ] = address
    parm['proc_nr'  ] = proc_nr
    parm['parm_nr'  ] = parm_nr
    parm['parm_type'] = parm_type
    resp = self.read_parameters([parm])    
    if resp:
      for r in resp:
        return r['data']
    else:
      return None

  def write(self, address, proc_nr, parm_nr, parm_type, data):
    """Write a single parameter.
    
    Args:
      address (int): instrument node address.
      proc_nr (int): process number.
      parm_nr (int): parameter number.
      parm_type (int): parameter type.
      data: parameter data.

    Returns:
      True if successful, False otherwise.
    """
    parm = {}
    parm['node'     ] = address
    parm['proc_nr'  ] = proc_nr
    parm['parm_nr'  ] = parm_nr
    parm['parm_type'] = parm_type
    parm['data'     ] = data
    resp = self.write_parameters([parm])
    return resp == PP_STATUS_OK    
      
      
  def read_parameters(self, parameters, callback=None):  
    """Read multiple parameters.
    
    From a list of parameter objects.

    Args:
      parameters (list): List of parameter objects to read.
      callback (func, optional): Function to call when parameters are received (parameters passed in callback).

    Returns:
      List with parameters with data if successful, list with one status item otherwise.
      When callback is used this will return None.
    """
    request_message = {}    
    
    # Add parm_size (from type) and add proc_index and parm_index (= proc_nr and parm_nr)
    for parameter in parameters:
      if 'parm_size' not in parameter:
        parameter['parm_size'] = self.__get_size(parameter['parm_type'])      
      parameter['proc_index'] = parameter['proc_nr']
      parameter['parm_index'] = parameter['parm_nr']
        
    # Fill request message with node address and sequence number
    request_message['node'] = parameters[0]['node']
    request_message['seq' ] = self.__next_seq()        
    
    # Build the request message (will update length and data fields)
    request_message = self.propar_builder.build_pp_request_parameter_message(request_message, parameters)     
    # Add this message to the pending requests list
    request = {'message': request_message, 'parameters': parameters, 'age': time.time(), 'callback': callback}
    self.__pending_requests.append(request)
      
    # Write the message to the propar interface
    self.propar.write_propar_message(request_message)
    
    if callback != None:
      return None
    else:
      # Wait for processed response to appear magically!
      timeout_time = time.time() + self.response_timeout    
      response = None
      while time.time() <= timeout_time and response == None:
        time.sleep(0.00001)
        for resp in self.__processed_requests:
          if resp['message']['seq'] == request_message['seq']:
            if resp['request'] != request: # Stale request, remove
              self.__processed_requests.remove(resp) 
            else:
              response = resp
              self.__processed_requests.remove(resp) 
              break
      
      # no response, timeout
      if response is None:
        return [{'status': PP_STATUS_TIMEOUT_ANSWER, 'data': None}]        
      # parameter data
      elif 'parameters' in response and response['parameters'] is not None:
        return response['parameters']
      # error code status
      elif len(response['message']['data']) == 1:  # this is an error
        return [{'status': 0x80 + response['message']['data'][0], 'data': None}]  # return a parameter with error code (+ 0x80)
      # status code status
      else:
        return [{'status':        response['message']['data'][1], 'data': None}]  # return a parameter with status code
          
      
  def write_parameters(self, parameters, command=PP_COMMAND_SEND_PARM_WITH_ACK, callback=None):  
    """Write multiple parameters.
    
    Args:
      parameters: List of parameter objects, with data.
      command (int, optional): Propar command to use for writing.
      callback (func, optional): Function to call when parameters are received (parameters passed in callback).

    Returns:
      Propar status code (0 if successful, or callback is used).
    """
    write_message = {}   
    
    # Add parm_size (from type) and add proc_index and parm_index (= proc_nr and parm_nr)
    for parameter in parameters:
      if 'parm_size' not in parameter:
        parameter['parm_size'] = self.__get_size(parameter['parm_type'])      
      parameter['proc_index'] = parameter['proc_nr']
      parameter['parm_index'] = parameter['parm_nr']

    # Setup the final fields, and build the message.
    write_message['node'] = parameters[0]['node']
    write_message['seq' ] = self.__next_seq()    
    write_message = self.propar_builder.build_pp_send_parameter_message(write_message, parameters, command)
    
    if command == PP_COMMAND_SEND_PARM_WITH_ACK:
      request = {'message': write_message, 'parameters': parameters, 'age': time.time(), 'callback': callback}
      self.__pending_requests.append(request)
    
    if self.debug:
      print("Sent Message:", write_message)
      
    self.propar.write_propar_message(write_message)
    
    if command == PP_COMMAND_SEND_PARM_WITH_ACK and callback == None:
      # Wait for processed response to appear magically!
      timeout_time = time.time() + self.response_timeout    
      response = None
      while time.time() <= timeout_time and response == None:      
        time.sleep(0.00001)
        for resp in self.__processed_requests:
          if resp['message']['seq'] == write_message['seq']:
            if resp['request'] != request: # Stale request, remove
              self.__processed_requests.remove(resp) 
            else:
              response = resp
              self.__processed_requests.remove(resp) 
              break
      if response is None:
        return PP_STATUS_TIMEOUT_ANSWER
      else:
        return resp['message']['data'][1]
    else:
      return PP_STATUS_OK




class database(object):
  """The database class is used to convert FlowDDE numbers to propar parameter objects.
  
    Several other supporting functions are also provided for manual use.
  """

  def __init__(self, database_path=None):
    #Columns:
    #Parameter	LongName	Name	Available	Group0	Group1	Group2	Process	FBnr	VarType	VarType2	VarLength	Min	Max	Read	Write	Poll	Advanced	Secured	Highly secured	Default	Description
    # Import database
    parm_list      = parameters.parameters['allparameters']
    self.parm_vals = parameters.parameters['parvalue']
    self.dde_dict  = {}
    self.pp_dict   = {}
    # Create dicts for faster access to parameters
    for parm in self.__rows_to_parms(parm_list):
      # Create dde dict
      self.dde_dict[parm['dde_nr']] = parm
      # Create propar dict
      proc_nr = parm['proc_nr']
      parm_nr = parm['parm_nr']
      if proc_nr not in self.pp_dict.keys():          
        self.pp_dict[proc_nr] = {}
      if parm_nr not in self.pp_dict[proc_nr].keys():
        self.pp_dict[proc_nr][parm_nr] = []
      self.pp_dict[proc_nr][parm_nr].append(parm)


  def __rows_to_parms(self, rows):
    type_conv = {'c': PP_TYPE_INT8,
                 'i': PP_TYPE_INT16,
                 'l': PP_TYPE_INT32,
                 'f': PP_TYPE_FLOAT}
    parms = []
    for r in rows:
      p = {}
      p['dde_nr'   ] = int(r['parameter'])
      if r['process'] == '': r['process'] = '1'
      p['proc_nr'] = int(r['process'])
      p['parm_nr'] = int(r['fbnr'])
      p['parm_type'] = type_conv[r['vartype']]
      # Set extended int types if required.
      if p['parm_type'] == PP_TYPE_INT16:
        # regular signed int
        if int(r['min']) == -32767:
          p['parm_type'] = PP_TYPE_SINT16
        # bronkhorst signed int
        elif int(r['min']) == -23593:
          p['parm_type'] = PP_TYPE_BSINT16
      if r['varlength'] != '':
        p['parm_type'] = PP_TYPE_STRING
      p['parm_name'] = r['longname']
      parms.append(p)
    return parms

  def get_all_parameters(self):
    """Get a list containing all known parameter objects."""
    return [dict(obj) for obj in self.dde_dict.values()]

  def get_parameters(self, dde_parameter_nrs):
    """Get propar parameter objects from a list of DDE nrs.
    
    Args:
      dde_parameter_nrs (list:int): List of DDE nrs.

    Returns:
      A list of corresponding propar parameter objects.
    """
    parms = []
    for dde_nr in dde_parameter_nrs:
      parms.append(self.get_parameter(dde_nr))
    return parms

  def get_parameter(self, dde_parameter_nr):
    """Get a propar parameter object for the given DDE nrs.
    
    Args:
      dde_parameter_nr (int): DDE nrs.

    Returns:
      A propar parameter object.
    """
    return dict(self.dde_dict[dde_parameter_nr])

  def get_parameters_like(self, like_this):
    """Get a list of propar parameter objects that match the like_this argument.
    
    Args:
      like_this (str): String to find in parameter name.

    Returns:
      A list of matching propar parameter objects.
    """
    like_this =  like_this.lower().replace(' ', '')
    parms = [dict(obj) for obj in self.dde_dict.values() if like_this in obj['parm_name'].lower().replace(' ', '')]    
    return parms

  def get_parameter_values(self, dde_parameter_nr):
    """Get a list of possible values for for the given DDE nr..
    
    Args:
      dde_parameter_nr (int): DDE nr.

    Returns:
      A list with possible values.
    """
    rows = [dict(obj) for obj in self.parm_vals if int(obj['parameter']) == dde_parameter_nr]
    return rows

  def get_propar_parameter(self, proc_nr, parm_nr):
    """Get a list of possible propar parameter objects for the given process, parameter number combination.
    
    Args:
      proc_nr (int): Process number.
      parm_nr (int): Parameter number.

    Returns:
      A list with propar parameter objects.
    """
    try:
      return [dict(obj) for obj in self.pp_dict[proc_nr][parm_nr]]
    except:
      return None

  def get_propar_parameters(self, process):
    """Get a list of possible propar parameter objects for the given process.
    
    Args:
      proc_nr (int): Process number.

    Returns:
      A list with processes, with a list of propar parameter objects per process.
    """
    try:
      return self.pp_dict[process]
    except:
      return None

    
    
    
class _propar_builder(object):
  """Contains Propar Message Functions for status/error/read/write/send/request"""

  def __init__(self, debug=False):
    self.debug = debug
    

  def create_pp_status_message(self, propar_message, status, status_pos=0):
    """Create a propar status message from status and optional status position"""
    response_message = {}
    response_message['seq' ] = propar_message['seq' ]
    response_message['node'] = propar_message['node']
    response_message['len' ] = 3
    response_message['data'] = []
    response_message['data'].append(PP_COMMAND_STATUS)
    response_message['data'].append(status)
    if status_pos <= 255:
      response_message['data'].append(status_pos)
    else:
      response_message['data'].append(255)
    return response_message


  def create_pp_error_message(self, propar_message, error):
    """Create a propar error message from error"""
    response_message = {}
    response_message['seq' ] = propar_message['seq' ]
    response_message['node'] = propar_message['node']
    response_message['len' ] = 1
    response_message['data'] = []
    response_message['data'].append(error)
    return response_message    
    

  def build_pp_send_parameter_message(self, propar_message, parameters, command = None):
    """Build propar write message from input parameters"""    

    # Preprocess parameters to setup all the required fields for chaining.
    f = 0  # First of the current process
    for i in range(len(parameters)):      
      # Start with no flags set
      parameters[i]['proc_chained'] = False
      parameters[i]['parm_chained'] = False
      # Parameter Chaining (set previous, based on current)
      if i != 0:
        if parameters[i]['proc_nr'] == parameters[i - 1]['proc_nr']:
          parameters[i - 1]['parm_chained'] = True
        else:
          parameters[i - 1]['parm_chained'] = False      
          parameters[f    ]['proc_chained'] = True
          f = i

    send_message = {}
    send_message['seq' ] = propar_message['seq' ]
    send_message['node'] = propar_message['node']
    send_message['len' ] = 0

    pos               = 0
    message           = [0 for x in range(0, 255)]
    max_message_len   = 255

    proc_index        = 0
    parm_index        = 0
    parm_chained      = False
    prev_parm_chained = False

    org_type          = 0

    if command is None:
      command = PP_COMMAND_SEND_PARM
    
    for parameter in parameters:
      values_ok = False

      if   parameter['parm_type'] == PP_TYPE_FLOAT:
        parm_type = PP_TYPE_INT32
      elif parameter['parm_type'] in [PP_TYPE_SINT16, PP_TYPE_BSINT16]:
        parm_type = PP_TYPE_INT16
      else:
        parm_type = parameter['parm_type']

      if(
          parameter['proc_nr']   <= 0x7F            and
          parameter['parm_nr']   <= 0x1F            and
          (parm_type & 0x9F)     == 0x00            and
          parameter['parm_size'] <  MAX_PP_PARM_LEN
        ):
        if(
            command == PP_COMMAND_SEND_PARM_WITH_ACK or
            command == PP_COMMAND_SEND_PARM          or
            command == PP_COMMAND_SEND_PARM_BROADCAST
          ):
          values_ok = True

      if values_ok:
        if pos == 0:
          message[0] = command
          pos += 1

        proc_index   = parameter['proc_index']
        parm_index   = parameter['parm_index']
        proc_chained = parameter['proc_chained']
        parm_chained = parameter['parm_chained']

        if parameter['proc_chained']:
          proc_index = proc_index | 0x80

        if parameter['parm_chained']:
          parm_index = parm_index | 0x80

        if (parm_chained and (max_message_len - pos) >= 2) or (not parm_chained and (max_message_len - pos) >= 3):

          if prev_parm_chained == False:
            message[pos] = proc_index
            pos += 1
            
          prev_parm_chained = parameter['parm_chained']
            
          message[pos] = parm_index | parm_type
          pos += 1

          if parm_type == PP_TYPE_INT8:
            if (max_message_len - pos) >= 1:
              if isinstance(parameter['data'], bytes):
                message[pos] = parameter['data'][0]
              else:
                message[pos] = parameter['data']
              pos += 1

          if parm_type == PP_TYPE_INT16:
            if (max_message_len - pos) >= 2:
              try:
                data = struct.unpack('2B', struct.pack('h', parameter['data']))
              except:
                try:
                  data = struct.unpack('2B', struct.pack('H', parameter['data']))
                except:
                  data = [0, 0]
              for byte in reversed(data):
                message[pos] = byte
                pos += 1

          if parm_type == PP_TYPE_INT32:
            if (max_message_len - pos) >= 4:
              if parameter['parm_type'] == PP_TYPE_FLOAT:
                try:
                  data = struct.unpack('4B', struct.pack('f', parameter['data'])) 
                except:
                  data = [0, 0]
              else:
                try:
                  data = struct.unpack('4B', struct.pack('i', parameter['data']))
                except:
                  try:
                    data = struct.unpack('4B', struct.pack('I', parameter['data']))
                  except:
                    data = [0, 0, 0, 0]
              for byte in reversed(data):
                message[pos] = byte
                pos += 1

          if parm_type == PP_TYPE_STRING:
            if (max_message_len - pos) >= 1:
              len_pos = pos
              pos += 1
              # get bytes
              if type(parameter['data']) is str:
                str_bytes = parameter['data'].encode('utf-8')
              elif type(parameter['data']) is bytes:
                str_bytes = parameter['data']
              else:
                str_bytes = str(parameter['data']).encode('utf-8')
              # get string length
              if parameter['parm_size'] == 0:
                try:
                  len_str = len(str_bytes)
                except:
                  pass
              else:
                len_str = parameter['parm_size']
              message[len_pos] = len_str
              # pad with spaces if needed
              if len_str > len(str_bytes):
                str_bytes += b' ' * (len_str - len(str_bytes))
              # adjust string length to parm_size
              for c in str_bytes:
                message[pos] = c
                pos += 1
              # zero terminate the string
              message[pos] = 0
              pos += 1
              message[len_pos] += 1 

    send_message['data'] = message[0:pos]
    send_message['len' ] = pos

    return send_message
    
    
  def build_pp_request_parameter_message(self, propar_message, parameters):
    """Build a propar request parameter message from the passed parameters.
    The passed parameters should all be destined for the same node!"""   
    request_message = {}
    request_message['seq' ] = propar_message['seq' ]
    request_message['node'] = propar_message['node']
    request_message['len' ] = 0    
    
    pos               = 0
    message           = [0 for x in range(0, 255)]
    message_len       = 0
    max_message_len   = 255
    build_ok          = False

    parm_chained      = False
    prev_proc_nr      = 0  
    prev_proc_index   = 0
    prev_parm_index   = 0
    
    for parameter in parameters:
      
      parm_chained = False
              
      if   parameter['parm_type'] == PP_TYPE_FLOAT:
        parm_type = PP_TYPE_INT32        
      elif parameter['parm_type'] in [PP_TYPE_SINT16, PP_TYPE_BSINT16]:
        parm_type = PP_TYPE_INT16
      else:
        parm_type = parameter['parm_type']

      if request_message['node'] is None:
        request_message['node'] = parameter['node']
      
      if(pos                     <  max_message_len      and
         parameter['proc_nr']    <= 0x7F                 and
         parameter['proc_index'] <= 0x7F                 and
         parameter['parm_nr']    <= 0x1F                 and
         parameter['parm_index'] <= 0x1F                 and
         (parm_type & 0x9F)      == 0x00                 and
         parameter['parm_size']  <  MAX_PP_PARM_LEN         ):
         
        if pos == 0:
          message[pos] = PP_COMMAND_REQUEST_PARM
          pos += 1
          
        if pos == 1:
          prev_proc_index = pos
          prev_parm_index = pos + 1
          
        elif prev_proc_nr != parameter['proc_nr']:
          message[prev_proc_index] = message[prev_proc_index] | 0x80
          prev_proc_index = pos
          prev_parm_index = pos + 1
          
        else:
          parm_chained = True
          message[prev_parm_index] = message[prev_parm_index] | 0x80
          prev_parm_index = pos          
          
        prev_proc_nr = parameter['proc_nr']
        
        if(((parm_chained is True  and (max_message_len - pos) >= 3)) or
           ((parm_chained is False and (max_message_len - pos) >= 4))   ):
           
          if(parm_chained is False): 
            message[pos] = parameter['proc_index']
            pos += 1

          message[pos] = parameter['parm_index'] | parm_type
          pos += 1

          message[pos] = parameter['proc_nr']
          pos += 1
          message[pos] = parameter['parm_nr'] | parm_type
          pos += 1

          if(parm_type == PP_TYPE_STRING):
            if((max_message_len - pos) >= 1):
              message[pos] = parameter['parm_size']
              pos += 1
              build_ok = True
          else:
            build_ok = True

          if build_ok:
            message_len = pos
    
    request_message['data'] = message[0:message_len]
    request_message['len' ] = message_len    
    return request_message
    
    
  def read_pp_send_parameter_message(self, propar_message):
    """Read parameter_objects from send parameter propar_message.
    Function returns a list of parameter_objects, with the sent data in the parameter_object['data'] field.
    If an error occurs during processing the error will be stored in the parameter_object['status'] field.
    """
    read_status = PP_STATUS_OK

    message_len = propar_message['len' ]
    message     = propar_message['data']

    pos = 0

    if message_len == 0:
      read_status = PP_STATUS_PROTOCOL_ERROR
    elif message[0] not in [PP_COMMAND_SEND_PARM_WITH_ACK, PP_COMMAND_SEND_PARM, PP_COMMAND_SEND_PARM_BROADCAST]:
      read_status = PP_STATUS_COMMAND
    else:
      pos = 1

    proc_chained = True
    parm_chained = False

    parameters   = []

    while pos < message_len and read_status is PP_STATUS_OK:

      parameter = {}
      parameter['data'  ] = None
      parameter['action'] = 'write'

      if parm_chained is True  and message_len - pos < 1:
        read_status = PP_STATUS_PROTOCOL_ERROR
      if parm_chained is False and message_len - pos < 2:
        read_status = PP_STATUS_PROTOCOL_ERROR

      if read_status is PP_STATUS_OK:
        if not parm_chained:
          proc_nr      = message[pos]
          pos += 1
          proc_chained = ((proc_nr & 0x80) != 0x00)

        parameter['proc_nr']      = proc_nr & 0x7F
        parameter['proc_index']   = proc_nr

        parm_nr      = message[pos]
        pos += 1
        parm_chained = ((parm_nr & 0x80) != 0x00)

        parameter['parm_type']    = parm_nr & 0x60
        parameter['parm_nr']      = parm_nr & 0x1F
        parameter['parm_index']   = parm_nr

        parameter['proc_chained'] = proc_chained
        parameter['parm_chained'] = parm_chained


        if parameter['parm_type'] == PP_TYPE_INT8:
          parameter['parm_size'] = 1
          if (message_len - pos) < parameter['parm_size']:
            read_status = PP_ERROR_PROTOCOL_ERROR
          else:
            parameter['data'] = message[pos]
            pos += 1

        elif parameter['parm_type'] == PP_TYPE_INT16:
          parameter['parm_size'] = 2
          if (message_len - pos) < parameter['parm_size']:
            read_status = PP_ERROR_PROTOCOL_ERROR
          else:
            parameter['data'] = int.from_bytes(bytes(message[pos:pos+2]), byteorder='big')
            pos += 2

        elif parameter['parm_type'] == PP_TYPE_INT32:
          parameter['parm_size'] = 4
          if (message_len - pos) < parameter['parm_size']:
            read_status = PP_ERROR_PROTOCOL_ERROR
          else:
            parameter['data'] = int.from_bytes(bytes(message[pos:pos+4]), byteorder='big')
            pos += 4

        elif parameter['parm_type'] == PP_TYPE_STRING:
          if (message_len - pos) < 1:
            read_status = PP_ERROR_PROTOCOL_ERROR
          else:
            # Get string length from message
            parameter['parm_size'] = message[pos]
            pos += 1

            # Max possible length of current string in this message
            slen = message_len - pos

            # Calculate string length (including zero terminator)
            if parameter['parm_size'] == 0:
              cnt = pos
              while message[cnt] != 0 and cnt < message_len:
                cnt += 1
              parameter['parm_size'] = cnt - pos
              # Data is string + null byte
              data_size = parameter['parm_size'] + 1
            else:
              # Data is string + without null byte
              data_size = parameter['parm_size']

            # Check string length
            if parameter['parm_size'] > slen:
              read_status = PP_ERROR_PROTOCOL_ERROR              
            elif parameter['parm_size'] > MAX_PP_PARM_LEN - 1:
              # Decode string and store data
              string_bytes = bytes(message[pos:pos+parameter['parm_size']])
              parameter['data'] = string_bytes
            else:
              # Decode string and store data
              string_bytes = bytes(message[pos:pos+parameter['parm_size']])
              try:
                parameter['data'] = string_bytes.decode('utf-8')
              except:
                parameter['data'] = string_bytes

            # Increase pos for messsage decoding    
            pos += data_size

      parameter['status'    ] = read_status
      parameter['status_pos'] = pos

      parameters.append(parameter)
    return parameters

      
  def read_pp_request_parameter_message(self, propar_message):
    """Read parameter_objects from request parameter propar_message.
    Function returns a list of parameter_objects.
    If an error occurs during processing the error will be stored in the parameter_object['status'] field.
    """
    read_status = PP_STATUS_OK

    message_len = propar_message['len' ]
    message     = propar_message['data']

    pos = 0
    proc_index = 0
    parm_index = 0

    if message_len == 0:
      read_status = PP_STATUS_PROTOCOL_ERROR
    elif message[0] != PP_COMMAND_REQUEST_PARM:
      read_status = PP_STATUS_COMMAND
    else:
      pos = 1

    proc_chained = True
    parm_chained = False

    while pos < message_len and read_status is PP_STATUS_OK:
      parameter = {}
      parameter['data'  ] = None
      parameter['action'] = 'read'

      if proc_chained is False and parm_chained is False:
        read_status = PP_STATUS_PROTOCOL_ERROR
      if parm_chained is True  and message_len - pos < 3:
        read_status = PP_STATUS_PROTOCOL_ERROR
      if parm_chained is False and message_len - pos < 4:
        read_status = PP_STATUS_PROTOCOL_ERROR

      if read_status is PP_STATUS_OK:
        if not parm_chained:
          proc_index = message[pos]
          pos += 1
          proc_chained = ((proc_index & 0x80) != 0x00)

        parameter['proc_index']   = proc_index & 0x7F

        parm_index = message[pos]
        pos += 1
        parm_chained = ((parm_index & 0x80) != 0x00)

        parameter['parm_type']    = parm_index & 0x60
        parameter['parm_index']   = parm_index & 0x1F

        proc_nr                   = message[pos]
        pos += 1
        parameter['proc_nr']      = proc_nr & 0x7F

        parm_nr                   = message[pos]
        pos += 1
        parameter['parm_nr']      = parm_nr & 0x1F

        parameter['proc_chained'] = proc_chained
        parameter['parm_chained'] = parm_chained

        if (parm_nr & 0x60) != parameter['parm_type']:
          read_status = PP_STATUS_PARM_TYPE

        if parameter['parm_type'] == PP_TYPE_INT8:
          parameter['parm_size'] = 1
        elif parameter['parm_type'] == PP_TYPE_INT16:
          parameter['parm_size'] = 2
        elif parameter['parm_type'] == PP_TYPE_INT32:
          parameter['parm_size'] = 4
        elif parameter['parm_type'] == PP_TYPE_STRING:
          if (message_len - pos) < 1:
            read_status = PP_STATUS_PROTOCOL_ERROR
          else:
            parameter['parm_size'] = message[pos]
            pos += 1

      parameter['status'    ] = read_status
      parameter['status_pos'] = pos

      yield parameter


      
      
class _propar_provider(object):
  """Implements the propar interface for master or slave"""

  def __init__(self, baudrate, comport, debug=False, dump=0, mode=PP_MODE_BINARY, serial_class=serial.Serial):
    """Implements the propar interface for the propar_slave/master class.
    Creates a serial connection that reads binary propar messages into a queue.
    The connection can also write messages to the serial connection.

    The read and write functions require a propar_message type, which is a
    dictionary with the following fields:
    propar_message['seq']       # Sequence Number (byte)
    propar_message['node']      # Node Address (byte)
    propar_message['len']       # Data Length (byte)
    propar_message['data']      # Data (list of bytes)

    dump 0 = no dump
    dump 1 = dump non-propar
    dump 2 = dump all
    """
    try:
      self.serial = serial_class(comport, baudrate, timeout=0.01, write_timeout=0)
    except:
      raise
 
    # External flags / options
    self.debug = debug
    self.dump  = dump
    self.mode  = mode    
	
	# Additional features
    self.auto_reopen = True
    self.open_count  = 0
    self.dump_byte   = None # function that takes dumped byte / char.

    # queues for propar data packets
    self.__receive_queue  = collections.deque()
    self.__transmit_queue = collections.deque()

    # receive variables
    self.__receive_buffer      = []
    self.__receive_state       = 0
    self.__receive_error_count = 0

    # propar binary receive states
    self.RECEIVE_START_1             = 0
    self.RECEIVE_START_2             = 1
    self.RECEIVE_MESSAGE_DATA        = 2
    self.RECEIVE_MESSAGE_DATA_OR_END = 3
    self.RECEIVE_ERROR               = 4

    # propar binary start/stop/control bytes
    self.BYTE_DLE = 0x10
    self.BYTE_STX = 0x02
    self.BYTE_ETX = 0x03

    # internal flags for reader thread
    self.run    = True
    self.paused = False

    # thread for reading serial data, will put all bytes into process_propar_byte
    self.serial_read_thread = threading.Thread(target=self.serial_read_task, args=())
    self.serial_read_thread.daemon = True
    self.serial_read_thread.start()


  def set_baudrate(self, baudrate):
    self.serial.baudrate = baudrate


  def stop(self):
    self.paused = True
    self.serial.close()


  def start(self):
    self.serial.open()
    self.paused = False


  def serial_read_task(self):
    """This function is responsible for reading bytes from the serial port and
    processing the received bytes according to the binary propar protocol to
    build propar messages to put into the queue.
    This function must run in a thread.
    """
    while self.run:
      try:
        if self.paused == False:
          if self.serial.in_waiting:
            serial_data = self.serial.read(self.serial.in_waiting)
            for data_byte in serial_data:
              was_propar_byte = self.__process_propar_byte(data_byte)
              if self.dump != 0:
                if self.dump == 2 or was_propar_byte == False:
                  if self.dump_byte:
                    self.dump_byte(chr(data_byte))
                  else:
                    print(chr(data_byte), end='')
          else:
            time.sleep(0.001)
          if self.dump != 0:
            print(end='', flush=True)
        else:
          time.sleep(0.002)
      except (IOError, TypeError) as e:
        time.sleep(0.2)
        if self.auto_reopen:
          try:
            self.serial.close()
            self.serial.open()
            self.open_count += 1
          except:
            pass
      except:
        time.sleep(0.002)


  def write_propar_message(self, propar_message):
    """Writes a propar message to the serial port.
    propar_message is a dictionary containing the message seq, node, len, and
    data. This is converted to a binary or ascii propar message before sending.
    """
    if ('seq'  not in propar_message or
        'node' not in propar_message or
        'len'  not in propar_message or
        'data' not in propar_message  ):
      raise Exception("propar_message not valid!")

    if self.mode == PP_MODE_BINARY:
      msg = []
      msg.append(self.BYTE_DLE)
      msg.append(self.BYTE_STX)

      msg.append(propar_message['seq' ])
      if propar_message['seq'] == self.BYTE_DLE:
        msg.append(propar_message['seq' ])

      msg.append(propar_message['node'])
      if propar_message['node'] == self.BYTE_DLE:
        msg.append(propar_message['node'])

      msg.append(propar_message['len' ])
      if propar_message['len'] == self.BYTE_DLE:
        msg.append(propar_message['len' ])

      for byte in propar_message['data']:
        msg.append(byte)
        if byte == self.BYTE_DLE:
          msg.append(byte)

      msg.append(self.BYTE_DLE)
      msg.append(self.BYTE_ETX)

      if self.debug:
        print("TX ({:3d}): {:}".format(len(msg), ' '.join(["{:02X}".format(x) for x in msg])))

      self.serial.write(bytes(msg))
    
    else:
      # no sequence in ascii mode, but we need it to match in master
      # therefore, store it, and set it on receive (as we do request->response)
      self.last_seq = propar_message['seq']
      # convert data, build and send message
      data = ''.join(['{:02X}'.format(b) for b in propar_message['data']])
      msg  = ':{:02X}{:02X}{:}\r\n'.format(propar_message['len'] + 1, propar_message['node'], data)
      if self.debug:
        print("TX ({:3d}):".format(len(msg)), bytes(msg, encoding='ascii'))
      self.serial.write(bytes(msg, encoding='ascii'))
    

  def read_propar_message(self):
    """ Reads a propar message from the receive queue.
    Will return None when no messages are available.
    """
    try:
      return self.__receive_queue.popleft()
    except:
      return None

      
  def __get_transmit_message(self):
    """ Reads a propar message from the transmit queue.
    Will return None when no messages are available.
    """
    try:
      return self.__transmit_queue.popleft()
    except:
      return None


  def __process_propar_byte(self, received_byte):
    """Processes the received_byte following the active propar protocol (mode).
    Fully received data will be placed in the __receive_queue as a
    propar message.
    """
    was_propar_byte = True

    if self.mode == PP_MODE_BINARY:    

      if self.RECEIVE_START_1 is self.__receive_state:
        self.__receive_buffer = []
        if received_byte == self.BYTE_DLE:
          self.__receive_state = self.RECEIVE_START_2
        else:
          was_propar_byte = False

      elif self.RECEIVE_START_2 is self.__receive_state:
        if received_byte == self.BYTE_STX:
          self.__receive_state = self.RECEIVE_MESSAGE_DATA
        else:
          self.__receive_state = self.RECEIVE_ERROR

      elif self.RECEIVE_MESSAGE_DATA is self.__receive_state:
        if received_byte == self.BYTE_DLE:
          self.__receive_state = self.RECEIVE_MESSAGE_DATA_OR_END
        else:
          self.__receive_buffer.append(received_byte)

      elif self.__receive_state is self.RECEIVE_MESSAGE_DATA_OR_END:
        if received_byte == self.BYTE_DLE:
          self.__receive_buffer.append(received_byte)
          self.__receive_state = self.RECEIVE_MESSAGE_DATA
        elif received_byte == self.BYTE_ETX:
          if len(self.__receive_buffer) > 3:
            propar_message = {}
            propar_message['seq' ] = self.__receive_buffer[0 ]
            propar_message['node'] = self.__receive_buffer[1 ]
            propar_message['len' ] = self.__receive_buffer[2 ]
            propar_message['data'] = self.__receive_buffer[3:]
            self.__receive_queue.append(propar_message)
            if self.debug:
              l = self.__receive_buffer.count(0x10) + len(self.__receive_buffer)
              print("RX ({:3d}): 10 02 {:} 10 03".format(l, ' '.join(["{:02X}".format(x) for x in self.__receive_buffer])))
          self.__receive_state = self.RECEIVE_START_1
        else:
          self.__receive_state = self.RECEIVE_ERROR
    
    else: # PP_MODE_ASCII
      
      if self.RECEIVE_START_1 is self.__receive_state:
        if received_byte == 0x3A:
          self.__receive_state = self.RECEIVE_MESSAGE_DATA
          self.__receive_buffer = []
        else:
          was_propar_byte = False

      elif self.RECEIVE_MESSAGE_DATA is self.__receive_state:
        if received_byte == 0x0D:
          self.__receive_state = self.RECEIVE_MESSAGE_DATA_OR_END
        elif((received_byte >= 48 and received_byte <=  57) or 
             (received_byte >= 65 and received_byte <=  90) or
             (received_byte >= 97 and received_byte <= 122)):    
          self.__receive_buffer.append(received_byte)
        else:
          self.__receive_state = self.RECEIVE_ERROR

      elif self.RECEIVE_MESSAGE_DATA_OR_END is self.__receive_state:
        if received_byte == 0x0A:
          if len(self.__receive_buffer) > 4:
            msg = bytes(self.__receive_buffer)
            propar_message = {}
            propar_message['seq' ] = self.last_seq
            propar_message['len' ] = int(msg[0:2], 16) - 1
            propar_message['node'] = int(msg[2:4], 16)
            propar_message['data'] = []
            try:
              data = msg[4:]
              for i in range(0, len(data), 2):
                byte = int(data[i:i+2], 16) 
                propar_message['data'].append(byte)
            except:
              pass
            self.__receive_queue.append(propar_message)
            if self.debug:
              print("RX ({:3d}):".format(len(msg) + 3), b':' + msg + b'\r\n')
          self.__receive_state = self.RECEIVE_START_1
        else:
          self.__receive_state = self.RECEIVE_ERROR
        
    if self.__receive_state == self.RECEIVE_ERROR:
      self.__receive_state = self.RECEIVE_START_1
      self.__receive_error_count += 1
      if self.debug:
        print("Receive Error:", self.__receive_error_count, propar_message)        
      was_propar_byte = False

    return was_propar_byte

