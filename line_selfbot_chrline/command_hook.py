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

        message_recover = False
        data: Dict[str, bool] = self.db.getData(DBKeys.MESSAGE_RECOVER, {})
        if to in data.keys():
            message_recover = True

        def bool_to_str(v: bool) -> str:
            if v:
                return "オン"
            return "オフ"

        text = f"""送信取り消し: {bool_to_str(message_recover)}"""
        line.send_message(msg, text)

    @tracer.Command()
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

    @tracer.Command()
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

    @tracer.Command()
    def debug(self, msg: Message, cl: CHRLINE) -> None:
        """デバッグ用コマンド"""

        print(msg)
        line.send_message(msg, "ターミナル見てね")
