import atexit
from concurrent.futures import ThreadPoolExecutor
from typing import List, TypeVar, Generic, Type, Literal, TypedDict, cast
from ctypes import c_void_p, c_int64
import traceback
from reactivex.subject import Subject
from reactivex import Observable, operators as rxops

from .dto_object import DtoObject
from .dto import requests as dto
from .serialization import deserialize
from .bindings import c_set_event_handler, CALLBACK


TEventData = TypeVar('TEventData', bound=DtoObject)


class Event(Generic[TEventData]):
    def __init__(self, name: str, data: TEventData) -> None:
        self.name = name
        self.data = data


events = Subject[Event[DtoObject]]()

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

EventName = Literal[
    'test/event',
    'interface/unknown_response',
    'binary/interface/unknown_response',
    'interface/alert',
    'binary/interface/reply_only',
    'interface/disconnected',
]

ParsersDict = TypedDict('ParsersDict', {
    'test/event': Type[dto.TestEvent],
    'interface/unknown_response': Type[dto.UnknownResponseEventWrapper],
    'binary/interface/unknown_response': Type[dto.UnknownBinaryResponseEventWrapper],
    'interface/alert': Type[dto.AlertEventWrapper],
    'binary/interface/reply_only': Type[dto.BinaryReplyOnlyEventWrapper],
    'interface/disconnected': Type[dto.DisconnectedEvent],
})

parsers: ParsersDict = {
    'test/event': dto.TestEvent,
    'interface/unknown_response': dto.UnknownResponseEventWrapper,
    'binary/interface/unknown_response': dto.UnknownBinaryResponseEventWrapper,
    'interface/alert': dto.AlertEventWrapper,
    'binary/interface/reply_only': dto.BinaryReplyOnlyEventWrapper,
    'interface/disconnected': dto.DisconnectedEvent,
}


def process_event_catch(event_buffers: List[bytes]) -> None:
    try:
        process_event(event_buffers)
    except:  # noqa, pylint: disable=W0702
        print("Unhandled exception in event:")
        traceback.print_exc()


def process_event(event_buffers: List[bytes]) -> None:
    event = dto.GatewayEvent.from_binary(event_buffers[0])

    event_name = cast(EventName, event.event)
    parse_event_data = parsers.get(event_name)
    if parse_event_data is None:
        raise RuntimeError(f"Event not supported: {event_name}")

    event_data = parse_event_data.from_binary(event_buffers[1])
    events.on_next(Event(event_name, event_data))


def filter_events(
        name: EventName,
        data_type: Type[TEventData],
) -> Observable[TEventData]:
    assert parsers[name] is data_type

    def filter_name(event: Event[DtoObject]) -> bool:
        return event.name == name

    def map_data(event: Event[DtoObject]) -> TEventData:
        assert isinstance(event.data, data_type)
        return event.data

    return events.pipe(
        rxops.filter(filter_name),
        rxops.map(map_data))
