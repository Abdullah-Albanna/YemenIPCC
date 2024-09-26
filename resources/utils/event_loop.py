import asyncio
import threading
import time

class NewEventLoop(threading.Thread):
    def __init__(self):
        super().__init__(target=self._start_loop)

        self.loop = None

        self.daemon = True

        self.start()

    def _start_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def getLoop(self):
        if self.loop is None:
            time.sleep(0.1)

        return self.loop
