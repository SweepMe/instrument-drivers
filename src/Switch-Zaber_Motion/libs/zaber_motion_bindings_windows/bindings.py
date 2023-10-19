from ctypes import cdll
import os

def load_library(name):
    file = os.path.join(os.path.dirname(__file__), name)
    return cdll.LoadLibrary(file)