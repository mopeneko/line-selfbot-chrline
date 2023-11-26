from typing import List
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import (
    OpType,
    Operation,
    ContentType,
    Message,
    MIDType,
)

cl = CHRLINE(device="IOSIPAD", useThrift=True)

tracer = HooksTracer(cl)


def send_message(got_msg: Message, text: str, cl: CHRLINE) -> None:
    to = get_to(got_msg)
    if got_msg.isE2EE:
        cl.sendCompactE2EEMessage(to, text)
        return
    cl.sendCompactMessage(to, text)


def get_to(msg: Message) -> str:
    to = msg.to
    if msg.toType == MIDType.USER:
        to = msg.from_

    return to


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
            if msg.id == msg_id:
                if msg.contentType == ContentType.NONE:
                    text = f"メッセージが取り消されました。\n\n{msg.text}"
                    send_message(msg, text, cl)
                return


class ContentHook(HooksTracer):
    @tracer.Content(ContentType.NONE)
    def text_message(self, msg: Message, cl: CHRLINE) -> None:
        tracer.trace(msg, self.HooksType["Command"], cl)


class CommandHook(HooksTracer):
    @tracer.Command()
    def help(self, msg: Message, cl: CHRLINE) -> None:
        """ヘルプを送信"""

        text = self.genHelp(self.getPrefix(msg.text))
        send_message(msg, text, cl)

    @tracer.Command()
    def test(self, msg: Message, cl: CHRLINE) -> None:
        """botの動作テスト"""

        send_message(msg, "OK", cl)

    @tracer.Command()
    def debug(self, msg: Message, cl: CHRLINE) -> None:
        """デバッグ用コマンド"""

        print(msg)
        send_message(msg, "ターミナル見てね", cl)


tracer.run()
