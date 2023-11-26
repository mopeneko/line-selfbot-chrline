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
        cl = CHRLINE(device="IOSIPAD", useThrift=True)
        self.tracer = HooksTracer(cl)

    def send_message(self, got_msg: Message, text: str) -> None:
        to = self.get_to(got_msg)
        try:
            if got_msg.isE2EE:
                self.tracer.cl.sendCompactE2EEMessage(to, text)
                return
            self.tracer.cl.sendCompactMessage(to, text)
        except:
            self.tracer.cl.sendCompactMessage(to, text)

    def get_to(self, msg: Message) -> str:
        to = msg.to
        if msg.toType == MIDType.USER:
            to = msg.from_

        return to
