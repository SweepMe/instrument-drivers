# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! driver
# * Module: Camera
# * Instrument: PC Webcam

from __future__ import annotations

import ctypes
import sys
import uuid
from pathlib import Path
from typing import Annotated, Any, Literal

import cv2
import numpy as np
from pysweepme.commands import Elements, Label, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call).
Intensity = Annotated[int, Label("Intensity")]  # one color value of a pixel, 0 to 255
Image = Annotated[np.ndarray, Elements(Intensity)]  # height x width x 3, RGB, uint8
FileFormat = Literal["jpg", "png"]

# Highest camera index find_ports tries; OpenCV numbers the cameras from 0 without gaps.
MAX_CAMERAS = 10

# Media Foundation on Windows: its order of the cameras is the one get_identification reads. Without it, OpenCV may pick
# another backend (e.g. GStreamer where installed) that numbers the cameras differently.
BACKEND = cv2.CAP_MSMF if sys.platform == "win32" else cv2.CAP_ANY


class Device(EmptyDevice):
    """Driver for webcams and other cameras that OpenCV opens by their index (0, 1, ...)."""

    def __init__(self) -> None:
        """Define the returned variable; the camera is opened in connect()."""
        super().__init__()

        self.shortname = "Webcam"

        # The Camera module shows the picture behind the first returned value.
        self.variables = ["image path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [False]

        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.file_format: str = "jpg"
        self.camera_index: int = 0
        self.capture: cv2.VideoCapture | None = None
        self.picture_count: int = 0
        self.image_path: str = ""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields: the file format of the saved pictures."""
        return {
            "SweepMode": ["None"],
            "FileFormat": ["jpg", "png"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections; the port is the camera's index as text."""
        self.gui_parameters = parameters
        self.port_string = str(parameters.get("Port", "")).strip()
        self.file_format = parameters.get("FileFormat", "jpg")

    # check_driver: ignore DC004 - a hook of the Camera module
    def find_ports(self) -> list[str]:
        """Return the cameras as SweepMe!'s Find Ports button asks: their index, on Windows followed by what they are.

        On Windows a port reads e.g. "0: Integrated Camera, USB 04F2:B6EA rev 6218, serial 0001", taken from the list
        of Media Foundation without opening a camera; connect uses only the index in front, so a port of earlier
        versions ("0") still works. Elsewhere, or when that list cannot be read, the cameras OpenCV can open are tried.
        """
        if sys.platform == "win32":
            try:
                cameras = media_foundation_cameras()
            except OSError:
                pass
            else:
                return [f"{index}: {describe(name, link)}" for index, (name, link) in enumerate(cameras)]
        found = []
        for index in range(MAX_CAMERAS):
            capture = cv2.VideoCapture(index, BACKEND)
            opened = capture.isOpened()
            capture.release()
            if not opened:
                break
            found.append(str(index))
        return found

    def connect(self) -> None:
        """Open the camera with the index at the start of the port (0 when none is given)."""
        index = self.port_string.split(":", 1)[0].strip()
        if index and not index.isdigit():
            msg = f"The port of a webcam starts with its index (0, 1, ...), not '{self.port_string}'. Use Find Ports."
            raise ValueError(msg)
        self.camera_index = int(index) if index else 0
        self.capture = cv2.VideoCapture(self.camera_index, BACKEND)
        if not self.capture.isOpened():
            self.capture.release()
            self.capture = None
            msg = f"Camera {self.camera_index} cannot be opened. It may be in use by another program."
            raise ValueError(msg)

    def disconnect(self) -> None:
        """Release the camera, so that other programs can use it."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def initialize(self) -> None:
        """Take one picture and drop it: the first pictures of many webcams are too dark."""
        self.picture_count = 0
        self._read_frame()

    def measure(self) -> None:
        """Save a picture into the temporary folder of the run."""
        self.picture_count += 1
        name = f"temp_Webcam{self.camera_index}_{self.picture_count:03d}.{self.file_format}"
        self.image_path = str(Path(self.get_folder("TEMP")) / name)
        self.save_picture(self.image_path)

    def call(self) -> list[str]:
        """Return the path of the saved picture."""
        return [self.image_path]

    # Communication commands

    @command(returns=("image",))
    def get_image(self) -> Image:
        """Take a picture and return its pixels: height x width x 3 color values (RGB) from 0 to 255."""
        return cv2.cvtColor(self._read_frame(), cv2.COLOR_BGR2RGB)

    @command(kind="run")
    def save_picture(self, path: str) -> None:
        """Take a picture and save it to path; the file format follows the extension (.jpg, .jpeg or .png)."""
        suffix = Path(path).suffix.lower()
        if suffix not in (".jpg", ".jpeg", ".png"):
            msg = f"A picture is saved as .jpg, .jpeg or .png, not '{suffix or path}'."
            raise ValueError(msg)
        # imencode and write_bytes instead of imwrite, which fails on paths with non-ASCII characters on Windows.
        Path(path).write_bytes(self._encode(self._read_frame(), suffix))

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the camera's name, USB vendor and product id, revision and serial number, as Windows lists them.

        The serial number is the one the camera reports over USB; many webcams report none, and integrated cameras often
        a placeholder such as 0001. A camera without one says "no serial number": the id Windows makes up for it instead
        is never given as one. Takes no picture.
        """
        if sys.platform != "win32":
            msg = "Identifying a webcam is built for Windows only."
            raise NotImplementedError(msg)
        cameras = media_foundation_cameras()
        if self.camera_index >= len(cameras):
            msg = f"Windows lists {len(cameras)} camera(s); there is no camera {self.camera_index} to identify."
            raise RuntimeError(msg)
        return describe(*cameras[self.camera_index])

    # Further functions

    # check_driver: ignore DC004 - answers bytes, which a communication command never does (guide 7.5)
    def get_picture_bytes(self, file_format: FileFormat = "jpg") -> bytes:
        """Take a picture and return it as the bytes of a JPEG or PNG file, e.g. to show it live in a program.

        Not a communication command: answers of commands are no bytes (driver guide, section 7.5), so it is not
        offered as a button or to agents. Scripts and programs call it directly; save_picture writes the same bytes.
        """
        if file_format not in ("jpg", "png"):
            msg = f"The file format is 'jpg' or 'png', not '{file_format}'."
            raise ValueError(msg)
        return self._encode(self._read_frame(), f".{file_format}")

    def makePicture(self, pic_path: str) -> None:  # noqa: N802 - the name of earlier versions
        """Save a picture to pic_path; kept for scripts of earlier versions, use save_picture."""
        self.save_picture(pic_path)

    # Helpers

    def _read_frame(self) -> np.ndarray:
        """Read the next picture from the camera as OpenCV gives it (BGR)."""
        if self.capture is None:
            msg = "The camera is not connected."
            raise RuntimeError(msg)
        captured, frame = self.capture.read()
        if not captured:
            msg = f"Camera {self.camera_index} gave no picture. It may be in use by another program."
            raise RuntimeError(msg)
        return frame

    @staticmethod
    def _encode(frame: np.ndarray, suffix: str) -> bytes:
        """Encode a BGR picture as the file format of suffix (.jpg, .jpeg or .png)."""
        encoded, data = cv2.imencode(suffix, frame)
        if not encoded:
            msg = f"The picture could not be encoded as {suffix}."
            raise RuntimeError(msg)
        return data.tobytes()


# Windows device information, through Media Foundation and the configuration manager (ctypes, no further packages)

MF_VERSION = 0x00020070
"""MF_SDK_VERSION 2 and MF_API_VERSION 0x70, as MFStartup expects them."""
MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE = "c60ac5fe-252a-478f-a0ef-bc8fa5f7cad3"
MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID = "8ac3587a-4ae7-42d8-99e0-0a6013eef90f"
MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME = "60d0e559-52f8-4fa2-bbce-acdb34a8ec01"
MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK = "58f0aad8-22bf-4f8a-bb3d-d2c4978c6e2f"
RELEASE = 2
"""Place of Release in the vtable of IUnknown."""
GET_ALLOCATED_STRING = 13
"""Place of GetAllocatedString in the vtable of IMFAttributes, from which IMFActivate derives."""
SET_GUID = 24
"""Place of SetGUID in the vtable of IMFAttributes."""
CM_DRP_HARDWAREID = 0x02
RPC_E_CHANGED_MODE = -2147417850
"""COM was initialized on this thread in another mode by someone else; it can be used as it is."""


class GUID(ctypes.Structure):
    """A Windows GUID as COM functions take it."""

    _fields_ = (
        ("data1", ctypes.c_uint32),
        ("data2", ctypes.c_uint16),
        ("data3", ctypes.c_uint16),
        ("data4", ctypes.c_ubyte * 8),
    )


def guid(text: str) -> GUID:
    """Return the GUID of its text form."""
    return GUID.from_buffer_copy(uuid.UUID(text).bytes_le)


def com_call(obj: ctypes.c_void_p, index: int, *args: Any) -> int:  # noqa: ANN401 - ctypes objects of any type
    """Call method `index` of the vtable of COM object `obj` with the addresses of `args`; return its HRESULT."""
    vtable = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p)))[0]
    method = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *[ctypes.c_void_p] * len(args))(vtable[index])
    return method(obj, *[ctypes.addressof(a) for a in args])


def check(hresult: int, what: str) -> None:
    """Raise an error for a failed HRESULT."""
    if hresult < 0:
        msg = f"{what} failed with 0x{hresult & 0xFFFFFFFF:08X}."
        raise OSError(msg)


def media_foundation_cameras() -> list[tuple[str, str]]:
    """Return name and symbolic link of every camera Media Foundation lists, in its order (OpenCV's index there)."""
    ole32 = ctypes.WinDLL("ole32")
    mfplat = ctypes.WinDLL("mfplat")
    mf = ctypes.WinDLL("mf")
    ole32.CoTaskMemFree.argtypes = (ctypes.c_void_p,)
    initialized = ole32.CoInitializeEx(None, 0)  # COINIT_MULTITHREADED
    if initialized < 0 and initialized != RPC_E_CHANGED_MODE:
        check(initialized, "CoInitializeEx")
    check(mfplat.MFStartup(MF_VERSION, 0), "MFStartup")
    attributes = ctypes.c_void_p()
    devices = ctypes.POINTER(ctypes.c_void_p)()
    count = ctypes.c_uint32()
    cameras: list[tuple[str, str]] = []
    try:
        check(mfplat.MFCreateAttributes(ctypes.byref(attributes), 1), "MFCreateAttributes")
        key, value = guid(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE), guid(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID)
        check(com_call(attributes, SET_GUID, key, value), "SetGUID")
        check(mf.MFEnumDeviceSources(attributes, ctypes.byref(devices), ctypes.byref(count)), "MFEnumDeviceSources")
        for i in range(count.value):
            device = ctypes.c_void_p(devices[i])
            try:
                name = allocated_string(ole32, device, MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME)
                link = allocated_string(ole32, device, MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK)
                cameras.append((name, link))
            finally:
                com_call(device, RELEASE)
    finally:
        if devices:
            ole32.CoTaskMemFree(ctypes.cast(devices, ctypes.c_void_p))
        if attributes:
            com_call(attributes, RELEASE)
        mfplat.MFShutdown()
        if initialized >= 0:
            ole32.CoUninitialize()
    return cameras


def allocated_string(ole32: ctypes.WinDLL, activate: ctypes.c_void_p, key: str) -> str:
    """Return a string attribute of a Media Foundation object, "" when it has none."""
    text = ctypes.c_void_p()
    length = ctypes.c_uint32()
    attribute = guid(key)
    if com_call(activate, GET_ALLOCATED_STRING, attribute, text, length) < 0:
        return ""
    try:
        return ctypes.wstring_at(text.value, length.value)
    finally:
        ole32.CoTaskMemFree(text)


def describe(name: str, link: str) -> str:
    """Return what a camera is: its name, USB vendor and product id, revision and serial number."""
    usb = usb_device_of(link)
    if usb is None:
        return f"{name}, no USB device"
    vendor, product, revision, serial = usb
    text = f"{name}, USB {vendor}:{product}" + (f" rev {revision}" if revision else "")
    return text + (f", serial {serial}" if serial else ", no serial number")


def usb_device_of(link: str) -> tuple[str, str, str, str] | None:
    """Return vendor id, product id, revision and serial number of the USB device behind a camera's symbolic link.

    The serial number is "" when the device reports none; None is returned for a camera that is no USB device.
    """
    # \\?\usb#vid_04f2&pid_b6ea&mi_00#6&1793c9d&0&0000#{e5323777-...}\global -> USB\VID_04F2&PID_B6EA&MI_00\6&...
    instance = link.removeprefix("\\\\?\\").split("#{")[0].replace("#", "\\").upper()
    if not instance.startswith("USB\\"):
        return None
    cfgmgr32 = ctypes.WinDLL("cfgmgr32")
    node = ctypes.c_uint32()
    if cfgmgr32.CM_Locate_DevNodeW(ctypes.byref(node), ctypes.c_wchar_p(instance), 0) != 0:
        return None
    # A camera of a composite device (&MI_xx) is one of its interfaces: the USB device is its parent.
    if "&MI_" in instance:
        parent = ctypes.c_uint32()
        if cfgmgr32.CM_Get_Parent(ctypes.byref(parent), node, 0) != 0:
            return None
        node = parent
    buffer = ctypes.create_unicode_buffer(512)
    if cfgmgr32.CM_Get_Device_IDW(node, buffer, len(buffer), 0) != 0:
        return None
    parts = buffer.value.upper().split("\\")  # USB, VID_04F2&PID_B6EA, 0001
    ids = dict(part.split("_", 1) for part in parts[1].split("&") if "_" in part) if len(parts) > 1 else {}
    # Windows makes up an instance id with "&" in it for a device without a serial number.
    serial = parts[2] if len(parts) > 2 and "&" not in parts[2] else ""  # noqa: PLR2004 - USB, ids, instance
    return ids.get("VID", ""), ids.get("PID", ""), hardware_revision(cfgmgr32, node), serial


def hardware_revision(cfgmgr32: ctypes.WinDLL, node: ctypes.c_uint32) -> str:
    """Return the revision (bcdDevice) in the hardware ids of a USB device, e.g. "0012"; "" when it has none."""
    size = ctypes.c_uint32(2048)
    buffer = ctypes.create_string_buffer(size.value)
    if cfgmgr32.CM_Get_DevNode_Registry_PropertyW(node, CM_DRP_HARDWAREID, None, buffer, ctypes.byref(size), 0) != 0:
        return ""
    for hardware_id in buffer.raw[: size.value].decode("utf-16-le").upper().split("\0"):
        if "&REV_" in hardware_id:
            return hardware_id.split("&REV_")[1].split("&")[0]
    return ""
