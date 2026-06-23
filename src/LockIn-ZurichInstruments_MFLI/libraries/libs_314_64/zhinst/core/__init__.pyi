"""LabOne core API."""

from typing import (
    List,
    Union,
    overload,
    Any,
    Dict,
    Optional,
    Tuple,
    TypeAlias,
)

# typing.Literal requires Python 3.8+
from typing_extensions import Literal
from enum import Enum
import numpy as np

__version__: str

LabOneResultAny: TypeAlias = Any
LabOneResultNested: TypeAlias = Dict[str, Union[LabOneResultNested, LabOneResultAny]]

_STUB_VERSION_HASH = "ab4f5efbc6d6ce36626aaffa5b6968ce"

class ziListEnum(Enum):
    """Enumeration for listNodes."""

    absolute: int
    """Returns absolute paths."""
    all: int
    """Default flag, returning a simple listing of the given node."""
    basechannel: int
    """Returns only one instance of a node in case of multiple channels."""
    excludestreaming: int
    """Excludes streaming nodes."""
    excludevectors: int
    """Excludes vector nodes."""
    getonly: int
    """Returns only nodes which can be used with the get command."""
    leavesonly: int
    """Returns only nodes that are leaves, which means the they are at the outermost level of the tree."""
    recursive: int
    """Returns the nodes recursively."""
    settingsonly: int
    """Returns only nodes which are marked as setting."""
    streamingonly: int
    """Returns only streaming nodes."""
    subscribedonly: int
    """Returns only subscribed nodes."""

class ModuleBase:
    def clear(self) -> None:
        """End the module thread."""

    def execute(self) -> None:
        """Start the module execution.

        Subscribing or unsubscribing is not possible until the execution is
        finished."""

    def finish(self) -> None:
        """Stop the execution.

        The execution may be restarted by calling 'execute' again."""

    def finished(self) -> bool:
        """Check if the execution has finished.

        Returns:
            Flag if the execution is finished."""

    @overload
    def get(self, path: str, *, flat: Literal[False] = False) -> LabOneResultNested:
        """Return a dict with all nodes from the specified sub-tree.

        Args:
            path: Path string of the node. Use wild card to select all.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with all nodes from the specified sub-tree."""

    @overload
    def get(self, path: str, *, flat: Literal[True]) -> Dict[str, LabOneResultAny]:
        """Return a dict with all nodes from the specified sub-tree.

        Args:
            path: Path string of the node. Use wild card to select all.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with all nodes from the specified sub-tree."""

    def get(self, path: str, *, flat: bool = False) -> LabOneResultNested:
        """Return a dict with all nodes from the specified sub-tree.

        Args:
            path: Path string of the node. Use wild card to select all.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with all nodes from the specified sub-tree."""

    def getDouble(self, path: str) -> float:
        """Get a double value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Floating point double value."""

    def getInt(self, path: str) -> int:
        """Get a integer value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Integer value."""

    def getString(self, path: str) -> str:  # Wrong return type in docs (object)
        """Get a string value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            String value."""

    def getStringUnicode(self, path: str) -> str:  # Wrong return type in docs (object)
        """Get a unicode encoded string value from the specified node.

        Deprecated, please use `getString` instead.
        Args:
            path: Path string of the node.

        Returns:
            Unicode encoded string value."""

    def help(self, path: str = "*") -> None:
        """Prints a well-formatted description of a module parameter.

        Args:
            path: Path for which the nodes should be listed. The path may
                  contain wildcards so that the returned nodes do not
                  necessarily have to have the same parents."""

    def listNodes(
        self,
        path: str,
        *,
        flags: Union[ziListEnum, int] = 0,
        recursive: bool = False,
        absolute: bool = False,
        leavesonly: bool = False,
        settingsonly: bool = False,
        streamingonly: bool = False,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        getonly: bool = False,
        excludevectors: bool = False,
        excludestreaming: bool = False,
    ) -> List[str]:
        """This function returns a list of node names found at the specified path.

        Args:
            path:  Path for which the nodes should be listed. The path may
                   contain wildcards so that the returned nodes do not
                   necessarily have to have the same parents.
            flags: Flags specifying how the selected nodes are listed
                   (see `zhinst.core.ziListEnum`). Flags can also specified by
                   the keyword arguments below.
            recursive: Returns the nodes recursively (default: False)
            absolute: Returns absolute paths (default: True)
            leavesonly: Returns only nodes that are leaves, which means they
                   are at the outermost level of the tree (default: False).
            settingsonly: Returns only nodes which are marked as setting
                   (default: False).
            streamingonly: Returns only streaming nodes (default: False).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                   multiple channels (default: False).
            getonly: Return only nodes that can be used in a get request
            excludestreaming: Exclude streaming nodes (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            List of node names."""

    def listNodesJSON(
        self,
        path: str,
        *,
        flags: Union[ziListEnum, int] = 0,
        recursive: bool = False,
        absolute: bool = False,
        leavesonly: bool = False,
        settingsonly: bool = False,
        streamingonly: bool = False,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        getonly: bool = False,
        excludevectors: bool = False,
        excludestreaming: bool = False,
    ) -> str:  # `object` in documentation
        """Returns a json dict of all nodes found at the specified path.

        Args:
            path:  Path for which the nodes should be listed. The path may
                   contain wildcards so that the returned nodes do not
                   necessarily have to have the same parents.
            flags: Flags specifying how the selected nodes are listed
                   (see `zhinst.core.ziListEnum`). Flags can also specified by
                   the keyword arguments below. They are the same as for
                   listNodes(), except that recursive, absolute, and leavesonly
                   are enforced.
            settingsonly: Returns only nodes which are marked as setting
                   (default: False).
            streamingonly: Returns only streaming nodes (default: False).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                   multiple channels (default: False).
            excludestreaming: Exclude streaming nodes (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            JSON dictionary nodepath:information"""

    def progress(self) -> np.ndarray:
        """Reports the progress of the execution.

        Returns:
            Progress with a number between 0 and 1."""

    @overload
    def read(self, flat: Literal[False]) -> LabOneResultNested:
        """Read the module output data.

        If the module execution is still ongoing only a subset of data is
        returned. If huge data sets are produced call this method to keep
        memory usage reasonable.

        Args:
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            The module output data."""

    @overload
    def read(self, flat: Literal[True]) -> Dict[str, LabOneResultAny]:
        """Read the module output data.

        If the module execution is still ongoing only a subset of data is
        returned. If huge data sets are produced call this method to keep
        memory usage reasonable.

        Args:
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            The module output data."""

    def read(self, flat: bool = False) -> Dict[str, LabOneResultAny]:
        """Read the module output data.

        If the module execution is still ongoing only a subset of data is
        returned. If huge data sets are produced call this method to keep
        memory usage reasonable.

        Args:
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            The module output data."""

    def save(self, filename: str) -> None:
        """Save measured data to file.

        Args:
            filename: File name string (without extension)."""

    @overload
    def set(self, path: str, value: Any) -> None:
        """Set a single node value.

        `path` is the node path and `value` the value to set.

        Args:
            path: Node path string.
            value: The value to set in case of a single node set.
        """

    @overload
    def set(self, items: Union[List[Tuple[str, Any]], Tuple[Tuple[str, Any]]]) -> None:
        """Set multiple nodes. `items` is a list of path/value pairs.

        A transaction is used to optimize the data transfer.

        Args:
            items: A list of path/value pairs.
        """

    def subscribe(self, path: Union[str, List[str]]) -> None:
        """Subscribe to one or several nodes.

        After subscription the module execution can be started with the
        'execute' command. During the module execution paths can not be
        subscribed or unsubscribed.

        Args:
            path: Path string of the node. Use wild card to
                  select all. Alternatively also a list of path
                  strings can be specified."""

    def trigger(self) -> None:
        """Execute a manual trigger, if applicable."""

    def unsubscribe(self, path: Union[str, List[str]]) -> None:
        """Unsubscribe from one or several nodes.

        During the module execution paths can not be subscribed
        or unsubscribed.

        Args:
            path: Path string of the node. Use wild card to
                  select all. Alternatively also a list of path
                  strings can be specified."""

class AwgModule(ModuleBase): ...
class DataAcquisitionModule(ModuleBase): ...
class DataStreamingModule(ModuleBase): ...
class DeviceSettingsModule(ModuleBase): ...
class ImpedanceModule(ModuleBase): ...
class MultiDeviceSyncModule(ModuleBase): ...
class PidAdvisorModule(ModuleBase): ...
class PrecompensationAdvisorModule(ModuleBase): ...
class QuantumAnalyzerModule(ModuleBase): ...
class RecorderModule(ModuleBase): ...
class ScopeModule(ModuleBase): ...
class SweeperModule(ModuleBase): ...
class ZoomFFTModule(ModuleBase): ...

class ziDAQServer:
    """Class to connect with a Zurich Instruments data server.

    Args:
        host: Host string e.g. '127.0.0.1' for localhost
        port: Port number e.g. 8004 for the ziDataServer.
        api_level: API level number.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)
    """

    def __init__(
        self,
        host: str,
        port: int,
        api_level: Literal[0, 1, 4, 5, 6],
        allow_version_mismatch: bool = False,
    ) -> None: ...
    def asyncSetDouble(self, path: str, value: float) -> None:
        """Asynchronously set the value as double for a specified node.

        Asynchronously means that the command is nonblocking and
        does not wait for the data server acknowledgement.

        Warning:
            This command never reports any error.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def asyncSetInt(self, path: str, value: int) -> None:
        """Asynchronously set the value as integer for a specified node.

        Asynchronously means that the command is nonblocking and
        does not wait for the data server acknowledgement.

        Warning:
            This command never reports any error.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def asyncSetString(self, path: str, value: str) -> None:
        """Asynchronously set the value as string for a specified node.

        Asynchronously means that the command is nonblocking and
        does not wait for the data server acknowledgement.

        Warning:
            This command never reports any error.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def awgModule(self) -> AwgModule:
        """Create a AwgModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def connect(self) -> None:
        """Initiate the connection to the data server.

        Important:
            During the object initialization the connection is already
            established. It is therefore not necessary to call this
            function unless one actively disconnects from the data
            server with the `disconnect` method."""

    def connectDevice(
        self,
        dev: str,
        interface: Literal["USB", "PCIe", "1GbE"],
        params: Optional[str] = None,
    ) -> None:
        """Connect with the data server to a specified device.

        The device must be visible to the server. If the device is
        already connected the call will be ignored. The function will block
        until the device is connected and the device is ready to use.

        Args:
            dev: Device serial.
            interface: Device interface.
            params: Optional interface parameters string."""

    def dataAcquisitionModule(self) -> DataAcquisitionModule:
        """Create a DataAcquisitionModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def dataStreamingModule(self) -> DataStreamingModule:
        """Create a DataStreamingModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def deviceSettings(
        self,
    ) -> DeviceSettingsModule:  # Deprecated arguments not included
        """Create a Device Settings Module object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def disconnect(self) -> None:
        """Disconnects from the data server.

        Important:
            During the destruction the connection is closed properly.
            This function therefore does not need to be called in normal
            usage."""

    def disconnectDevice(self, dev: str) -> None:
        """Disconnect a device from the data server.

        This function will return immediately. The disconnection of
        the device may not yet be finished.
        Args:
            dev: Device serial string of device to disconnect."""

    def echoDevice(self, dev: str) -> None:  # Deprecated
        """Deprecated, see the 'sync' command.

        Sends an echo command to a device and blocks until
        answer is received. This is useful to flush all
        buffers between API and device to enforce that
        further code is only executed after the device executed
        a previous command.
        Args:
            dev: Device string e.g. 'dev100'."""

    def flush(self) -> None:  # Deprecated
        """Deprecated, see the 'sync' command.

        The flush command is identical to the sync command."""

    @overload
    def get(
        self,
        paths: str,
        *,
        flat: Literal[False] = False,
        flags: Union[ziListEnum, int] = 0,
        settingsonly: bool = True,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        excludevectors: bool = False,
    ) -> LabOneResultNested:
        """Return a dict with all nodes matching the path expression.

        Note: High-speed streaming nodes (e.g. `/devN/demods/0/sample`) are
              are never returned.

        Args:
            paths: Path expression string. Multiple paths can be specified
                   as a comma-separated list. Wildcards are supported to
                   select multiple matching nodes.
            flat:  Specify which type of data structure to return.
                   Return data either as a flat dict (True) or as a nested
                   dict tree (False, default).
            flags: Flags specifying how the selected nodes are listed
                   (see `zhinst.core.ziListEnum`). Flags can also specified by
                   the keyword arguments below.
            settingsonly: Returns only nodes which are marked as setting
                   (default: True).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                   multiple channels (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            A dict with all nodes from the specified sub-tree."""

    @overload
    def get(
        self,
        paths: str,
        *,
        flat: Literal[True],
        flags: Union[ziListEnum, int] = 0,
        settingsonly: bool = True,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        excludevectors: bool = False,
    ) -> Dict[str, LabOneResultAny]:
        """Return a dict with all nodes from the specified sub-tree.
        Note: Flags are ignored for a path that specifies one or more leaf nodes.
                Specifying flags, either as positional or keyword argument is
                mandatory if an empty set would be returned given the
                default flags (settingsonly).
                High-speed streaming nodes (e.g. `/devN/demods/0/sample`) are
                are never returned.

        Args:
            paths: Path string of the node. Multiple paths can be specified
                    as a comma-separated list. Wild cards are supported to
                    select multiple matching nodes.
            flat:  Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False, default).
            flags: Flags specifying how the selected nodes are listed
                    (see `zhinst.core.ziListEnum`). Flags can also specified by
                    the keyword arguments below.

            settingsonly: Returns only nodes which are marked as setting
                    (default: True).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                    multiple channels (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            A dict with all nodes from the specified sub-tree."""

    def get(
        self,
        paths: str,
        *,
        flat: bool = False,
        flags: Union[ziListEnum, int] = 0,
        settingsonly: bool = True,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        excludevectors: bool = False,
    ) -> LabOneResultNested:
        """Return a dict with all nodes from the specified sub-tree.
        Note: Flags are ignored for a path that specifies one or more leaf nodes.
                Specifying flags, either as positional or keyword argument is
                mandatory if an empty set would be returned given the
                default flags (settingsonly).
                High-speed streaming nodes (e.g. `/devN/demods/0/sample`) are
                are never returned.

        Args:
            paths: Path string of the node. Multiple paths can be specified
                    as a comma-separated list. Wild cards are supported to
                    select multiple matching nodes.
            flat:  Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False, default).
            flags: Flags specifying how the selected nodes are listed
                    (see `zhinst.core.ziListEnum`). Flags can also specified by
                    the keyword arguments below.

            settingsonly: Returns only nodes which are marked as setting
                    (default: True).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                    multiple channels (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            A dict with all nodes from the specified sub-tree."""

    def getAsEvent(self, path: str) -> None:
        """Trigger an event on the specified node.

        The node data is returned by a subsequent poll command.

        Args:
            path:  Path string of the node. Note: Wildcards and paths
                   referring to streaming nodes are not permitted."""

    def asyncGetAsEvent(self, path: str) -> None:
        """Trigger an event on the specified node.

        The node data is returned by a subsequent poll command.

        The difference to the non async equivalent is that this
        function returns immediately, even before the data server
        has received the request. This gives the lowest latency at
        the cost of not providing feedback if the request fails

        .. versionadded:: 23.02

        Args:
            path:  Path string of the node. Note: Wildcards and paths
                   referring to streaming nodes are not permitted."""

    def getAuxInSample(self, path: str) -> Dict[str, np.ndarray]:
        """Returns a single auxin sample.

        The auxin data is averaged in contrast to the auxin data
        embedded in the demodulator sample.

        Args:
            path: Path string of the node"""

    def getByte(self, path: str) -> str:
        """Get a byte array (string) value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Byte array (string) value."""

    def getComplex(self, path: str) -> complex:
        """Get a complex double value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Complex double value."""

    def getConnectionAPILevel(self) -> Literal[0, 1, 4, 5, 6]:  # Deprecated
        """Returns ziAPI level used for the active connection.

        DEPRECATED, use api_level.

        Returns:
            ziAPI level used for the active connection."""

    def getDIO(self, path: str) -> Dict[str, np.ndarray]:
        """Returns a single DIO sample.

        Args:
            path: Path string of the node

        Returns:
            Single DIO sample."""

    def getDebugLogpath(self) -> str:
        """Path where logfiles are stored.

        Note, it will return an empty string if the path has not
        been set or logging has not been enabled via `setDebugLevel()`.

        Returns:
            Path to directory where logfiles are stored."""

    def getDouble(self, path: str) -> float:
        """Get a double value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Floating point double value."""

    def getInt(self, path: str) -> int:
        """Get a integer value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            Integer value."""

    def getList(self, path: str, flags: int = 8) -> List[str]:  # Deprecated
        """DEPRECATED: superseded by get(...).

        Return a list with all nodes from the specified sub-tree.
        Args:
            path:  Path string of the node. Use wild card to
                   select all.
            flags: Specify which type of nodes to include in the
                   result. Allowed:
                   ZI_LIST_NODES_SETTINGSONLY = 0x08 (default)
                   ZI_LIST_NODES_ALL = 0x00 (all nodes)"""

    def getSample(self, path: str) -> Dict[str, np.ndarray]:
        """Returns a single demodulator sample (including DIO and AuxIn).

        For more efficient data recording use subscribe and poll methods!

        Args:
            path: Path string of the node

        Returns:
            Single demodulator sample (including DIO and AuxIn)."""

    def getString(self, path: str) -> str:  # `object` in documentation
        """Get a string value from the specified node.

        Args:
            path: Path string of the node.

        Returns:
            String value."""

    def getStringUnicode(self, path: str) -> str:  # `object` in documentation
        """Get a unicode encoded string value from the specified node.

        Deprecated, please use `getString` instead.
        Args:
            path: Path string of the node.

        Returns:
            Unicode encoded string value."""

    def help(self, path: str) -> None:
        """Prints a well-formatted description of a node.

        HF2 devices do not support this functionality.

        Args:
            path: Path for which the nodes should be listed. The path may
                  contain wildcards so that the returned nodes do not
                  necessarily have to have the same parents."""

    def impedanceModule(self) -> ImpedanceModule:
        """Create a ImpedanceModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def listNodes(
        self,
        path: str,
        *,
        flags: Optional[Union[ziListEnum, int]] = None,
        recursive: bool = False,
        absolute: bool = False,
        leavesonly: bool = False,
        settingsonly: bool = False,
        streamingonly: bool = False,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        getonly: bool = False,
        excludevectors: bool = False,
        excludestreaming: bool = False,
    ) -> List[str]:
        """This function returns a list of node names found at the specified path.

        Args:
            path:  Path for which the nodes should be listed. The path may
                   contain wildcards so that the returned nodes do not
                   necessarily have to have the same parents.
            flags: Flags specifying how the selected nodes are listed
                   (see `zhinst.core.ziListEnum`). Flags can also specified by
                   the keyword arguments below.

            recursive: Returns the nodes recursively (default: False)
            absolute: Returns absolute paths (default: True)
            leavesonly: Returns only nodes that are leaves, which means they
                   are at the outermost level of the tree (default: False).
            settingsonly: Returns only nodes which are marked as setting
                   (default: False).
            streamingonly: Returns only streaming nodes (default: False).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                   multiple channels (default: False).
            getonly: Return only nodes that can be used in a get request
            excludestreaming: Exclude streaming nodes (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            List of node names."""

    def listNodesJSON(
        self,
        path: str,
        *,
        flags: Optional[Union[ziListEnum, int]] = None,
        recursive: bool = False,
        absolute: bool = False,
        leavesonly: bool = False,
        settingsonly: bool = False,
        streamingonly: bool = False,
        subscribedonly: bool = False,
        basechannelonly: bool = False,
        getonly: bool = False,
        excludevectors: bool = False,
        excludestreaming: bool = False,
    ) -> List[str]:  # `object` in documentation
        """Returns a list of nodes with description found at the specified path.

        HF2 devices do not support this functionality.

        Args:
            path:  Path for which the nodes should be listed. The path may
                   contain wildcards so that the returned nodes do not
                   necessarily have to have the same parents.
            flags: Flags specifying how the selected nodes are listed
                   (see `zhinst.core.ziListEnum`). Flags can also specified by
                   the keyword arguments below. They are the same as for
                   listNodes(), except that recursive, absolute, and leavesonly
                   are enforced.
            settingsonly: Returns only nodes which are marked as setting
                   (default: False).
            streamingonly: Returns only streaming nodes (default: False).
            subscribedonly: Returns only subscribed nodes (default: False).
            basechannelonly: Return only one instance of a node in case of
                   multiple channels (default: False).
            getonly: Return only nodes that can be used in a get request
            excludestreaming: Exclude streaming nodes (default: False).
            excludevectors: Exclude vector nodes (default: False).

        Returns:
            JSON dictionary nodepath:information"""

    def logOff(self) -> None:
        """Disables logging of commands sent to a server."""

    def logOn(self, flags: int, filename: str, style: Literal[0, 1, 2] = 2) -> None:
        """Enables logging of commands sent to a server.

        Args:
            flags: Flags (LOG_NONE:             0x00000000
                          LOG_SET_DOUBLE:       0x00000001
                          LOG_SET_INT:          0x00000002
                          LOG_SET_BYTE:         0x00000004
                          LOG_SET_STRING:       0x00000008
                          LOG_SYNC_SET_DOUBLE:  0x00000010
                          LOG_SYNC_SET_INT:     0x00000020
                          LOG_SYNC_SET_BYTE:    0x00000040
                          LOG_SYNC_SET_STRING:  0x00000080
                          LOG_GET_DOUBLE:       0x00000100
                          LOG_GET_INT:          0x00000200
                          LOG_GET_BYTE:         0x00000400
                          LOG_GET_STRING:       0x00000800
                          LOG_GET_DEMOD:        0x00001000
                          LOG_GET_DIO:          0x00002000
                          LOG_GET_AUXIN:        0x00004000
                          LOG_GET_COMPLEX:      0x00008000
                          LOG_LISTNODES:        0x00010000
                          LOG_SUBSCRIBE:        0x00020000
                          LOG_UNSUBSCRIBE:      0x00040000
                          LOG_GET_AS_EVENT:     0x00080000
                          LOG_UPDATE:           0x00100000
                          LOG_POLL_EVENT:       0x00200000
                          LOG_POLL:             0x00400000
                          LOG_ALL :             0xffffffff)
            filename: Log file name.
            style: Log style (LOG_STYLE_TELNET: 0, LOG_STYLE_MATLAB: 1,
                   LOG_STYLE_PYTHON: 2 (default))."""

    def multiDeviceSyncModule(self) -> MultiDeviceSyncModule:
        """Create a MultiDeviceSyncModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def pidAdvisor(self) -> PidAdvisorModule:  # Deprecated arguments not included
        """Create a PID Advisor Module object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    @overload
    def poll(
        self,
        recording_time_s: float,
        timeout_ms: int,
        *,
        flat: Literal[False] = False,
        flags: int = 0,
    ) -> LabOneResultNested:
        """Poll all Events available before and within an given time period.

        Continuously check for value changes (by calling pollEvent) in all
        subscribed nodes for the specified duration and return the data. If
        no value change occurs in subscribed nodes before duration + timeout,
        poll returns no data. This function call is blocking (it is
        synchronous). However, since all value changes are returned since
        either subscribing to the node or the last poll (assuming no buffer
        overflow has occurred on the Data Server), this function may be used
        in a quasi-asynchronous manner to return data spanning a much longer
        time than the specified duration. The timeout parameter is only
        relevant when communicating in a slow network. In this case it may be
        set to a value larger than the expected round-trip time in the
        network.

        Args:
            recording_time_s: Recording time in [s]. The function will block
                  during that time.
            timeout_ms: Poll timeout in [ms]. Recommended value is 500ms.
            flags: Poll flags.
                  DEFAULT = 0x0000: Default.
                  FILL    = 0x0001: Fill holes.
                  THROW   = 0x0004: Throw EOFError exception if sample
                                    loss is detected (only possible in
                                    combination with DETECT).
                  DETECT  = 0x0008: Detect data loss holes.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with the polled events. (Empty if no event
                occurred within the given timeout)"""

    @overload
    def poll(
        self,
        recording_time_s: float,
        timeout_ms: int,
        *,
        flat: Literal[True],
        flags: int = 0,
    ) -> Dict[str, LabOneResultAny]:
        """Poll all Events available before and within an given time period.

        Continuously check for value changes (by calling pollEvent) in all
        subscribed nodes for the specified duration and return the data. If
        no value change occurs in subscribed nodes before duration + timeout,
        poll returns no data. This function call is blocking (it is
        synchronous). However, since all value changes are returned since
        either subscribing to the node or the last poll (assuming no buffer
        overflow has occurred on the Data Server), this function may be used
        in a quasi-asynchronous manner to return data spanning a much longer
        time than the specified duration. The timeout parameter is only
        relevant when communicating in a slow network. In this case it may be
        set to a value larger than the expected round-trip time in the
        network.

        Args:
            recording_time_s: Recording time in [s]. The function will block
                  during that time.
            timeout_ms: Poll timeout in [ms]. Recommended value is 500ms.
            flags: Poll flags.
                  DEFAULT = 0x0000: Default.
                  FILL    = 0x0001: Fill holes.
                  THROW   = 0x0004: Throw EOFError exception if sample
                                    loss is detected (only possible in
                                    combination with DETECT).
                  DETECT  = 0x0008: Detect data loss holes.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with the polled events. (Empty if no event
                occurred within the given timeout)"""

    def poll(
        self,
        recording_time_s: float,
        timeout_ms: int,
        flags: int = 0,
        flat: bool = False,
    ) -> Dict[str, LabOneResultAny]:
        """Poll all Events available before and within an given time period.

        Continuously check for value changes (by calling pollEvent) in all
        subscribed nodes for the specified duration and return the data. If
        no value change occurs in subscribed nodes before duration + timeout,
        poll returns no data. This function call is blocking (it is
        synchronous). However, since all value changes are returned since
        either subscribing to the node or the last poll (assuming no buffer
        overflow has occurred on the Data Server), this function may be used
        in a quasi-asynchronous manner to return data spanning a much longer
        time than the specified duration. The timeout parameter is only
        relevant when communicating in a slow network. In this case it may be
        set to a value larger than the expected round-trip time in the
        network.

        Args:
            recording_time_s: Recording time in [s]. The function will block
                  during that time.
            timeout_ms: Poll timeout in [ms]. Recommended value is 500ms.
            flags: Poll flags.
                  DEFAULT = 0x0000: Default.
                  FILL    = 0x0001: Fill holes.
                  THROW   = 0x0004: Throw EOFError exception if sample
                                    loss is detected (only possible in
                                    combination with DETECT).
                  DETECT  = 0x0008: Detect data loss holes.
            flat: Specify which type of data structure to return.
                  Return data either as a flat dict (True) or as a nested
                  dict tree (False). Default = False.

        Returns:
            A dict with the polled events. (Empty if no event occurred within
                the given timeout)"""

    def pollEvent(self, timeout_ms: int) -> Dict[str, LabOneResultAny]:
        """Poll a single Event.

        An event are one or multiple changes that occurred in
        one single subscribed node. This is a low-level function
        to obtain a single event from the data server connection.
        To get all data waiting in the buffers, this command should
        be executed continuously until an empty dict is returned.

        The `poll()` function is better suited in many cases, as it
        returns the data accumulated over some time period.
        Args:
            timeout_ms: Poll timeout in [ms]. Recommended value is 500ms.

        Returns:
            A dict with the polled event. (Empty if no event
                occurred within the given timeout)"""

    def precompensationAdvisor(self) -> PrecompensationAdvisorModule:
        """Create a PrecompensationAdvisorModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def programRT(self, dev: str, filename: str) -> None:
        """Program RT.
        Only relevant for a HF2 device.

        Args:
            dev: Device identifier e.g. 'dev99'.
            filename: File name of the RT program."""

    def quantumAnalyzerModule(self) -> QuantumAnalyzerModule:
        """Create a QuantumAnalyzerModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def record(self) -> RecorderModule: ...  # Deprecated arguments not included

    """Create a Record Module object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def revision(self) -> int:
        """Get the revision number of the Python interface of Zurich Instruments.

        Returns:
            Revision number."""

    def scopeModule(self) -> ScopeModule:
        """Create a ScopeModule object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    @overload
    def set(self, path: str, value: Any) -> None:
        """Overloaded function.

        Set a single node value. `path` is the node path
        and `value` the value to set.

        Args:
            path: Node path string.
            value: The value to set in case of a single node set
                (items is the node path).
        """

    @overload
    def set(self, items: Union[List[Tuple[str, Any]], Tuple[Tuple[str, Any]]]) -> None:
        """Set multiple nodes. `items` is a list of path/value pairs.

        A transaction is used to optimize the data transfer.

        Args:
            items: A list of path/value pairs
        """

    def set(
        self,
        items_or_path: Union[Union[List[Tuple[str, Any]], Tuple[Tuple[str, Any]]], str],
        value: Optional[Any] = None,
    ) -> None:
        """Overloaded function.

        1. `set(self, items: _MultipleNodeItems)`

            Set multiple nodes. `items` is a list of path/value pairs.

            A transaction is used to optimize the data transfer.

        2. `set(self, path: str, value: Any)`

            Set a single node value. `path` is the node path
            and `value` the value to set.

        Args:
            items_or_path: A list of path/value pairs or the node path string.
            value: The value to set in case of a single node set
                (items is the node path).
        """

    def setByte(self, path: str, value: Any) -> None:
        """Set the value as byte array (string) for a specified node.

        The command blocks until the data server has acknowledgement
        the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def setComplex(self, path: str, value: complex) -> None:
        """Set the value as complex double for a specified node.

        The command blocks until the data server has acknowledgement
        the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def setDebugLevel(self, severity: Literal[0, 1, 2, 3, 4, 5, 6]) -> None:
        """Enables debug log and sets the debug level.

        Resets the debug levels for individual sinks.

        Args:
            severity: Debug level (trace:0, debug:1, info:2, status:3,
                warning:4, error:5, fatal:6)."""

    def setDebugLevelConsole(self, severity: Literal[0, 1, 2, 3, 4, 5, 6]) -> None:
        """Enables debug log and sets the debug level for the console output.
        Args:
            severity: Debug level (trace:0, debug:1, info:2, status:3,
                warning:4, error:5, fatal:6)."""

    def setDebugLevelFile(self, severity: Literal[0, 1, 2, 3, 4, 5, 6]) -> None:
        """Enables debug log and sets the debug level for the file output.
        Args:
            severity: Debug level (trace:0, debug:1, info:2, status:3,
                warning:4, error:5, fatal:6)."""

    def setDebugLogpath(self, path: str) -> None:
        """Sets the path where logfiles are stored.

        Note, it will restart logging if it was already enabled
        via setDebugLevel().

        Args:
            path: Path to directory where logfiles are stored."""

    def setDeprecated(
        self, items: Union[List[Tuple[str, Any]], Tuple[Tuple[str, Any]]]
    ) -> None:
        """DEPRECATED: superseded by set(...).

        Set multiple nodes.

        Args:
            items: A list of path/value pairs."""

    def setDouble(self, path: str, value: float) -> None:
        """Set the value as double for a specified node.

        The command blocks until the data server has acknowledgement
        the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def setInt(self, path: str, value: int) -> None:
        """Set the value as integer for a specified node.

        The command blocks until the data server has acknowledgement
        the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def setString(self, path: str, value: str) -> None:
        """Set the value as string for a specified node.

        The command blocks until the data server has acknowledgement
        the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node."""

    def setVector(
        self,
        path: str,
        value: Union[
            np.ndarray,
            List[Union[int, float, complex]],
            Tuple[Union[int, float, complex], ...],
            str,
        ],
    ) -> None:
        """Set the value for a specified vector node.

        The command is different from the other set commands and is
        Optimized for vector transfer. It blocks until the device
        itself has acknowledged the complete vector data set.

        Args:
            path:  Path string of the node.
            value: Vector ((u)int8, (u)int16, (u)int32, (u)int64, float, double)
                   or string to write."""

    def subscribe(self, path: Union[str, List[str]]) -> None:
        """Subscribe to one or several nodes.

        Fetch data with the poll command.
        In order to avoid fetching old data that is still in the
        buffer, execute a sync command before subscribing to data streams.

        Args:
            path: Path string of the node. Use wild card to
                  select all. Alternatively also a list of path
                  strings can be specified."""

    def sweep(self) -> SweeperModule:  # Deprecated arguments not included
        """Create a Sweeper Module object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    def sync(self) -> None:
        """Synchronize all data paths.
        Ensures that get and poll commands return data which
        was recorded after the setting changes in front of
        the sync command. This sync command replaces the
        functionality of all syncSet, flush, and echoDevice commands.

        Warning:
            This blocks until all devices connected to the data
            server report a ready state! This can take up to a minute."""

    def syncSetDouble(self, path: str, value: float) -> float:
        """Synchronously set the value as double for a specified node.

        Synchronously means that the command is blocking until
        the device has acknowledged the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node.

        Returns:
            Acknowledged value by the device."""

    def syncSetInt(self, path: str, value: int) -> int:
        """Synchronously set the value as integer for a specified node.

        Synchronously means that the command is blocking until
        the device has acknowledged the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node.

        Returns:
            Acknowledged value by the device."""

    def syncSetString(self, path: str, value: str) -> str:
        """Synchronously set the value as string for a specified node.

        Synchronously means that the command is blocking until
        the device has acknowledged the set request.

        Args:
            path:  Path string of the node.
            value: Value of the node.

        Returns:
            Acknowledged value by the device."""

    def unsubscribe(self, path: Union[str, List[str]]) -> None:
        """Unsubscribe data streams.

        Use this command after recording to avoid buffer overflows
        that may increase the latency of other command.

        Args:
            path: Path string of the node. Use wild card to
                  select all. Alternatively also a list of path
                  strings can be specified."""

    def update(self) -> None:
        """Check if additional devices are attached.

        Only revelant for connections to an HF2 Data Server.
        This function is not needed for servers running under windows
        as devices will be detected automatically."""

    def version(self) -> str:
        """Get version string of the Python interface of Zurich Instruments."""

    def writeDebugLog(
        self, severity: Literal[0, 1, 2, 3, 4, 5, 6], message: str
    ) -> None:
        """Outputs message to the debug log (if enabled).

        Args:
            severity: Debug level (trace:0, debug:1, info:2, status:3,
                warning:4, error:5, fatal:6).    message:  Message to output to the log.
        """

    def zoomFFT(self) -> ZoomFFTModule:  # Deprecated arguments not included
        """Create a zoomFFT Module object.

        This will start a thread for running an asynchronous module.

        Returns:
            Created module instance."""

    @property
    def host(self) -> str:
        """The host used for the active connection.

        .. versionadded:: 22.08"""

    @property
    def port(self) -> int:
        """The port used for the active connection.

        .. versionadded:: 22.08"""

    @property
    def api_level(self) -> Literal[0, 1, 4, 5, 6]:
        """The ziAPI level used for the active connection.

        .. versionadded:: 22.08"""

class ziDiscovery:
    """Class to find devices and get their connectivity properties."""

    """Class to find devices and get their connectivity properties."""

    def __init__(self) -> None: ...
    def find(self, dev: str) -> str:
        """Return the device id for a given device address.

        Args:
            dev: Device address string e.g. UHF-DEV2000.

        Returns:
            Device id."""

    def findAll(self) -> List[str]:
        """Return a list of all discoverable devices.

        Returns:
            List of all discoverable devices."""

    def get(self, dev: str) -> Dict[str, LabOneResultAny]:
        """Return the device properties for a given device id.

        Args:
            dev: Device id string e.g. DEV2000.

        Returns:
            Device properties."""

    def setDebugLevel(self, severity: Literal[0, 1, 2, 3, 4, 5, 6]) -> None:
        """Set debug level.

        Args:
            severity: debug level."""

def compile_seqc(
    code: str,
    devtype: str,
    options: Union[str, List[str]],
    index: int,
    samplerate: Optional[float] = None,
    sequencer: Optional[str] = None,
    wavepath: Optional[str] = None,
    waveforms: Optional[str] = None,
    filename: Optional[str] = None,
    pipeliner: Optional[bool] = False,
) -> Tuple[bytes, Dict[str, Any]]:
    """Compile the sequencer code.

    This function is a purely static function that does not require an
    active connection to a Data Server.

    .. versionadded:: 22.08

    Args:
        code: SeqC input
        devtype: target device type, e.g., HDAWG8, SHFQC
        options: list of device options, or string of
            options separated by newlines as returned by node
            /dev.../features/options.
        index: index of the AWG core
        samplerate: target sample rate of the sequencer
            Mandatory and only respected for HDAWG. Should match the
            value set on the device:
            `/dev.../system/clocks/sampleclock/freq`.
        sequencer: one of 'qa', 'sg', or 'auto'.
            Mandatory for SHFQC.
        wavepath: path to directory with waveforms. Defaults to
            path used by LabOne UI or AWG Module.
        waveforms: list of CSV waveform files separated by ';'.
            Defaults to an empty list. Set to `None` to include
            all CSV files in `wavepath`.
        filename: name of embedded ELF filename.
        pipeliner: set to `True` if the compiled program will be
            loaded into the AWG pipeliner. Pipeliner mode imposes a
            smaller waveform memory limit; compilation fails when
            the total waveform memory exceeds it. Defaults to False.

    Returns:
        Tuple (elf, extra) of binary ELF data for sequencer and extra
            dictionary with compiler output.

    Note:
        The same function is available in the `zhinst-seqc-compiler`
        package. `zhinst.core.compile_seqc` will forward the call to
        `zhinst.seqc_compiler.compile_seqc` if a compatible version of
        this package is installed. A version is compatible if major and
        minor package versions match, and the revision of
        `zhinst-seqc-compiler` is greater or equal to the revision of
        `zhinst-core`. A warning will be issued if the versions do not
        match."""
