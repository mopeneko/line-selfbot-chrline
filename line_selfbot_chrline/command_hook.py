from typing import Dict
from CHRLINE import CHRLINE
from CHRLINE.hooks import HooksTracer
from CHRLINE.services.thrift.ttypes import Message
from db_keys import DBKeys
from line import LINE

line = LINE()
tracer = line.tracer


class CommandHook(HooksTracer):
    @tracer.Command()
    def help(self, msg: Message, cl: CHRLINE) -> None:
        """ヘルプを送信"""

        text = self.genHelp(self.getPrefix(msg.text))
        line.send_message(msg, text)

    @tracer.Command()
    def test(self, msg: Message, cl: CHRLINE) -> None:
        """botの動作テスト"""

        line.send_message(msg, "OK")

    @tracer.Command()
    def status(self, msg: Message, cl: CHRLINE) -> None:
        """設定情報を送信"""

        to = line.get_to(msg)

        statuses: Dict[str, str] = {}

        def bool_to_str(v: bool) -> str:
            if v:
                return "オン"
            return "オフ"

        message_recover = False
        data: Dict[str, bool] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        if to in data.keys():
            message_recover = True

        statuses["送信取り消し"] = bool_to_str(message_recover)

        greeting = False
        greeting_message = ""
        data: Dict[str, str] = self.db.getData(DBKeys.GREETING, {})
        if to in data.keys():
            greeting = True
            greeting_message = data[to]

        statuses["参加挨拶"] = bool_to_str(greeting)
        if greeting:
            statuses["参加挨拶メッセージ"] = greeting_message

        text = "\n".join([f"{k}: {v}" for k, v in statuses.items()])
        line.send_message(msg, text)

    @tracer.Command(alt=["recover on"])
    def recover_on(self, msg: Message, cl: CHRLINE) -> None:
        """メッセージ復元を有効化"""

        data: Dict[str, bool] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        to = line.get_to(msg)

        if to in data.keys():
            line.send_message(msg, "既に有効です。")
            return

        data[to] = True
        self.db.saveData(DBKeys.MESSAGE_RECOVER, data)

        line.send_message(msg, "有効にしました。")

    @tracer.Command(alt=["recover off"])
    def recover_off(self, msg: Message, cl: CHRLINE) -> None:
        """メッセージ復元を無効化"""

        data: Dict[str, bool] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        to = line.get_to(msg)

        if to not in data.keys():
            line.send_message(msg, "既に無効です。")
            return

        del data[to]
        self.db.saveData(DBKeys.MESSAGE_RECOVER, data)

        line.send_message(msg, "無効にしました。")

    @tracer.Command(alt=["greeting on"])
    def greeting_on(self, msg: Message, cl: CHRLINE) -> None:
        """参加挨拶を有効化"""

        data: Dict[str, str] = self.db.getData(DBKeys.GREETING, {})
        to = line.get_to(msg)

        if to in data.keys():
            line.send_message(msg, "既に有効です。")
            return

        data[to] = "よろしく！"
        self.db.saveData(DBKeys.GREETING, data)

        line.send_message(msg, "有効にしました。\n挨拶の初期設定は「よろしく！」です。\n「greeting:文字列」で変更できます。")

    @tracer.Command(alt=["greeting off"])
    def greeting_off(self, msg: Message, cl: CHRLINE) -> None:
        """参加挨拶を無効化"""

        data: Dict[str, str] = self.db.getData(DBKeys.GREETING, {})
        to = line.get_to(msg)

        if to not in data.keys():
            line.send_message(msg, "既に無効です。")
            return

        del data[to]
        self.db.saveData(DBKeys.GREETING, data)

        line.send_message(msg, "無効にしました。")

    @tracer.Command(splitchar=":")
    def greeting(self, msg: Message, cl: CHRLINE) -> None:
        """参加挨拶を設定"""

        data: Dict[str, str] = self.db.getData(DBKeys.GREETING, {})
        to = line.get_to(msg)

        args = self.getArgs(msg.text)
        if not args or len(args) != 1:
            line.send_message(msg, "参加挨拶が指定されていません。")
            return

        data[to] = args[0]
        self.db.saveData(DBKeys.GREETING, data)

        line.send_message(msg, "参加挨拶を設定しました。")

    @tracer.Command()
    def mentionees(self, msg: Message, cl: CHRLINE) -> None:
        """メンション確認"""

        data: Dict[str, list] = self.db.getData(DBKeys.MENTION, {})
        to = line.get_to(msg)

        if to not in data or len(data[to]) == 0:
            line.send_message(msg, "メンションはありません。")
            return

        for i, msg_id in enumerate(data[to]):
            cl.replyMessage(msg, text=str(i + 1), relatedMessageId=msg_id)

        del data[to]
        self.db.saveData(DBKeys.MENTION, data)

    @tracer.Command()
    def debug(self, msg: Message, cl: CHRLINE) -> None:
        """デバッグ用コマンド"""

        related_message_id = msg.relatedMessageId
        if not related_message_id:
            line.send_message(msg, "リプライでメッセージを指定してください。")
            return

        to = line.get_to(msg)
        msgs = cl.getRecentMessagesV2(to)
        for msg in msgs:
            if msg.id != related_message_id:
                continue

            if msg.chunks:
                msg.text = cl.decryptE2EETextMessage(msg, isSelf=False)
            line.send_message(msg, str(msg))
            return

        line.send_message(msg, "メッセージが見つかりませんでした。")
