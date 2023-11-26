from enum import Enum
from typing import Dict, List
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


class DBKeys(Enum):
    MESSAGE_RECOVER = "message_recover"


def send_message(got_msg: Message, text: str, cl: CHRLINE) -> None:
    to = get_to(got_msg)
    try:
        if got_msg.isE2EE:
            cl.sendCompactE2EEMessage(to, text)
            return
        cl.sendCompactMessage(to, text)
    except:
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
            if msg.id != msg_id:
                continue

            if msg.contentType != ContentType.NONE:
                return

            data: Dict[str] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
            if to not in data.keys():
                return

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
    def status(self, msg: Message, cl: CHRLINE) -> None:
        """設定情報を送信"""
        to = get_to(msg)

        message_recover = False
        data: Dict[str] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        if to in data.keys():
            message_recover = True

        def bool_to_str(v: bool) -> str:
            if v:
                return "オン"
            return "オフ"

        text = f"""送信取り消し: {bool_to_str(message_recover)}"""
        send_message(msg, text, cl)

    @tracer.Command()
    def recover_on(self, msg: Message, cl: CHRLINE) -> None:
        """メッセージ復元を有効化"""

        data: Dict[str] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        to = get_to(msg)

        if to in data.keys():
            send_message(msg, "既に有効です。", cl)
            return

        data[to] = True
        self.db.saveData(DBKeys.MESSAGE_RECOVER, data)

        send_message(msg, "有効にしました。", cl)

    @tracer.Command()
    def recover_off(self, msg: Message, cl: CHRLINE) -> None:
        """メッセージ復元を無効化"""

        data: Dict[str] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        to = get_to(msg)

        if to not in data.keys():
            send_message(msg, "既に無効です。", cl)
            return

        del data[to]
        self.db.saveData(DBKeys.MESSAGE_RECOVER, data)

        send_message(msg, "無効にしました。", cl)

    @tracer.Command()
    def debug(self, msg: Message, cl: CHRLINE) -> None:
        """デバッグ用コマンド"""

        print(msg)
        send_message(msg, "ターミナル見てね", cl)


tracer.run()
