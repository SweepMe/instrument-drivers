"""Test the SOCKET communication with the iseg SHR."""
import socket
import time

IP_ADDRESS = "192.168.178.30"
PORT = "10001"


class Port:
    def __init__(self):
        self.eol = "\r\n"
        self.buffer: str = ""
        self.buffer_size = 1024

        self.port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port.settimeout(5)  # Set a timeout for the connection attempt
        self.port.connect((IP_ADDRESS, int(PORT)))

    def write(self, command: str) -> None:
        """Send a command to the device."""
        self.port.sendall(f"{command}{self.eol}".encode())

    def read(self) -> str:
        """Read a response from the device."""
        while True:
            # print(len(self.buffer))
            idx = self.buffer.find(self.eol)
            if idx != -1:
                # If the end of line is found, split the buffer
                response = self.buffer[:idx + len(self.eol)]
                self.buffer = self.buffer[idx + len(self.eol) :]
                response = response.strip(self.eol)
                print("Response: ", response, len(response), repr(response))
                # This should be driver specific
                if not response:
                    continue

                return response

            chunk = self.port.recv(self.buffer_size).decode()
            if not chunk:
                # End of Stream
                if self.buffer:
                    line = self.buffer
                    self.buffer = ""
                    print(line)
                    return line
                return ""
            self.buffer += chunk

    def query(self, command: str) -> str:
        """Send a command and read the response."""
        self.clear()
        self.write(command)
        return self.read()

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer = ""

if __name__ == "__main__":
    channel = 0

    port = Port()
    port.query("*IDN?")
    port.write("*CLS")
    port.write("*RST")
    port.query(f":READ:VOLT:ON? (@{channel})")
    # port.get_non_empty_line()
    port.write(f":VOLT ON,(@{channel})")
    port.write(f":VOLT 10,(@{channel})")
    time.sleep(10)
    port.write(f":VOLT 15,(@{channel})")
    time.sleep(5)
    port.write(f":VOLT OFF,(@{channel})")







