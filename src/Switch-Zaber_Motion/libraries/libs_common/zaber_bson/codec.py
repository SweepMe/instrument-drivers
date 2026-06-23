#!/usr/bin/python -OOOO
# vim: set fileencoding=utf8 shiftwidth=4 tabstop=4 textwidth=80 foldmethod=marker :
# Copyright (c) 2010, Kou Man Tong. All rights reserved.
# Copyright (c) 2015, Ayun Park. All rights reserved.
# For licensing, see LICENSE file included in the package.
"""
Base codec functions for bson.
"""
import struct
import warnings
from datetime import datetime, timezone
from abc import ABCMeta, abstractmethod
from uuid import UUID
from decimal import Decimal
from io import BytesIO as StringIO
import calendar
from binascii import b2a_hex
from typing import Optional, Union, Callable, List, Iterator, Any, Tuple, Dict

from zaber_bson.types import UInt64, Int64, Int32

Key = Union[str, bytes]
AnyDict = Dict[Key, Any]
AnyList = List[Any]
AnyTuple = Tuple[Any, ...]


class MissingClassDefinition(ValueError):
    def __init__(self, class_name: str):
        super().__init__(f"No class definition for class {class_name}")


class UnknownSerializerError(ValueError):
    def __init__(self, key: Key, value: Any):
        super().__init__(f"Unable to serialize: key '{key!r}' value: {value} type: {type(value)}")


class MissingTimezoneWarning(RuntimeWarning):
    def __init__(self, *args: object):
        if len(args) < 1:
            args = ("Input datetime object has no tzinfo, assuming UTC.",)
        super().__init__(*args)


class TraversalStep:
    def __init__(self, parent: object, key: Union[str, bytes, int]):
        self.parent = parent
        self.key = key


TraversalStack = List[TraversalStep]
GeneratorFunc = Optional[Callable[[Any, TraversalStack], Iterator[str]]]
OnUnknown = Optional[Callable[[Any], Any]]


class BSONCoding:
    __metaclass__ = ABCMeta

    @abstractmethod
    def bson_encode(self) -> AnyDict:
        pass

    @abstractmethod
    def bson_init(self, raw_values: AnyDict) -> Any:
        pass


CLASSNAME_KEY = "$$__CLASS_NAME__$$"
classes = {}


def import_class(cls: Any) -> None:
    if not issubclass(cls, BSONCoding):
        return

    global classes
    classes[cls.__name__] = cls


def import_classes(*args: Any) -> None:
    for cls in args:
        import_class(cls)


def import_classes_from_modules(*args: Any) -> None:
    for module in args:
        for item in module.__dict__:
            if hasattr(item, "__new__") and hasattr(item, "__name__"):
                import_class(item)


def encode_object(obj: BSONCoding, traversal_stack: TraversalStack,
                  generator_func: GeneratorFunc, on_unknown: OnUnknown=None) -> bytes:
    values = obj.bson_encode()
    class_name = obj.__class__.__name__
    values[CLASSNAME_KEY] = class_name
    return encode_document(values, traversal_stack, obj,
                           generator_func, on_unknown)


def encode_object_element(name: Key, value: BSONCoding, traversal_stack: TraversalStack,
                          generator_func: GeneratorFunc, on_unknown: OnUnknown) -> bytes:
    return b"\x03" + encode_cstring(name) + \
           encode_object(value, traversal_stack,
                         generator_func=generator_func, on_unknown=on_unknown)


class _EmptyClass:
    pass


def decode_object(raw_values: AnyDict) -> Any:
    global classes
    class_name = raw_values[CLASSNAME_KEY]
    try:
        cls = classes[class_name]
    except KeyError as e:
        raise MissingClassDefinition(class_name) from e

    retval = _EmptyClass()
    retval.__class__ = cls
    assert isinstance(retval, BSONCoding)
    alt_retval = retval.bson_init(raw_values)  # pylint: disable=no-member
    return alt_retval or retval


def encode_string(value: str) -> bytes:
    bvalue = value.encode("utf-8")
    length = len(bvalue)
    return struct.pack(f"<i{length}sb", length + 1, bvalue, 0)


def encode_cstring(value: Key) -> bytes:
    if not isinstance(value, bytes):
        value = str(value).encode("utf-8")
    if b"\x00" in value:
        raise ValueError("Element names may not include NUL bytes.")
        # A NUL byte is used to delimit our string, accepting one would cause
        # our string to terminate early.
    return value + b"\x00"


def encode_binary(value: bytes, binary_subtype: int=0) -> bytes:
    length = len(value)
    return struct.pack("<ib", length, binary_subtype) + value


def encode_double(value: float) -> bytes:
    return struct.pack("<d", value)


ELEMENT_TYPES = {
    0x01: "double",
    0x02: "string",
    0x03: "document",
    0x04: "array",
    0x05: "binary",
    0x07: "object_id",
    0x08: "boolean",
    0x09: "UTCdatetime",
    0x0A: "none",
    0x10: "int32",
    0x11: "uint64",
    0x12: "int64"
}


def encode_double_element(name: Key, value: float) -> bytes:
    return b"\x01" + encode_cstring(name) + encode_double(value)


def encode_string_element(name: Key, value: str) -> bytes:
    return b"\x02" + encode_cstring(name) + encode_string(value)


def encode_value(name: Key, value: Any, buf: StringIO, traversal_stack: TraversalStack,
                 generator_func: GeneratorFunc, on_unknown: OnUnknown=None) -> None:
    if isinstance(value, bool):
        buf.write(encode_boolean_element(name, value))
    elif isinstance(value, int):
        if value < -0x80000000 or 0x7FFFFFFFFFFFFFFF >= value > 0x7fffffff:
            buf.write(encode_int64_element(name, value))
        elif value > 0x7FFFFFFFFFFFFFFF:
            if value > 0xFFFFFFFFFFFFFFFF:
                raise ValueError(f"BSON format supports only int value < {0xFFFFFFFFFFFFFFFF}")
            buf.write(encode_uint64_element(name, value))
        else:
            buf.write(encode_int32_element(name, value))
    elif isinstance(value, Int32):
        buf.write(encode_int32_element(name, value.get_value()))
    elif isinstance(value, Int64):
        buf.write(encode_int64_element(name, value.get_value()))
    elif isinstance(value, UInt64):
        buf.write(encode_uint64_element(name, value.get_value()))
    elif isinstance(value, float):
        buf.write(encode_double_element(name, value))
    elif isinstance(value, str):
        buf.write(encode_string_element(name, value))
    elif isinstance(value, bytes):
        buf.write(encode_binary_element(name, value))
    elif isinstance(value, UUID):
        buf.write(encode_binary_element(name, value.bytes, binary_subtype=4))
    elif isinstance(value, datetime):
        buf.write(encode_utc_datetime_element(name, value))
    elif value is None:
        buf.write(encode_none_element(name))
    elif isinstance(value, dict):
        buf.write(encode_document_element(name, value, traversal_stack,
                                          generator_func, on_unknown))
    elif isinstance(value, (list, tuple)):
        buf.write(encode_array_element(name, value, traversal_stack,
                                       generator_func, on_unknown))
    elif isinstance(value, BSONCoding):
        buf.write(encode_object_element(name, value, traversal_stack,
                                        generator_func, on_unknown))
    elif isinstance(value, Decimal):
        buf.write(encode_double_element(name, float(value)))
    else:
        if on_unknown is not None:
            encode_value(name, on_unknown(value), buf, traversal_stack,
                         generator_func, on_unknown)
        else:
            raise UnknownSerializerError(name, value)


def encode_document(obj: AnyDict, traversal_stack: TraversalStack, traversal_parent: object=None,
                    generator_func: GeneratorFunc=None, on_unknown: OnUnknown=None) -> bytes:
    buf = StringIO()
    key_iter = iter(obj.keys())
    if generator_func is not None:
        key_iter = generator_func(obj, traversal_stack)
    for name in key_iter:
        value = obj[name]
        traversal_stack.append(TraversalStep(traversal_parent or obj, name))
        encode_value(name, value, buf, traversal_stack,
                     generator_func, on_unknown)
        traversal_stack.pop()
    e_list = buf.getvalue()
    e_list_length = len(e_list)
    return struct.pack(f"<i{e_list_length}sb",
                       e_list_length + 4 + 1, e_list, 0)


def encode_array(array: Union[AnyList, AnyTuple], traversal_stack: TraversalStack, traversal_parent: object=None,
                 generator_func: GeneratorFunc=None, on_unknown: OnUnknown=None) -> bytes:
    buf = StringIO()
    for i, value in enumerate(array):
        traversal_stack.append(TraversalStep(traversal_parent or array, i))
        encode_value(str(i), value, buf, traversal_stack,
                     generator_func, on_unknown)
        traversal_stack.pop()
    e_list = buf.getvalue()
    e_list_length = len(e_list)
    return struct.pack(f"<i{e_list_length}sb",
                       e_list_length + 4 + 1, e_list, 0)


def decode_binary_subtype(value: bytes, binary_subtype: int)-> Union[UUID, bytes]:
    if binary_subtype in [0x03, 0x04]:  # legacy UUID, UUID
        return UUID(bytes=value)
    return value


def decode_document(data: bytes, base: int, as_array: bool=False) -> Tuple[int, Any]:
    # Create all the struct formats we might use.
    double_struct = struct.Struct("<d")
    int_struct = struct.Struct("<i")
    char_struct = struct.Struct("<b")
    long_struct = struct.Struct("<q")
    uint64_struct = struct.Struct("<Q")
    int_char_struct = struct.Struct("<ib")

    length = struct.unpack("<i", data[base:base + 4])[0]
    end_point = base + length
    if data[end_point - 1] not in ('\0', 0):
        raise ValueError('missing null-terminator in document')
    base += 4

    retval: Union[AnyDict, AnyList] = [] if as_array else {}
    decode_name = not as_array
    name: Optional[Key] = None

    while base < end_point - 1:

        element_type = char_struct.unpack(data[base:base + 1])[0]

        ll = data.index(0, base + 1) + 1
        if decode_name:
            name = data[base + 1:ll - 1]
            try:
                name = name.decode("utf-8")
            except UnicodeDecodeError:
                pass
        else:
            name = None
        base = ll

        if element_type == 0x01:  # double
            value = double_struct.unpack(data[base: base + 8])[0]
            base += 8
        elif element_type == 0x02:  # string
            length = int_struct.unpack(data[base:base + 4])[0]
            value = data[base + 4: base + 4 + length - 1]
            value = value.decode("utf-8")
            base += 4 + length
        elif element_type == 0x03:  # document
            base, value = decode_document(data, base)
        elif element_type == 0x04:  # array
            base, value = decode_document(data, base, as_array=True)
        elif element_type == 0x05:  # binary
            length, binary_subtype = int_char_struct.unpack(
                data[base:base + 5])
            value = data[base + 5:base + 5 + length]
            value = decode_binary_subtype(value, binary_subtype)
            base += 5 + length
        elif element_type == 0x07:  # object_id
            value = b2a_hex(data[base:base + 12])
            base += 12
        elif element_type == 0x08:  # boolean
            value = bool(char_struct.unpack(data[base:base + 1])[0])
            base += 1
        elif element_type == 0x09:  # UTCdatetime
            value = datetime.fromtimestamp(
                long_struct.unpack(data[base:base + 8])[0] / 1000.0, tz=timezone.utc)
            base += 8
        elif element_type == 0x0A:  # none
            value = None
        elif element_type == 0x10:  # int32
            value = int_struct.unpack(data[base:base + 4])[0]
            base += 4
        elif element_type == 0x11:  # uint64
            value = uint64_struct.unpack(data[base:base + 8])[0]
            base += 8
        elif element_type == 0x12:  # int64
            value = long_struct.unpack(data[base:base + 8])[0]
            base += 8
        else:
            raise ValueError(f"Unknown element type: {element_type}")

        if isinstance(retval, list):
            retval.append(value)
        else:
            assert name is not None
            retval[name] = value

    if isinstance(retval, dict) and CLASSNAME_KEY in retval:
        return end_point, decode_object(retval)
    else:
        return end_point, retval


def encode_document_element(name: Key, value: AnyDict, traversal_stack: TraversalStack,
                            generator_func: GeneratorFunc, on_unknown: OnUnknown) -> bytes:
    return b"\x03" + encode_cstring(name) + \
           encode_document(value, traversal_stack,
                           generator_func=generator_func, on_unknown=on_unknown)


def encode_array_element(name: Key, value: Union[AnyList, AnyTuple], traversal_stack: TraversalStack,
                         generator_func: GeneratorFunc, on_unknown: OnUnknown) -> bytes:
    return b"\x04" + encode_cstring(name) + \
           encode_array(value, traversal_stack,
                        generator_func=generator_func, on_unknown=on_unknown)


def encode_binary_element(name: Key, value: bytes, binary_subtype: int=0) -> bytes:
    return b"\x05" + encode_cstring(name) + encode_binary(value, binary_subtype=binary_subtype)


def encode_boolean_element(name: Key, value: bool) -> bytes:
    return b"\x08" + encode_cstring(name) + struct.pack("<b", value)


def encode_utc_datetime_element(name: Key, value: datetime) -> bytes:
    if value.tzinfo is None:
        warnings.warn(MissingTimezoneWarning(), None, 4)
    bvalue = int(round(calendar.timegm(value.utctimetuple()) * 1000 +
                      (value.microsecond / 1000.0)))
    return b"\x09" + encode_cstring(name) + struct.pack("<q", bvalue)


def encode_none_element(name: Key) -> bytes:
    return b"\x0a" + encode_cstring(name)


def encode_int32_element(name: Key, value: int) -> bytes:
    bvalue = struct.pack("<i", value)
    return b"\x10" + encode_cstring(name) + bvalue


def encode_uint64_element(name: Key, value: int) -> bytes:
    return b"\x11" + encode_cstring(name) + struct.pack("<Q", value)


def encode_int64_element(name: Key, value: int) -> bytes:
    return b"\x12" + encode_cstring(name) + struct.pack("<q", value)


def encode_object_id_element(name: Key, value: bytes) -> bytes:
    return b"\x07" + encode_cstring(name) + value
