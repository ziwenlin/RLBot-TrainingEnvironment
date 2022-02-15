import tkinter as tk
from typing import Dict, Union, Callable

from snapshot.snapshot_base import SnapshotPhysics
from util.agent_base import BaseTrainingAgent
from util.bin.relative_physics import RelativePhysics
from util.thread_base import BaseThreadManager

PhysicVariables = Dict[str, Dict[str, tk.StringVar]]
CarDataVariables = Dict[str, Union[tk.DoubleVar, tk.IntVar]]
GameInfoVariables = Dict[str, Union[tk.IntVar, tk.DoubleVar, tk.StringVar]]

SelectorVariables = Dict[str, PhysicVariables]
SelectorData = Dict[str, Union[SnapshotPhysics, RelativePhysics]]
SelectorUpdater = Dict[str, Callable]


class InterfaceVariables:
    car_data: CarDataVariables = {}
    game_info: GameInfoVariables = {}

    selector: SelectorData = {}
    selector_vars: SelectorVariables = {}
    selector_updater: SelectorUpdater = {}

    agent: BaseTrainingAgent = None
    thread = BaseThreadManager()

    def update(self):
        for updater in self.selector_updater.values():
            updater()

    def info(self, name: str):
        return self.game_info[name].get() == 1


class ControlVariables:
    psyonix_bot = 'Psyonix bot'
    hot_reload = 'Hot Reload'
    freeze = 'Freeze'
    live = 'Live'
    preview = 'Preview'
    change_game = 'Change Game'
    pause = 'Pause'
    end_match = 'End Match'

    gravity = 'Gravity'
    speed = 'Speed'
    debug = 'Debug'


CONTROL_CHECKBOXES = [
    ControlVariables.hot_reload, ControlVariables.psyonix_bot, ControlVariables.freeze, ControlVariables.live,
    ControlVariables.preview,
    ControlVariables.change_game,
    ControlVariables.pause, ControlVariables.end_match
]

CONTROL_SLIDERS = [ControlVariables.gravity, ControlVariables.speed]

PHYSICS_PANEL_PRIMARY = 1
PHYSICS_PANEL_SECONDARY = 2
PHYSICS_PANEL_SECONDARY_RELATIVE = 3