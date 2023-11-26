import json
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

    @tracer.Operation(OpType.NOTIFIED_JOIN_CHAT)
    def notified_join_chat(self, op: Operation, cl: CHRLINE) -> None:
        gid = op.param1

        data: Dict[str, str] = self.db.getData(DBKeys.GREETING, {})
        if gid not in data.keys():
            return

        text = data[gid]
        line.send_message(gid, text)

    @tracer.Operation(OpType.RECEIVE_MESSAGE)
    def receive_message(self, op: Operation, cl: CHRLINE) -> None:
        msg = op.message

        if msg.contentType != ContentType.NONE:
            return

        if "MENTION" not in msg.contentMetadata:
            return

        mention_data = json.loads(msg.contentMetadata["MENTION"])
        for mention in mention_data["MENTIONEES"]:
            if ("A" in mention.keys() and mention["A"] == 1) or (
                "M" in mention.keys() and mention["M"] == cl.profile.mid
            ):
                data: Dict[str, list] = self.db.getData(DBKeys.MENTION, {})
                to = line.get_to(msg)
                if to not in data:
                    data[to] = []
                data[to].append(msg.id)
                self.db.saveData(DBKeys.MENTION, data)
