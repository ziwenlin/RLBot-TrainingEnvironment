import threading

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from exercise.training_base import BaseTrainingManager
from snapshot.snapshot_structs import generate_game_state
from snapshot.snapshot_base import Snapshot


class BaseTrainingAgent:
    game_state: GameState = generate_game_state()
    game_packet: GameTickPacket
    game_items: dict = {}

    snapshot: Snapshot = Snapshot()
    """Contains the game state information which can be parsed to a dictionary
    From the dictionary the data can be stored in a json file
    """
    snapshot_load_flag: bool = False
    """Flag to load snapshot data to the game state. It is used in the interface
    when the user wants to load a snapshot while fetching is frozen.
    """
    snapshot_override_flag: bool = False
    """If set the snapshot will override the current game state.
    Otherwise the current game state will override the snapshot.
    """
    snapshot_live_flag: bool = False
    """When set the snapshot is always overriding the current game state
    This makes it possible to see changes from the interface live in the game.
    """

    agent_is_reloadable: bool = False
    """Enables/disable hot reloading. Often when programming you don't want
    to reload the agent when saving the files. For example while training
    machine learning. This prevents hot reloading when it is not set.
    """
    agent_is_example_mode: bool = True
    """When the actions of the desired agent should be used or the actions should
    be replaced with those actions from a dummy or an example bot.
    """
    agent_is_driving: bool = True
    """Enable/disable the movement of the agent. This will make the agent to do
    nothing. Useful if it is desired to stop the agent from performing actions.
    """
    agent_controller = SimpleControllerState()
    """The ControllerState of the agent. This will give the final output to the 
    game if agent_is_example_mode is set. If agent_is_example_mode is not set agent_controller
    will not be used for the final output.
    """

    lifetime: int = 0
    """Amount of ticks the bot is alive. Keeps track of it in the entire runtime.
    """
    training: BaseTrainingManager = BaseTrainingManager()
    """Base of the training. It contains information about how the agent is doing
    in the current episode or performance in the current exercise
    """
    interface_thread: threading.Thread = None
    """Object used to create the interface.
    """
    interface_running = threading.Event()
    """Object used to stop the interface.
    """

    def __init__(self):
        self.index: int = 0

    def restore_agent(self):
        self.agent_is_driving = True


