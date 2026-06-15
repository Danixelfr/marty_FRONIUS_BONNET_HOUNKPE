import threading
from collections import deque
from datetime import datetime


# journal des evenements (hello/start/step/bye) pour l'affichage live dans l'UI
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
        # l'UI donne le dernier seq qu'elle a affiche, on lui renvoie juste les nouveaux
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
