"""
Contains ComModbus class to configure and communicate with EDrive devices.

This implementation uses the pymodbus library
https://pymodbus.readthedocs.io/en/latest/index.html
"""
import threading
import time
import traceback
from pymodbus.client.tcp import ModbusTcpClient as ModbusClient
from pymodbus.mei_message import ReadDeviceInformationRequest
from edcon.utils.logging import Logging
from edcon.edrive.com_base import ComBase

REG_OUTPUT_DATA = 0
REG_INPUT_DATA = 100
REG_TIMEOUT = 400

IO_DATA_SIZE = 56

REG_PNU_MAILBOX_PNU = 500
REG_PNU_MAILBOX_SUBINDEX = 501
REG_PNU_MAILBOX_NUM_ELEMENTS = 502
REG_PNU_MAILBOX_EXEC = 503
REG_PNU_MAILBOX_DATA_LEN = 504
REG_PNU_MAILBOX_DATA = 510

PNU_MAILBOX_EXEC_READ = 0x01
PNU_MAILBOX_EXEC_WRITE = 0x02
PNU_MAILBOX_EXEC_ERROR = 0x03
PNU_MAILBOX_EXEC_DONE = 0x10


class IOThread(threading.Thread):
    """Class to handle I/O transfers in a separate thread."""

    def __init__(self, perform_io=None, cycle_time: int = 10):
        """Constructor of the IOThread class.

        Parameters:
            perform_io (function): function that is called periodically (with interval cycle_time)
                                   and performs the I/O data transfer
            cycle_time (int): Cycle time (in ms) that should be used for I/O transfers
        """
        self.perform_io = perform_io
        self.cycle_time = cycle_time
        self.active = False
        self.exe_event = threading.Event()
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        """Method that needs to be implemented by child."""
        while self.active:
            try:
                self.perform_io()
                self.exe_event.set()
                self.exe_event.clear()
            except Exception:
                traceback.print_exc()
                self.stop()
                raise
            time.sleep(self.cycle_time * 0.001)

    def start(self):
        """Starts the thread."""
        self.active = True
        super().start()

    def stop(self):
        """Stops the thread."""
        self.active = False


class ComModbus(ComBase):
    """Class to configure and communicate with EDrive devices via Modbus."""

    def __init__(self, ip_address, cycle_time: int = 10, timeout_ms: int = 1000):
        """Constructor of the ComModbus class.

        Parameters:
            ip_address (str): Required IP address as string e.g. ('192.168.0.1')
            cycle_time (int): Cycle time (in ms) that should be used for I/O transfers
            timeout_ms (int): Modbus timeout (in ms) that should be configured on the slave
        """
        self.io_thread = IOThread(self.perform_io, cycle_time)

        Logging.logger.info(f"Starting Modbus connection on {ip_address}")
        self.modbus_client = ModbusClient(ip_address)
        self.modbus_client.connect()

        self.device_info = self.read_device_info()

        self.in_data = b'\x00' * IO_DATA_SIZE
        self.out_data = b'\x00' * IO_DATA_SIZE

        self.set_timeout(timeout_ms)

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        """Tries stop the communication thread and closes the modbus connection"""
        if hasattr(self, 'io_thread'):
            self.io_thread.stop()

        if hasattr(self, 'modbus_client'):
            self.modbus_client.close()

    def read_device_info(self) -> dict:
        """Reads device info from the CMMT and returns dict with containing values

        Returns:
            dict: Contains device information values
        """
        dev_info = {}

        # Read device information
        rreq = ReadDeviceInformationRequest(0x1, 0)
        rres = self.modbus_client.execute(rreq)
        dev_info["vendor_name"] = rres.information[0].decode('ascii')
        dev_info["product_code"] = rres.information[1].decode('ascii')
        dev_info["revision"] = rres.information[2].decode('ascii')

        rreq = ReadDeviceInformationRequest(0x2, 0)
        rres = self.modbus_client.execute(rreq)
        dev_info["vendor_url"] = rres.information[3].decode('ascii')
        dev_info["product_name"] = rres.information[4].decode('ascii')
        dev_info["model_name"] = rres.information[5].decode('ascii')

        for key, value in dev_info.items():
            Logging.logger.info(f"{key.replace('_',' ').title()}: {value}")

        return dev_info

    def set_timeout(self, timeout_ms) -> bool:
        """Sets the modbus timeout to the provided value"""
        Logging.logger.info(f"Setting modbus timeout to {timeout_ms} ms")
        self.modbus_client.write_registers(REG_TIMEOUT, [timeout_ms, 0])
        # Check if it actually succeeded
        indata = self.modbus_client.read_holding_registers(REG_TIMEOUT, 1)
        if indata.registers[0] != timeout_ms:
            Logging.logger.error("Setting of modbus timeout was not successful")
            return False
        return True

    def perform_io(self):
        """Reads input data from and writes output data to according modbus registers."""
        # Inputs, convert to bytes
        indata = self.modbus_client.read_holding_registers(
            REG_INPUT_DATA, int(IO_DATA_SIZE/2))
        self.in_data = b''.join(reg.to_bytes(2, 'little')
                                for reg in indata.registers)

        # Outputs, convert to list of modbus words
        word_list = [int.from_bytes(self.out_data[i:i+2], 'little')
                     for i in range(0, len(self.out_data), 2)]
        self.modbus_client.write_registers(REG_OUTPUT_DATA, word_list)

    def read_pnu_raw(self, pnu: int, subindex: int = 0, num_elements: int = 1) -> bytes:
        """Reads a PNU from the EDrive without interpreting the data"""
        try:
            self.modbus_client.write_register(REG_PNU_MAILBOX_PNU, pnu)
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_SUBINDEX, subindex)
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_NUM_ELEMENTS, num_elements)

            # Execute
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_EXEC, PNU_MAILBOX_EXEC_READ)
            status = self.modbus_client.read_holding_registers(
                REG_PNU_MAILBOX_EXEC, 1).registers[0]

            if status != PNU_MAILBOX_EXEC_DONE:
                Logging.logger.error(f"Error reading PNU {pnu}, status: {status}")
                return None

            # Read available data length
            length = self.modbus_client.read_holding_registers(
                REG_PNU_MAILBOX_DATA_LEN, 1).registers[0]

            # Divide length by 2 because each register is 2 bytes
            indata = self.modbus_client.read_holding_registers(
                510, int((length+1)/2))

            # Convert to integer
            data = b''.join(reg.to_bytes(2, 'little')
                            for reg in indata.registers)
            Logging.logger.info(
                f"Successful read of PNU {pnu} (subindex: {subindex}): {data})")
            return data

        except (AttributeError, IndexError):
            Logging.logger.error("Could not access PNU register")
            return None

    def write_pnu_raw(self, pnu: int, subindex: int = 0, num_elements: int = 1,
                      value: bytes = b'\x00') -> bool:
        """Writes raw bytes to a PNU on the EDrive"""
        try:
            self.modbus_client.write_register(REG_PNU_MAILBOX_PNU, pnu)
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_SUBINDEX, subindex)
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_NUM_ELEMENTS, num_elements)
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_DATA_LEN, len(value))

            # Convert to list of words
            word_list = [int.from_bytes(value[i:i+2], 'little')
                         for i in range(0, len(value), 2)]
            # Write data
            self.modbus_client.write_registers(510, word_list)

            # Execute
            self.modbus_client.write_register(
                REG_PNU_MAILBOX_EXEC, PNU_MAILBOX_EXEC_WRITE)
            status = self.modbus_client.read_holding_registers(
                REG_PNU_MAILBOX_EXEC, 1).registers[0]
            if status != PNU_MAILBOX_EXEC_DONE:
                Logging.logger.error(f"Error writing PNU {pnu}, status: {status}")
                return False

            Logging.logger.info(
                f"Successful write of PNU {pnu} (subindex: {subindex}): {value} ")
            return True

        except AttributeError:
            traceback.print_exc()
            Logging.logger.error("Could not access PNU register")
            return False

    def start_io(self):
        """Starts i/o data process"""
        self.io_thread.start()

    def stop_io(self):
        """Stops i/o data process"""
        self.send_io(b'\x00' * IO_DATA_SIZE)
        self.io_thread.stop()

    def send_io(self, data: bytes, nonblocking: bool = False):
        """Sends data to the output

        Parameters:
            nonblocking (bool): If True, function returns immediately.
                                Otherwise function awaits I/O thread to be executed.
        """
        if not self.io_thread.active:
            return
        self.out_data = data
        if not nonblocking:
            self.io_thread.exe_event.wait()

    def recv_io(self, nonblocking: bool = False) -> bytes:
        """Receives data from the input

        Parameters:
            nonblocking (bool): If True, function returns immediately.
                                Otherwise function awaits I/O thread to be executed.
        """
        if not self.io_thread.active:
            return None
        if not nonblocking:
            self.io_thread.exe_event.wait()
        return self.in_data
