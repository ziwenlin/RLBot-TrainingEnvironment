import threading

from gui.gui_builder import build_interface
from util.agent_base import BaseTrainingAgent


class InterfaceThread(threading.Thread):
    def __init__(self, agent):
        super().__init__(daemon=True)
        self.agent: BaseTrainingAgent = agent

    def run(self):
        root = build_interface(self.agent)
        running = self.agent.interface_running

        def close_event():
            if running.is_set():
                root.destroy()
            else:
                root.after(10, close_event)

        try:
            # root.after(1000, root.focus_force)
            close_event()
            root.mainloop()
            root.quit()
        except RuntimeError:
            print('Exception RuntimeError found')
            # print_exc()
        # running.set()
        import time
        while running.is_set():
            time.sleep(0.01)


class DQNManagerThread(threading.Thread):
    def __init__(self, agent, index):
        super().__init__(daemon=True)
        self.agent: BaseTrainingAgent = agent
        self.index = index

    def run(self):
        if not self.agent.neural_trainer:
            return
        running = self.agent.interface_running
        trainer = self.agent.neural_trainer
        agent = [a for a in trainer.agents.values()][self.index]
        import time
        try:
            while not running.is_set():
                time.sleep(0.1)
                if not self.agent.training.is_running: continue
                time.sleep(1)
                terminal_state = self.agent.training.episode_index % 10 == 0
                step = trainer.step
                agent.train(terminal_state, step, self.index)
        except RuntimeError:
            print('Exception RuntimeError found')
            print('Neural training thread %s ended' % self.index)


def start_trainer(agent):
    trainers = []
    for index in range(len(agent.neural_trainer.agents)):
        trainer = DQNManagerThread(agent, index)
        trainer.start()
        trainers.append(trainer)
    return trainers


def start_interface(agent):
    # print('Starting interface') # Debuggin info
    interface = InterfaceThread(agent)
    interface.start()
    # print('Active threads:', threading.active_count()) # Debugging info
    return interface


def stop_interface(agent):
    # print('Stopping interface') # Debuggin info
    agent.interface_running.set()
    # print('Active threads:', threading.active_count()) # Debugging info