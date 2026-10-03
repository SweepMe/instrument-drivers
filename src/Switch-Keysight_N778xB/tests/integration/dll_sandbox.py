import ctypes


DLL_PATH = r"C:\Program Files\Keysight\Polarization Navigator\bin\PolNavClient.dll"

class PolNavClient:

    def __init__(self):

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

        # Check for success
        if result != 0:
            msg = f"PolNav_SendCommand failed with error code: {result}"
            print(msg)
            # raise RuntimeError(msg)

        # Return the actual response string
        return response_buffer.value.decode("ascii")

    def read(self) -> str:
        """Read the response from Polarization Navigator."""
        return self.client.PolNavC_ReadResponse()

    def set_sop(self, value_str: str = "1,1,1") -> None:
        """Set the state of polarization (SOP) to a specific value."""
        pol_controller = "PolCon*"
        self.send_command(pol_controller, "Activate")
        self.send_command(pol_controller, "Stabilize")
        self.send_command(pol_controller, f"Set TargetSOP,{value_str}")
        self.send_command(pol_controller, "Set Stabilize,1")
        self.send_command(pol_controller, "Get CurrentSOPN")

        print(self.read())


if __name__ == "__main__":
    nav = PolNavClient()
    ret = nav.send_command("Global", "Get Version")
    print(ret)

    available_targets = nav.send_command("Global", "Dir")

    # turn the string into a list
    targets = available_targets.split("\r\n")
    if "Global" in targets:
        targets.remove("Global")

    print("Available Targets:" + str(targets))
    nav.set_sop()
