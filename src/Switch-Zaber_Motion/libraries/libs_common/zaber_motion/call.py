from threading import Lock
import asyncio
import functools
from typing import TYPE_CHECKING, Optional, List, Set, Callable, Any, TypeVar, overload  # pylint: disable=unused-import
from ctypes import c_void_p, c_int64
import queue
from .dto_object import DtoObject

from .convert_exception import convert_exception
from .dto import requests as dto
from .serialization import serialize, deserialize
from .bindings import c_call, CALLBACK
from .version import __version__

TResponse = TypeVar('TResponse', bound=DtoObject)  # pylint: disable=invalid-name


class CallbackWrap:
    def __init__(self, callbackFunc: Callable[[c_void_p, c_int64], None]):
        self._callback = CALLBACK(callbackFunc)

    @property
    def callback(self) -> Any:
        return self._callback


# we must store callback in a set to prevent garbage collection in case the future gets cancelled
callbacks: Set[CallbackWrap] = set()
callbacks_lock = Lock()


@overload
def call(
    request: str,
    data: Optional[DtoObject] = None,
) -> None:
    ...


@overload
def call(
    request: str,
    data: Optional[DtoObject],
    make_response: Callable[[bytes], TResponse],
) -> TResponse:
    ...


def call(
    request: str,
    data: Optional[DtoObject] = None,
    make_response: Optional[Callable[[bytes], TResponse]] = None,
) -> Optional[TResponse]:
    buffer = get_request_buffer(request, data)

    promise = queue.Queue(maxsize=1)  # type: ignore

    def callback(response_data: c_void_p, _tag: c_int64) -> None:
        resp_buffer = deserialize(response_data)
        promise.put(resp_buffer)

    cb = CALLBACK(callback)
    result = c_call(buffer, 0, cb, 1)

    if result != 0:
        raise RuntimeError(f"Invalid result code: {result}")

    response_buffers = promise.get()

    return process_response(response_buffers, make_response)


def set_result(future: 'asyncio.Future[List[bytes]]', resp_buffer: List[bytes]) -> None:
    if not future.done():
        future.set_result(resp_buffer)


@overload
async def call_async(
    request: str,
    data: Optional[DtoObject] = None,
) -> None:
    ...


@overload
async def call_async(
    request: str,
    data: Optional[DtoObject],
    make_response: Callable[[bytes], TResponse],
) -> TResponse:
    ...


async def call_async(
    request: str,
    data: Optional[DtoObject] = None,
    make_response: Optional[Callable[[bytes], TResponse]] = None,
) -> Optional[TResponse]:
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
        raise RuntimeError(f"Invalid result code: {result}")

    response_buffers = await future

    return process_response(response_buffers, make_response)


@overload
def call_sync(
    request: str,
    data: Optional[DtoObject] = None,
) -> None:
    ...


@overload
def call_sync(
    request: str,
    data: Optional[DtoObject],
    make_response: Callable[[bytes], TResponse],
) -> TResponse:
    ...


def call_sync(
    request: str,
    data: Optional[DtoObject] = None,
    make_response: Optional[Callable[[bytes], TResponse]] = None,
) -> Optional[TResponse]:
    buffer = get_request_buffer(request, data)

    resp_buffers = [None]  # type: Any

    def callback(response_data: c_void_p, _tag: c_int64) -> None:
        resp_buffers[0] = deserialize(response_data)

    cb = CALLBACK(callback)
    result = c_call(buffer, 0, cb, 0)

    if result != 0:
        raise RuntimeError(f"Invalid result code: {result}")

    return process_response(resp_buffers[0], make_response)


def get_request_buffer(request: str, data: Optional[DtoObject]) -> bytes:
    request_proto = dto.GatewayRequest(request=request)

    messages = [request_proto.to_binary()]
    if data is not None:
        messages.append(data.to_binary())

    buffer = serialize(messages)
    return buffer


def process_response(
    response_buffers: List[bytes],
    make_response: Optional[Callable[[bytes], TResponse]],
) -> Optional[TResponse]:
    response_dto = dto.GatewayResponse.from_binary(response_buffers[0])

    if response_dto.response != dto.ResponseType.OK:
        if len(response_buffers) > 1:
            raise convert_exception(response_dto.error_type, response_dto.error_message, response_buffers[1])
        raise convert_exception(response_dto.error_type, response_dto.error_message)

    if len(response_buffers) > 1:
        if make_response is None:
            raise RuntimeError("Response from library is ignored, response_data==None")
        return make_response(response_buffers[1])
    else:
        if make_response is not None:
            raise RuntimeError("No response from library")
        return None


def check_version() -> None:
    request = dto.CheckVersionRequest(
        host="py",
        version=__version__,
    )
    call_sync("library/check_version", request)


check_version()
