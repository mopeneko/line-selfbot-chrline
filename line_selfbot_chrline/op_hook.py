from typing import Dict, List
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import (
    OpType,
    Operation,
    ContentType,
    Message,
    Contact,
)
from db_keys import DBKeys
from line import LINE

line = LINE()
tracer = line.tracer


class OpHook(HooksTracer):
    @tracer.Operation(OpType.SEND_MESSAGE)
    def send_message(self, op: Operation, cl: CHRLINE) -> None:
        tracer.trace(op.message, self.HooksType["Content"], cl)

    @tracer.Operation(OpType.NOTIFIED_DESTROY_MESSAGE)
    def notified_destroy_message(self, op: Operation, cl: CHRLINE) -> None:
        to = op.param1
        msg_id = op.param2

        msgs: List[Message] = cl.getRecentMessagesV2(to)
        for msg in msgs:
            if msg.id != msg_id:
                continue

            if msg.contentType != ContentType.NONE:
                return

            data: Dict[str, bool] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
            if to not in data.keys():
                return

            contact: Contact = cl.getContact(msg._from)

            text = f"メッセージが取り消されました。\n\n送信者: {contact.displayName}\n{msg.text}"
            line.send_message(msg, text)
            return
