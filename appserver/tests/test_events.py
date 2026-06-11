import unittest

from server.events import EventLog, events
from server.registry import registry
from server.routes.hello import handle_post_hello


class TestEventLog(unittest.TestCase):

    def test_add_and_since(self):
        log = EventLog()
        log.add("hello", rid="A")
        log.add("step", rid="A", points=6)
        evs = log.since(0)
        self.assertEqual(len(evs), 2)
        self.assertEqual(evs[0]["kind"], "hello")
        self.assertEqual(evs[1]["points"], 6)

    def test_since_only_new(self):
        log = EventLog()
        log.add("hello", rid="A")
        seen = log.since(0)[-1]["seq"]
        log.add("bye", rid="A")
        new = log.since(seen)
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0]["kind"], "bye")

    def test_maxlen(self):
        log = EventLog(maxlen=3)
        for i in range(5):
            log.add("step", points=i)
        self.assertEqual(len(log.all()), 3)

    def test_events_have_timestamp(self):
        log = EventLog()
        log.add("hello", rid="A")
        self.assertIn("ts", log.all()[0])


class TestRouteEmitsEvent(unittest.TestCase):

    def setUp(self):
        registry._robots.clear()
        events.clear()

    def test_hello_route_emits(self):
        class FH:
            def send_text(self, code, text):
                self.text = text
        handle_post_hello(FH())
        kinds = [e["kind"] for e in events.since(0)]
        self.assertIn("hello", kinds)


if __name__ == "__main__":
    unittest.main()
