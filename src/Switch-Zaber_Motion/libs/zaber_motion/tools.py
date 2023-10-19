# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List
from .call import call, call_async
from .protobufs import main_pb2


class Tools:
    """
    Class providing various utility functions.
    """

    @staticmethod
    def list_serial_ports(
    ) -> List[str]:
        """
        Lists all serial ports on the computer.

        Returns:
            Array of serial port names.
        """
        request = main_pb2.EmptyRequest()
        response = main_pb2.ToolsListSerialPortsResponse()
        call("tools/list_serial_ports", request, response)
        return list(response.ports)

    @staticmethod
    async def list_serial_ports_async(
    ) -> List[str]:
        """
        Lists all serial ports on the computer.

        Returns:
            Array of serial port names.
        """
        request = main_pb2.EmptyRequest()
        response = main_pb2.ToolsListSerialPortsResponse()
        await call_async("tools/list_serial_ports", request, response)
        return list(response.ports)
