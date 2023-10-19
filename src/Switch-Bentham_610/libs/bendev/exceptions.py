# @file exceptions.py
# @author Markus Führer
# @date 7 Jan 2022
# @copyright Copyright © 2022 by Bentham Instruments Ltd. 

class ExternalDeviceNotFound(IOError):
    """The target device was not found."""
class DeviceClosed(IOError):
    """The connection to the target device is not open."""
