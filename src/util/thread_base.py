import threading
from time import sleep
from typing import List


class BaseThreadManager:
    def __init__(self, *args):
        self.running_event = threading.Event()
        self.threads: List[threading.Thread] = []

    def start(self):
        self.running_event.set()
        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running_event.clear()

    def add_thread(self, thread: threading.Thread):
        if self.running_event.is_set():
            thread.start()
        self.threads.append(thread)

    def add_task(self, task):
        thread = BaseHelperThread(task, self.running_event)
        if self.running_event.is_set():
            thread.start()
        self.threads.append(thread)


class BaseHelperThread(threading.Thread):
    def __init__(self, task, running_event):
        super().__init__(daemon=True)
        self.running_flag: threading.Event = running_event
        self.task = task

    def run(self):
        running = self.running_flag

        while running.is_set():
            self.task()
            sleep(0.01)