from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import ContentType, Message
from line import LINE
from logger import logger

line = LINE()
tracer = line.tracer


class ContentHook(HooksTracer):
    @tracer.Content(ContentType.NONE)
    def text_message(self, msg: Message, cl: CHRLINE) -> None:
        if tracer.trace(msg, self.HooksType["Command"], cl):
            logger.debug(f"{msg.to} | {msg.text}")
            return
        logger.info(f"{msg.to} | {msg.text}")
