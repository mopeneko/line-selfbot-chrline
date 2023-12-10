import os
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import Message, MIDType


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=MetaSingleton):
    pass


class LINE(Singleton):
    def __init__(self):
        cl = CHRLINE(
            authTokenOrEmail=os.getenv("LINE_AUTHTOKEN"),
            device="IOSIPAD",
            useThrift=True,
        )
        self.tracer = HooksTracer(cl)

    def is_e2ee(self, msg: Message) -> bool:
        if hasattr(msg, "isE2EE"):
            return msg.isE2EE
        return bool(msg.chunks)

    def send_message(self, got_msg: Message, text: str) -> None:
        to = self.get_to(got_msg)
        if self.is_e2ee(got_msg):
            self.tracer.cl.sendCompactE2EEMessage(to, text)
            return
        self.tracer.cl.sendCompactMessage(to, text)

    def get_to(self, msg: Message) -> str:
        to = msg.to

        return to
