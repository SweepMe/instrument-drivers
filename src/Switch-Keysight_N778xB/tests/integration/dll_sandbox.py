# from __future__ import annotations
#
# import time
#
# import sys
#
# import clr
#
# import platform
# print(platform.architecture())
#
# # Import Polarization Navigator dll
# navigator_path = "C:\\Program Files\\Keysight\\Polarization Navigator\\bin"
# if navigator_path not in sys.path:
#     sys.path.insert(0, navigator_path)
#
# clr.AddReference("PolNavClient")
#
# import PyPolNav
#
# # test some functions
# print("PyPolNav.dll version:", PyPolNav.GetDLLVersion())
#
# ret = PyPolNav.SendCommand("Global", "Get Version")
# print(ret)


import ctypes
import os

# Pfad zur DLL
dll_path = r"C:\Program Files\Keysight\Polarization Navigator\bin\PolNavClient.dll"

# DLL laden
polnav = ctypes.CDLL(dll_path)

# Beispiel: Angenommen, die DLL hat eine Funktion int GetDLLVersion()
# (Du musst die Signatur der Funktion kennen!)
polnav.GetDLLVersion.restype = ctypes.c_int

polnav.PolNavC_HelloWorld()

polnav.PolNavC_SendCommand("Global", "Get Version")

version = polnav.GetDLLVersion()
print("DLL Version:", version)