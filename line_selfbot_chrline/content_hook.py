from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import ContentType, Message
from line import LINE

line = LINE()
tracer = line.tracer


class ContentHook(HooksTracer):
    @tracer.Content(ContentType.NONE)
    def text_message(self, msg: Message, cl: CHRLINE) -> None:
        tracer.trace(msg, self.HooksType["Command"], cl)
