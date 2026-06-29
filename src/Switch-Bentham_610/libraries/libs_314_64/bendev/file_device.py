import os, select

class FileDevice:
    def __init__(self, path):
        self.file_handle = os.open(path, os.O_RDWR)

    def write(self, data, timeout=0.5):
        lR,lW,lX = select.select([],[self.file_handle],[],timeout)
        if lW:
            os.write(self.file_handle, data)
        else:
            raise TimeoutError(f"Device timeout, unavailable for writing for {timeout} seconds")
    
    def read(self, max_characters=64, timeout=None):
        if timeout==0:
            timeout = None
        lR,lW,lX = select.select([self.file_handle],[],[], timeout)
        if not lR:
            return ""
        return os.read(self.file_handle, max_characters)

    def close(self):
        try:
            os.close(self.file_handle)
        except OSError:
            pass

    def __del__(self):
        self.close()

if __name__ == "__main__":
    f = FileDevice("/dev/hidraw2")
    f.write(b"*IDN?")
    print (f.read())
    # print (f.read(1))


