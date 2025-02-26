# MIT License
#
# Copyright 2025 FormFactor GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the “Software”), to deal in the Software without 
# restriction, including without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR 
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
# OTHER DEALINGS IN THE SOFTWARE.

"""
Velox Message Server Interface
To simplify calls from the SCI commands, many of the class methods are
defined as static.  Some class variables are required to support a
connection to the Message Server, but the individual SCI commands
do not maintain a reference to the MessageServer object. Several
class global variables are used to maintain state.
Registration with the Message Server is handled in the __init__.
"""
import re
import socket
import sys
from collections import namedtuple
from os.path import basename

REGISTRATION_MESSAGE_TEMPLATE = "FCN=1:RegisterProberApp:{0} {0} 0\n"
GET_ALL_COMMANDS_MESSAGE = "FCN=1:GetCommands:\n"

class SciException(Exception):
    """ Contains fields for:
        code : The Error Number as a string
        description : The error description
        __str__, __repr__ : A formatted description of the exception """
    def __init__(self, cmd, code, description):
        self.command = cmd
        self.code = str(code)
        self.description = description

    def __repr__(self):
        return 'Error # {0} "{1}"'.format(self.code, self.description)

    def __str__(self):
        return 'Error # {0} "{1}"'.format(self.code, self.description)


class MessageServerInterface(object):

    def __init__(self, ipaddr = 'localhost', targetSocket = 1412):
        """ Initialize a socket and register with the Velox Message Server.
            Uses the python script name as the application name to register.
        """
        global mySocket, myBytesReceived, myResponse, myCurrentCommand

        try:
            if (sys.argv[0].strip() == ''): 
                sys.argv[0] = 'PythonApp'       # set a default script name if no name is set
            appName = basename(sys.argv[0])     # get the script name being executed
            appName = appName.replace(' ', '_') # make sure there are no spaces in the name
            registrationMessage = REGISTRATION_MESSAGE_TEMPLATE.format(appName)

            myCurrentCommand = 1
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mySocket.connect((ipaddr, targetSocket))

            #register with message server
            mySocket.send(registrationMessage.encode())
            myBytesReceived = 0
            myResponse = mySocket.recv(200)
        except ConnectionRefusedError:
            errormessage = ('Error: The connection to the Velox Message Server was refused.'
                            ' It probably is not running on IP [' 
                            + str(ipaddr) + '] on Socket [' + str(targetSocket) + '].'
                            ' Start Velox or examine IP Address and Socket parameters.')

            raise Exception(errormessage)
        pass

    def __enter__(self):
        return self
        pass

    def __exit__(self, type, value, traceback):
        """ Close the socket connected to the Message Server """
        global mySocket
        mySocket.close()
        pass

    def _getcommands(self):
        ''' Return a list of all commands known to the Velox Message Server '''
        global mySocket, myBytesReceived, myResponse
        mySocket.send(GET_ALL_COMMANDS_MESSAGE.encode())
        myBytesReceived = 0
        myResponse = mySocket.recv(60000)
        message = str(myResponse.decode('utf-8'))
        # parse the list
        commands = message.split(':')[2].split(';')

        # split the list into parsed tuples
        SimpleCommandTuple = namedtuple('SimpleCommandTuple', 'section, name, number, timeout')
        scilist = []
        for x in commands:
            parts = x.split(' ')
            scilist.append(SimpleCommandTuple(parts[0], parts[1], int(parts[2]),int(parts[3])))
        return scilist
        pass

    @staticmethod
    def __parseReturnValues(valueString):
        """ The values come back from the SCI command as a string separated by spaces,
            but with embedded strings as well.  Separate the values. """

        results = []   # the values parsed to be returned
        remainingValues = valueString   # holds all values still to be parsed
        while remainingValues:
            if remainingValues.startswith('"'):     # we have a string
                parts = remainingValues.split('"', 2) # creates 3-element array with empty string, result string, and remaining results
                results.append(parts[1].strip())    # this is the result string
                tmpRemaining = parts[2].strip()     # this is the rest of the line containing result values
                if len(tmpRemaining) > 0:
                    parts = [tmpRemaining]
                else:
                    parts = []
            else:   # get value separated by a space
                parts = remainingValues.split(' ', 1)
                results.append(parts.pop(0))                

            if len(parts) > 0:
                remainingValues = parts[0].strip()  # get the rest of the values
            else:
                remainingValues = None

        return results
        pass

    @staticmethod
    def __convertReturnValues(responses):
        """ The responses are all strings.  Use the hints from the SCI Command definition
            to convert them to the proper types """
        pass

    @staticmethod
    def __parseSciCommandResponse(response):
        """ The response from Message Server has the form
            Rsp=<ID>:<Return Code>:<Return Value>
            Split the response on the : character, then split up the return values """

        # Remove trailing whitespace, usually but not always a newline
        message = str(response.decode('utf-8').rstrip())

        # we may have 0 or more values
        partsCount = message.count(':')+1
        if partsCount == 2:
            command, code = re.split(":", message)
            values = '';
        elif partsCount > 3:
            """ Handle GetDatum messages with ':' 
            within the string """
            index = message.find(":")
            command = message[:index]
            
            index2 = message.find(":", index + 1)
            code = message[index + 1:index2]

            values = message[index2 + 1:]
            values = values.strip()
        else:
            command, code, values = re.split(":", message)
            values = values.strip()

        if message.startswith('Rsp='):
            values = MessageServerInterface.__parseReturnValues(values)

        commandNumber = command.split('=')[1]
        return int(commandNumber), int(code), values

    @staticmethod
    def __sendSynchronousCommand(commandName, message=''):
        global mySocket, myBytesReceived, myResponse, myCurrentCommand

        try:
            myCurrentCommand += 1       # increment the command ID
            if myCurrentCommand == 0 or myCurrentCommand > 999:
                myCurrentCommand = 1
            messageToSend = 'Cmd={}:{}:{}\n'.format(myCurrentCommand,commandName,message)
            mySocket.send(messageToSend.encode())
            myBytesReceived = 0
            myResponse = mySocket.recv(1024)

        except Exception as e:
            raise Exception('Unable to communicate with Velox Message Server. Start Velox.' + e)

        cmd, code, values = MessageServerInterface.__parseSciCommandResponse(myResponse)

        # if the response code is not 0, raise an exception
        if code:
            parameters = ' '.join(values)
            raise SciException(cmd, code, parameters)

        return values
        pass

    @staticmethod
    def sendSciCommand(commandName, *args, **kwargs):
        """ If the parameter rparams is passed, it is the full command parameter string and should be used.
            Otherwise, join the other arguments into a string separated by spaces and send that.
            The rparams is used for legacy scripts converted from Pascal or Basic or other cases 
            where you want to send the command parameters as a single string.  """

        if 'rparams' in kwargs: # use the raw parameter string if provided
            commandParameters = kwargs['rparams']
        else: # use the positional arguments and build the parameter string
            commandParameters = ' '.join(str(x) for x in args)
        return MessageServerInterface.__sendSynchronousCommand(commandName, commandParameters)

# This globally available function is there to replace the function exposed by Scripting Console. Used by SiPTools package.
def SendSciCommand(commandName, *args, **kwargs):
    """ If the parameter rparams is passed, it is the full command parameter string and should be used.
        Otherwise, join the other arguments into a string separated by spaces and send that.
        The rparams is used for legacy scripts converted from Pascal or Basic or other cases 
        where you want to send the command parameters as a single string.  """

    return MessageServerInterface.sendSciCommand(commandName, *args, **kwargs)
