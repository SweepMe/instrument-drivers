import atexit
from concurrent.futures import ThreadPoolExecutor
from typing import List
from ctypes import c_void_p, c_int64
import traceback
from rx.subject import Subject

from .protobufs import main_pb2
from .serialization import deserialize
from .bindings import c_set_event_handler, CALLBACK

events = Subject()

event_executor = ThreadPoolExecutor(max_workers=1)  # pylint: disable=consider-using-with


def on_shutdown() -> None:
    event_executor.shutdown()


atexit.register(on_shutdown)


def event_handler(event_data: c_void_p, _tag: c_int64) -> None:
    try:
        event_buffers = deserialize(event_data)
        event_executor.submit(process_event_catch, event_buffers)
    except RuntimeError:
        # the error appears due to race condition with python shutting down and cannot be prevented
        pass


event_handler_cb = CALLBACK(event_handler)

c_set_event_handler(0, event_handler_cb)

parsers = {
    'test/event': main_pb2.TestEvent,
    'interface/unknown_response': main_pb2.UnknownResponseEvent,
    'binary/interface/unknown_response': main_pb2.UnknownBinaryResponseEvent,
    'interface/alert': main_pb2.AlertEvent,
    'binary/interface/reply_only': main_pb2.BinaryReplyOnlyEvent,
    'interface/disconnected': main_pb2.DisconnectedEvent,
}


def process_event_catch(event_buffers: List[bytes]) -> None:
    try:
        process_event(event_buffers)
    except:  # noqa, pylint: disable=W0702
        print("Unhandled exception in event:")
        traceback.print_exc()


def process_event(event_buffers: List[bytes]) -> None:
    event = main_pb2.Event()
    event.ParseFromString(event_buffers[0])

    EventData = parsers.get(event.event, False)
    if EventData is False:
        raise Exception("Unknown event: {}".format(event.event))

    has_parser = EventData is not None
    has_data = len(event_buffers) > 1

    if has_data != has_parser:
        raise Exception("Event has no data or parser not provided for {}".format(event.event))

    event_data = None
    if has_data:
        event_data = EventData()  # type: ignore
        event_data.ParseFromString(event_buffers[1])

    event_tuple = (event.event, event_data)
    events.on_next(event_tuple)
