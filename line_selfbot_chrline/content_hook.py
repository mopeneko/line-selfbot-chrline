from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import ContentType, Message, MIDType
from line import LINE
from logger import logger

line = LINE()
tracer = line.tracer


class ContentHook(HooksTracer):
    @tracer.Content(ContentType.NONE)
    def text_message(self, msg: Message, cl: CHRLINE) -> None:
        tracer.trace(msg, self.HooksType["Command"], cl)
        to_id = msg.to
        if msg.toType == MIDType.GROUP:
            to_name = cl.getChats([to_id]).chats[0].chatName
        else:
            to_name = cl.getContact(to_id).displayName
        logger.info(f"{to_id}({to_name}) | {msg.text}")
