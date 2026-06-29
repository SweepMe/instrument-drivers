from ctypes import c_void_p, c_int, c_int64, c_uint8, CFUNCTYPE, cdll
from typing import Any
from os import path
import platform
import sys


def _load_library() -> Any:
    is64bit = sys.maxsize > 2**32
    os_system = platform.system().lower()
    os_machine = platform.machine().lower()

    if os_system == "darwin":
        arch = "uni"
    else:
        if os_machine.startswith("aarch64") or os_machine.startswith("arm"):
            arch = "arm64" if is64bit else "arm"
        else:
            arch = "amd64" if is64bit else "386"

    if os_system == "linux":
        ext = ".so"
    elif os_system == "darwin":
        ext = ".dylib"
    elif os_system == "windows":
        ext = ".dll"
    else:
        raise ImportError(f"Unsupported operating system {os_system}")

    lib_name = f"zaber-motion-core-{os_system}-{arch}{ext}"
    lib_path = path.join(path.dirname(__file__), "..", "zaber_motion_bindings", lib_name)
    lib_path = path.normpath(lib_path)

    if not path.exists(lib_path):
        lib_dir = path.dirname(lib_path)
        raise ImportError(f"Could not find library {lib_name} at path {lib_dir}. Please contact Zaber support.")
    return cdll.LoadLibrary(lib_path)


lib = _load_library()

CALLBACK = CFUNCTYPE(None, c_void_p, c_int64)

c_call = lib.zml_call
c_call.argtypes = [c_void_p, c_int64, CALLBACK, c_uint8]
c_call.restype = c_int

c_set_event_handler = lib.zml_setEventHandler
c_set_event_handler.argtypes = [c_int64, CALLBACK]
c_set_event_handler.restype = None
