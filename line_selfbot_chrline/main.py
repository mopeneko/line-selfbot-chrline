from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import (
    OpType,
    Operation,
    ContentType,
    Message,
    MIDType,
)

cl = CHRLINE(device="DESKTOPWIN", useThrift=True)

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


tracer.run()
