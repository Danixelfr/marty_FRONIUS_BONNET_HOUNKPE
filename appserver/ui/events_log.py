from PyQt6.QtWidgets import QTextEdit
from server.events import events


class EventsLog(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")
        self._last_seq = 0

    def append_message(self, text):
        self.append(text)

    def poll(self):
        # on n'affiche que les nouveaux events depuis le dernier passage
        for e in events.since(self._last_seq):
            self._last_seq = e["seq"]
            self.append(self._format(e))

    def _format(self, e):
        ts = e.get("ts", "")
        kind = e["kind"]
        rid = e.get("rid", "?")
        if kind == "hello":
            return f"{ts} [HELLO]  {rid}"
        if kind == "start":
            return f"{ts} [START]  {rid} -> {e.get('mvs')} pas"
        if kind == "step":
            pts = e.get("points", 0)
            sign = "+" if pts >= 0 else ""
            arm = e.get("arm") or "-"
            return f"{ts} [STEP]   {rid}  col={e.get('col')} arm={arm} exp={e.get('exp')} -> {sign}{pts} (total {e.get('score')})"
        if kind == "bye":
            return f"{ts} [BYE]    {rid} (score final: {e.get('final_score')})"
        return f"{ts} [{kind.upper()}] {rid}"
