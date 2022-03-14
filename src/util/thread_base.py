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

    def add_task(self, task, freq=100, name=''):
        thread = BaseHelperThread(task, self.running_event, freq)
        if name != '':
            thread.name = name
        if self.running_event.is_set():
            thread.start()
        self.threads.append(thread)


class BaseHelperThread(threading.Thread):
    def __init__(self, task, running_event, freq):
        super().__init__(daemon=True)
        self.running_flag: threading.Event = running_event
        self.task = task
        self.sleep = 1/freq

    def run(self):
        running = self.running_flag
        interval = self.sleep

        while running.is_set():
            try:
                self.task()
            except RuntimeError as ex:
                # running.clear()
                print(ex.with_traceback(None))
                break
            sleep(interval)
        properly = 'with an error' if running.is_set() else 'properly'
        print(f'Thread {self.name} closed {properly}')