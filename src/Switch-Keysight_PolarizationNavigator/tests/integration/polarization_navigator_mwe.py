import ctypes


DLL_PATH = r"C:\Program Files\Keysight\Polarization Navigator\bin\PolNavClient.dll"

class PolNavClient:
    """Python client for the Polarization Navigator DLL."""

    def __init__(self) -> None:
        """Initialize the Polarization Navigator client."""
        self.client = ctypes.CDLL(DLL_PATH)

        # Define argument and return types
        self.client.PolNavC_SendCommand.argtypes = [
            ctypes.c_char_p,        # Target
            ctypes.c_char_p,        # Command
            ctypes.c_char_p,        # Response buffer (output)
            ctypes.c_int,           # MaxLen
            ctypes.POINTER(ctypes.c_int),  # ResponseLen (output by reference)
        ]
        self.client.PolNavC_SendCommand.restype = ctypes.c_int

    def hello_world(self) -> None:
        """Call the HelloWorld function from the Polarization Navigator DLL."""
        print(self.client.PolNavC_HelloWorld())

    def send_command(self, target: str, command: str, buffer_size: int = 1024) -> str:
        """Send a command to the Polarization Navigator and return the response."""
        # Create response buffer
        response_buffer = ctypes.create_string_buffer(buffer_size)
        response_len = ctypes.c_int()

        # Call the DLL function
        result = self.client.PolNavC_SendCommand(
            ctypes.c_char_p(target.encode("ascii")),
            ctypes.c_char_p(command.encode("ascii")),
            response_buffer,
            ctypes.c_int(buffer_size),
            ctypes.byref(response_len),
        )

        self.handle_error(result)

        # Return the actual response string
        return response_buffer.value.decode("ascii")

    def read(self) -> str:
        """Read the response from Polarization Navigator."""
        return self.client.PolNavC_ReadResponse()

    @staticmethod
    def handle_error(error_code: str) -> None:
        """Handle errors based on the error code returned by the DLL."""
        error = int(error_code)
        # No error
        if error == 0:
            return

        error_messages = {
            0: "No error",
            3: "Undefined function",
            7: "Memory allocation error",
            8: "Memory overflow error",
            11: "Variable type mismatch",
            17: "Generic error",
            53: "Unknown tree number",
            54: "Unknown variable",
            55: "Variable access violation",
            56: "Unknown variable type",
            57: "Parameter missing/Wrong number of parameters",
            84: "Health check error",
            99: "Target not found",
            100: "Unknown command",
            101: "Response buffer overflow",
            103: "Referencing error",
            104: "Resolution error",
            1024: "Polcontroller generic error",
            1025: "Polcontroller memory allocation error",
            1537: "Polarimeter no calibration data",
            1538: "Polarimeter calibration range",
            1539: "Polarimeter measurement timeout",
            1540: "Polarimeter measurement in progress",
            1541: "Polarimeter measurement sequence error",
            1545: "Polarimeter measurement over range",
            1546: "Polarimeter measurement under range",
        }

        msg = f"Unknown error code: {error}" if error not in error_messages else f"Error: {error_messages[error]}"
        print(msg)

if __name__ == "__main__":
    navigator = PolNavClient()

    # Sanity checks - HelloWorld, Get Version, and available targets all work
    # prints: '123'
    navigator.hello_world()

    # returns: Version 3.313 (0), Built on Aug 17 2021 08:38:08
    versions = navigator.send_command("Global", "Get Version")

    available_targets = navigator.send_command("Global", "Dir")
    targets = available_targets.split("\r\n")

    # Set SOP - works
    x = 1
    y = 0
    z = 0
    target = targets[1]
    navigator.send_command(target, "Activate")
    navigator.send_command(target, "Stabilize")
    navigator.send_command(target, f"Set TargetSOP,{x},{y},{z}")
    navigator.send_command(target, "Set Stabilize,1")
    # This works, and the new SOP can be confirmed in the Polarization Navigator GUI

    # Retrieving the current SOP does not work. The 'Get CurrentSOPN' command results in a timeout
    # No usable error message is returned, just a timeout
    navigator.send_command(target, "Get CurrentSOPN")
    sop = navigator.client.PolNavC_ReadResponse()
