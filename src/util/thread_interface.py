import threading
import tkinter

from time import sleep

from gui.gui_base import InterfaceVariables
from gui.gui_builder import build_interface
from util.agent_base import BaseTrainingEnvironment


class InterfaceMainThread(threading.Thread):
    def __init__(self, agent, running_event):
        super().__init__(daemon=True)
        self.running_flag: threading.Event = running_event
        self.agent: BaseTrainingEnvironment = agent

    def run(self):
        running = self.running_flag
        root, interface = build_interface(self.agent)
        root.title('Training Environment')

        closing_thread = InterfaceClosingThread(root, running, interface)
        closing_thread.start()

        try:
            root.mainloop()
            root.quit()
        except RuntimeError:
            print('Exception RuntimeError found')
            # from traceback import print_exc
            # print_exc()
        while running.is_set():  # This thread needs to be alive
            sleep(0.1)  # in order to keep the game from crashing


class InterfaceClosingThread(threading.Thread):
    def __init__(self, root, running_event, interface):
        super().__init__(daemon=True)
        self.running_flag: threading.Event = running_event
        self.interface: InterfaceVariables = interface
        self.root: tkinter.Tk = root

    def run(self):
        running = self.running_flag
        interface = self.interface
        root = self.root

        while running.is_set():
            sleep(0.02)
        interface.thread.stop()
        root.event_generate('<<close>>')

