import threading
from time import sleep
from typing import List

from util.agent_base import BaseTrainingEnvironment
from util.thread_base import BaseThreadManager
from util.thread_interface import InterfaceMainThread


class ThreadManagerAgent(BaseThreadManager):
    def __init__(self, agent, *args):
        super().__init__(*args)
        runner_event = self.running_event
        self.add_thread(InterfaceMainThread(agent, runner_event))


class DQNManagerThread(threading.Thread):
    def __init__(self, running_flag, agent, index):
        super().__init__(daemon=True)
        self.running_flag: threading.Event = running_flag
        self.agent: BaseTrainingEnvironment = agent
        self.index = index

    def run(self):
        if not self.agent.neural_trainer:
            return
        running = self.running_flag
        trainer = self.agent.neural_trainer
        agent = [a for a in trainer.agents.values()][self.index]
        try:
            while not running.is_set():
                sleep(0.1)
                if not self.agent.training.is_running: continue
                sleep(1)
                terminal_state = self.agent.training.episode_index % 10 == 0
                step = trainer.step
                agent.train(terminal_state, step, self.index)
        except RuntimeError:
            print('Exception RuntimeError found')
            print('Neural training thread %s ended' % self.index)

# def start_trainer(agent):
#     trainers = []
#     for index in range(len(agent.neural_trainer.agents)):
#         trainer = DQNManagerThread(agent, index)
#         trainer.start()
#         trainers.append(trainer)
#     return trainers
#
# def start_interface(agent):
#     # print('Starting interface') # Debuggin info
#     interface = InterfaceThread(agent)
#     interface.start()
#     # print('Active threads:', threading.active_count()) # Debugging info
#     return interface
#
#
# def stop_interface(agent):
#     # print('Stopping interface') # Debuggin info
#     agent.interface_running.set()
#     # print('Active threads:', threading.active_count()) # Debugging info
