import json
import builtins
import asyncio
import logging

# As SweepMe! 1.5.5 does not come with tblib, we only use it
# if it is available
try:
    from tblib import Traceback
    tblib_imported = True
except ModuleNotFoundError:
    tblib_imported = False
    
from six import reraise


logger = logging.getLogger("TCPClientProxy")


class RemoteException(Exception):
    """
    A generic exception that is raised when the server-side code encountered an exception. As there is no universal
    specification on how an exception (in particular custom exception) looks like and can be created, we have
    to use a generic one and print the original traceback and exception type as the message.
    """


class RemoteVar:
    def __init__(self, variable_reference_name):
        self._variable_reference_name = variable_reference_name


class Proxy:
    _target_class: str

    def __init__(self, address: str, port: int, target_class: str):
        self.loop = asyncio.new_event_loop()
        self._target_class = target_class
        self.address = address
        self.port = port
        
    def __del__(self):
        self.loop.close()

    def _convert_argument_from_json(self, arg):
        if isinstance(arg, list):
            return [self._convert_argument_from_json(element) for element in arg]
        arg_type = arg["type"]
        arg_value = arg["value"]
        if arg_type == "RemoteVar":
            return RemoteVar(arg_value)
        elif arg_type == "NoneType":
            return None
        return getattr(builtins, arg_type)(arg_value)

    def _convert_argument_to_json(self, arg):
        # tuples become lists in json anyway, so treat them the same here
        if isinstance(arg, list) or isinstance(arg, tuple):
            return [self._convert_argument_to_json(element) for element in arg]
        arg_type = type(arg).__name__
        # complex types are not transferred but saved locally and only a reference is sent back
        if arg_type == "RemoteVar":
            arg = arg._variable_reference_name
        return {
            "type": arg_type,
            "value": arg
        }

    async def _async_send_to_server(self, command: str) -> str:
        reader, writer = await asyncio.open_connection(
            self.address, self.port)

        writer.write(command.encode("utf-8") + b'\n')
        await writer.drain()

        data = await reader.readline()

        writer.close()
        return data.decode("utf-8")

    def _send_to_server(self, command: str) -> str:
        result = self.loop.run_until_complete(self._async_send_to_server(command))
        return result

    def unpack_result(self, response):
        result = json.loads(response)
        status = result.get("status", "invalid")
        if status == "success":
            return result
        if status == "exception":
            message = result["message"]
            
             # only used if tblib was imported 
            if tblib_imported:
                tb = Traceback.from_dict(result["traceback"]).as_traceback() 
            else:
                tb = None

            reraise(
                RemoteException,
                RemoteException(f"Server-side processing failed with {message}"),
                tb,
                )
                
        raise Exception("Error decoding the response from the server")

    def __getattr__(self, function):
        def handle_call(*args, **kwargs):
            args = args or []
            kwargs = kwargs or {}
            command_json = {
                "class": self._target_class,
                "function": function,
                "args": [self._convert_argument_to_json(arg) for arg in args],
                "kwargs": {k: self._convert_argument_to_json(v) for k, v in kwargs.items()}
            }
            command = json.dumps(command_json)
            logger.debug(f"Request: {command}")
            result = self._send_to_server(command)
            logger.debug(f"Response: {result}")
            result_json = self.unpack_result(result)
            return self._convert_argument_from_json(result_json["return"])

        if function[0] != "_":
            # try to determine if it is an attribute and not a function
            command_json = {
                "class": self._target_class,
                "attribute": function
            }
            command = json.dumps(command_json)
            result = self._send_to_server(command)
            result_json = self.unpack_result(result)
            if result_json["return"]["type"] == "callable":
                return handle_call
            logger.debug(f"Request: {command}")
            logger.debug(f"Response: {result}")
            return self._convert_argument_from_json(result_json["return"])
        return None
