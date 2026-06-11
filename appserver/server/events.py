import threading
from collections import deque
from datetime import datetime


class EventLog:
    def __init__(self, maxlen=1000):
        self._lock = threading.Lock()
        self._events = deque(maxlen=maxlen)
        self._seq = 0

    def add(self, kind, **data):
        with self._lock:
            self._seq += 1
            entry = {"seq": self._seq, "kind": kind, "ts": datetime.now().strftime("%H:%M:%S")}
            entry.update(data)
            self._events.append(entry)

    def since(self, last_seq):
        with self._lock:
            return [e for e in self._events if e["seq"] > last_seq]

    def all(self):
        with self._lock:
            return list(self._events)

    def clear(self):
        with self._lock:
            self._events.clear()
            self._seq = 0


events = EventLog()
