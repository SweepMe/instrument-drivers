# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List, Optional
from ..call import call, call_async
from ..dto import requests as dto

if TYPE_CHECKING:
    from .device import Device


class DeviceStorage:
    """
    Class providing access to device storage.
    Requires at least Firmware 7.30.
    """

    def __init__(self, device: 'Device'):
        self._device: 'Device' = device

    def set_string(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the device value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
            encode=encode,
        )
        call("device/set_storage", request)

    async def set_string_async(
            self,
            key: str,
            value: str,
            encode: bool = False
    ) -> None:
        """
        Sets the device value stored at the provided key.

        Args:
            key: Key to set the value at.
            value: Value to set.
            encode: Whether the stored value should be base64 encoded before being stored.
                This makes the string unreadable to humans using the ASCII protocol,
                however, values stored this way can be of any length and use non-ASCII and protocol reserved characters.
        """
        request = dto.DeviceSetStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
            encode=encode,
        )
        await call_async("device/set_storage", request)

    def get_string(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the device value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = dto.DeviceGetStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            decode=decode,
        )
        response = call(
            "device/get_storage",
            request,
            dto.StringResponse.from_binary)
        return response.value

    async def get_string_async(
            self,
            key: str,
            decode: bool = False
    ) -> str:
        """
        Gets the device value stored with the provided key.

        Args:
            key: Key to read the value of.
            decode: Whether the stored value should be decoded.
                Only use this when reading values set by storage.set with "encode" true.

        Returns:
            Stored value.
        """
        request = dto.DeviceGetStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            decode=decode,
        )
        response = await call_async(
            "device/get_storage",
            request,
            dto.StringResponse.from_binary)
        return response.value

    def set_number(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = dto.DeviceSetStorageNumberRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
        )
        call("device/set_storage_number", request)

    async def set_number_async(
            self,
            key: str,
            value: float
    ) -> None:
        """
        Sets the value at the provided key to the provided number.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = dto.DeviceSetStorageNumberRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
        )
        await call_async("device/set_storage_number", request)

    def get_number(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = call(
            "device/get_storage_number",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    async def get_number_async(
            self,
            key: str
    ) -> float:
        """
        Gets the value at the provided key interpreted as a number.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = await call_async(
            "device/get_storage_number",
            request,
            dto.DoubleResponse.from_binary)
        return response.value

    def set_bool(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = dto.DeviceSetStorageBoolRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
        )
        call("device/set_storage_bool", request)

    async def set_bool_async(
            self,
            key: str,
            value: bool
    ) -> None:
        """
        Sets the value at the provided key to the provided boolean.

        Args:
            key: Key to set the value at.
            value: Value to set.
        """
        request = dto.DeviceSetStorageBoolRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
            value=value,
        )
        await call_async("device/set_storage_bool", request)

    def get_bool(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = call(
            "device/get_storage_bool",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def get_bool_async(
            self,
            key: str
    ) -> bool:
        """
        Gets the value at the provided key interpreted as a boolean.

        Args:
            key: Key to get the value at.

        Returns:
            Stored value.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = await call_async(
            "device/get_storage_bool",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def erase_key(
            self,
            key: str
    ) -> bool:
        """
        Erases the device value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = call(
            "device/erase_storage",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def erase_key_async(
            self,
            key: str
    ) -> bool:
        """
        Erases the device value stored at the provided key.

        Args:
            key: Key to erase.

        Returns:
            A boolean indicating if the key existed.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = await call_async(
            "device/erase_storage",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    def list_keys(
            self,
            prefix: Optional[str] = None
    ) -> List[str]:
        """
        Lists the device storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = dto.DeviceStorageListKeysRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            prefix=prefix,
        )
        response = call(
            "device/storage_list_keys",
            request,
            dto.StringArrayResponse.from_binary)
        return response.values

    async def list_keys_async(
            self,
            prefix: Optional[str] = None
    ) -> List[str]:
        """
        Lists the device storage keys matching a given prefix.
        Omit the prefix to list all the keys.

        Args:
            prefix: Optional key prefix.

        Returns:
            Storage keys matching the given prefix.
        """
        request = dto.DeviceStorageListKeysRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            prefix=prefix,
        )
        response = await call_async(
            "device/storage_list_keys",
            request,
            dto.StringArrayResponse.from_binary)
        return response.values

    def key_exists(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in device storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = call(
            "device/storage_key_exists",
            request,
            dto.BoolResponse.from_binary)
        return response.value

    async def key_exists_async(
            self,
            key: str
    ) -> bool:
        """
        Determines whether a given key exists in device storage.

        Args:
            key: Key which existence to determine.

        Returns:
            True indicating that the key exists, false otherwise.
        """
        request = dto.DeviceStorageRequest(
            interface_id=self._device.connection.interface_id,
            device=self._device.device_address,
            key=key,
        )
        response = await call_async(
            "device/storage_key_exists",
            request,
            dto.BoolResponse.from_binary)
        return response.value
