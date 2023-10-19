from ctypes import c_void_p, c_int, c_int64, c_uint8, CFUNCTYPE
from typing import Any
import platform
import sys
import importlib


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

    ext = ""
    if os_system == "linux":
        ext = ".so"
    if os_system == "darwin":
        ext = ".dylib"

    lib_name = "zaber-motion-lib-{}-{}{}".format(os_system, arch, ext)
    module_name = "zaber_motion_bindings_{}".format(os_system)
    return importlib.import_module(module_name).load_library(lib_name)  # type: ignore


lib = _load_library()

CALLBACK = CFUNCTYPE(None, c_void_p, c_int64)

c_call = lib.call
c_call.argtypes = [c_void_p, c_int64, CALLBACK, c_uint8]
c_call.restype = c_int

c_set_event_handler = lib.setEventHandler
c_set_event_handler.argtypes = [c_int64, CALLBACK]
c_set_event_handler.restype = None
