from threading import Lock
import asyncio
import functools
from typing import TYPE_CHECKING, Optional, List, Set, Callable, Any  # pylint: disable=unused-import
from ctypes import c_void_p, c_int64
import queue
from google.protobuf.message import Message

from .convert_exception import convert_exception
from .protobufs import main_pb2
from .serialization import serialize, deserialize
from .bindings import c_call, CALLBACK


class CallbackWrap:
    def __init__(self, callbackFunc: Callable[[c_void_p, c_int64], None]):
        self._callback = CALLBACK(callbackFunc)

    @property
    def callback(self) -> Any:
        return self._callback


# we must store callback in a set to prevent garbage collection in case the future gets cancelled
callbacks: Set[CallbackWrap] = set()
callbacks_lock = Lock()


def call(request: str, data: Optional[Message] = None, response_data: Optional[Message] = None) -> None:
    buffer = get_request_buffer(request, data)

    promise = queue.Queue(maxsize=1)  # type: ignore

    def callback(response_data: c_void_p, _tag: c_int64) -> None:
        resp_buffer = deserialize(response_data)
        promise.put(resp_buffer)

    cb = CALLBACK(callback)
    result = c_call(buffer, 0, cb, 1)

    if result != 0:
        raise Exception("Invalid result code: {}".format(result))

    response_buffers = promise.get()

    process_response(response_buffers, response_data)


def set_result(future: 'asyncio.Future[List[bytes]]', resp_buffer: List[bytes]) -> None:
    if not future.done():
        future.set_result(resp_buffer)


async def call_async(request: str, data: Optional[Message] = None, response_data: Optional[Message] = None) -> None:
    buffer = get_request_buffer(request, data)

    cb: CallbackWrap = None  # type: ignore
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def callback(response_data: c_void_p, _tag: c_int64) -> None:
        resp_buffer = deserialize(response_data)

        try:
            loop.call_soon_threadsafe(functools.partial(set_result, future, resp_buffer))
        except RuntimeError:
            # the loop may be done already
            pass

        with callbacks_lock:
            callbacks.remove(cb)

    cb = CallbackWrap(callback)
    with callbacks_lock:
        callbacks.add(cb)

    result = c_call(buffer, 0, cb.callback, 1)

    if result != 0:
        raise Exception("Invalid result code: {}".format(result))

    response_buffers = await future

    process_response(response_buffers, response_data)


def call_sync(request: str, data: Optional[Message] = None, response_data: Optional[Message] = None) -> None:
    buffer = get_request_buffer(request, data)

    resp_buffers = [None]  # type: Any

    def callback(response_data: c_void_p, _tag: c_int64) -> None:
        resp_buffers[0] = deserialize(response_data)

    cb = CALLBACK(callback)
    result = c_call(buffer, 0, cb, 0)

    if result != 0:
        raise Exception("Invalid result code: {}".format(result))

    process_response(resp_buffers[0], response_data)


def get_request_buffer(request: str, data: Optional[Message]) -> bytes:
    request_proto = main_pb2.Request()
    request_proto.request = request

    messages = [request_proto.SerializeToString()]
    if data is not None:
        messages.append(data.SerializeToString())

    buffer = serialize(messages)
    return buffer


def process_response(response_buffers: List[bytes], response_data: Optional[Message]) -> None:
    response_proto = main_pb2.Response()
    response_proto.ParseFromString(response_buffers[0])

    if response_proto.response != main_pb2.Response.OK:
        if len(response_buffers) > 1:
            raise convert_exception(response_proto.error_type, response_proto.error_message, response_buffers[1])
        raise convert_exception(response_proto.error_type, response_proto.error_message)

    if len(response_buffers) > 1:
        if response_data is None:
            raise Exception("Response from library is ignored, response_data==None")
        response_data.ParseFromString(response_buffers[1])
    else:
        if response_data is not None:
            raise Exception("No response from library")
