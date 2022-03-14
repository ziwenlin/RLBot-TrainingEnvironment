from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from exercise.training_main import TrainingManager
from minds.example_bot import example_controller
from util.agent_base import BaseTrainingAgent
from util.thread_agent import ThreadManagerAgent

ALIVE_INTERVAL = (2 * 60 * 30)


class BaseTrainingEnvironmentAgent(BaseAgent, BaseTrainingAgent):
    """Base of the training environment agent. Inherit this class to get access to a
     full blown interface which can:

     * Save a snapshot of the game state
     * Load a saved game state to the game
     * Making exercises with specific parameter to pass
     * Using those exercises to train machine learning
     * Alter the game state through the interface

     Use def run_agent() to give a controller output as a SimpleControllerState. You can use
     self.agent_controller as the output or either by using return in run_agent() to give
     controller output.
     """

    def __init__(self, name, team, index):
        BaseAgent.__init__(self, name, team, index)
        BaseTrainingAgent.__init__(self)
        # self.tps_graph = Graph1D((50, 50, 300, 300))

    def update_environment(self, packet: GameTickPacket):
        if self.lifetime > 6000:
            pass  # Don't waste compute power on all if-statements
        elif self.thread_manager is not ThreadManagerAgent and self.lifetime == 60:
            """After a set time the interface get initiated. It should 
            execute at 30th tick in the game."""
            self.training = TrainingManager(self)
            self.thread_manager = ThreadManagerAgent(self)
            self.thread_manager.start()
        elif self.lifetime == 120:
            """After 4 seconds (if fps is set at 30 otherwise after 1 second) 
            This function is only for 1 time execution after start"""
            # self.training.start_training()

        if not self.snapshot_override_flag:
            # Get the game state so it is accessible for the interface
            self.game_state = GameState.create_from_gametickpacket(packet)
            self.game_packet = packet
        else:
            # Bot is setting the game state
            self.snapshot_override_flag *= self.snapshot_live_flag
            self.set_game_state(self.game_state)

        # Trainer for custom training. Does thing that needs be executed
        self.training.step_training(packet)
        self.lifetime += 1

    def update_renderer(self, packet: GameTickPacket):
        """TODO I am not using the renderer yet"""
        # self.tps_graph.new_data(self.training.tick_performance.get_tps())
        # self.tps_graph.render(self.renderer)
        # car_location = Vec3(packet.game_cars[0].physics.location)
        # self.renderer.begin_rendering()
        # self.renderer.draw_string_3d(car_location, 1, 1, f'Tick: {self.lifetime:.1f}', self.renderer.white())
        # self.renderer.end_rendering()

    def update_controller(self, packet: GameTickPacket):
        """The update controller checks whether the agent should drive,
        playing dumb or standing still"""
        if self.agent_is_driving:
            if self.agent_is_driving_example:
                # Agent should be driving and be controlled
                controls = self.run_agent(packet)
                if not controls: # Handling a possible None
                    # Error handling if run_agent() gives no output
                    # All other options always gives a controller
                    controls = self.agent_controller
            else:
                # The agent should be driving but not controlled
                # Output a basic movement to the controller
                controls = example_controller(self, packet)
        else:
            # When the agent should not be driving
            # Output no movement to the controller
            controls = SimpleControllerState()
        self.agent_controller = controls
        return controls

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """TODO add comments"""
        # To future me or other programmers:
        # Do not change the order of these 4 functions
        self.update_environment(packet)
        self.update_renderer(packet)
        self.update_controller(packet)
        return self.agent_controller

    def retire(self):
        self.training.stop_training()
        self.thread_manager.stop()

    def is_hot_reload_enabled(self):
        return self.agent_is_reloadable

    def run_agent(self, packet: GameTickPacket) -> SimpleControllerState:
        pass


"""
A decision to not program the code this way. Because it is not the right way to
do so. It is better to use super().

Override def __init__() or use def init() or def initialize() to setup variables.
Use def initialize_agent() to initialize starting variables in the field.
Use def run_agent() for code that always needs to be executed. Because the run_agent()
is not always called.

I leave this here just for not making this mistake again/

# def initialize(self):
#     # Overrideable
#     pass
#
#
# def init(self):
#     # Overrideable
#     pass
"""
