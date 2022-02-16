from snapshot.snapshot_base import SnapshotPhysics, PhysicsData
from util.agent_base import BaseTrainingAgent
from gui.gui_base import InterfaceVariables, PhysicVariables
from snapshot.snapshot_structs import convert_snapshot_to_game_state, StructSnapshot
from util.bin.relative_physics import calculate_relative, calculate_back


def game_state_error_correction(agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    """Check if any sudden changes occurs in the game or gui and corrects those errors"""
    # if agent.game_packet.num_cars <= data_vars.select_car.get():
    #     data_vars.select_car.set(0)


# TODO why is this less glitchy and what does it do, I forgot...?
def game_state_render_snapshot(agent: BaseTrainingAgent, data_vars):
    """Calls the render function to show the positions live in game
    This is less glitch-y than the other function"""


def game_state_fetch_snapshot(agent: BaseTrainingAgent, interface: InterfaceVariables):
    """Fetching game state from the agent to a snapshot. The current game state will be the snapshot."""
    # game_state: StructSnapshot.game_state = convert_game_state_to_snapshot(agent.game_state)
    agent.snapshot.update(agent.game_state)  # Save the taken snapshot
    agent.snapshot.update_items(agent.game_items)
    interface.game_info['Debug a'].set(f'{agent.agent_controller.steer * 50 + 50: .2f}')
    interface.game_info['Debug b'].set(f'{agent.agent_controller.throttle * 50 + 50: .2f}')
    interface.update()


def game_state_push_snapshot(agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    """Pushing snapshot so that the game state is overridden.
     The base agent manager will setup the cars and ball into their positions."""
    agent.snapshot_override_flag = True
    agent.game_state = convert_snapshot_to_game_state(agent.snapshot.data)
    agent.game_items = agent.snapshot.items.copy()


@DeprecationWarning
def game_state_update_snapshot(agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    """Reading ui and set the values in the snapshot
    Works only when the fetching process is NOT running"""
    game_state = agent.snapshot
    # Reading the physics panel of the ball
    _update_snapshot_physics_vars(game_state.ball.physics, data_vars.ball_vars)

    # car = game_state.cars[data_vars.select_car.get()]
    # Reading the physics panel of the car
    if data_vars.selected_item:
        _update_snapshot_physics_vars(data_vars.selected_item, data_vars.selected_item_vars)

    if data_vars.selected_relative and data_vars.selected_item:
        _update_snapshot_relative_vars(data_vars.selected_item, data_vars.selected_item_vars,
                                       data_vars.selected_relative, data_vars.selected_relative_vars)

    # car.data[StructCar.boost] = data_vars.car_data[StructCar.boost].get()
    # car.data[StructCar.jumped] = data_vars.car_data[StructCar.jumped].get()


@DeprecationWarning
def game_state_update_ui(agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    """Setting the UI to the current known snapshot"""

    if agent:
        game_state = agent.snapshot
        ball = game_state.ball  # Takes the ball Physics
        # Update the ui with the data of the snapshot
        _update_ui_physics_vars(ball, data_vars.ball_vars)

    # Update the ui with the data of the snapshot
    if data_vars.selected_item:
        _update_ui_physics_vars(data_vars.selected_item, data_vars.selected_item_vars)

    if data_vars.selected_relative and data_vars.selected_item:
        _update_ui_relative_vars(data_vars.selected_item, data_vars.selected_item_vars, data_vars.selected_relative,
                                 data_vars.selected_relative_vars)

    # TODO Temporarily disabled till it is supported
    # Take the cars dictionary from the game_state
    # car_data = game_state.cars[data_vars.select_car.get()]
    # car = data_vars.select_item

    # Push the values of the snapshot to the UI
    # data_vars.car_data[StructCar.boost].set(float(car_data[StructCar.boost]))
    # data_vars.car_data[StructCar.jumped].set(int(car_data[StructCar.jumped]))
    # data_vars.car_data[StructCar.double_jumped].set(int(car_data[StructCar.double_jumped]))


@DeprecationWarning
def _update_snapshot_relative_vars(physics, physic_vars: PhysicVariables, relative: SnapshotPhysics,
                                   relative_vars: PhysicVariables):
    """Key: Location, Velocity, Rotation, Angular Velocity. Vector is a xyz object in the physics object"""
    o = SnapshotPhysics(StructSnapshot.physics())
    for vector, vec3 in relative_vars.items():
        # Dimension/axis is x, y, z. Value is a float number
        for axis, value in vec3.items():
            item = value.get()
            if not item:
                item = 0
            try:
                o.get(vector).set(axis, float(item))
            except (ValueError, AttributeError):
                continue
    c = calculate_back(physics, o)
    relative.update(c)


@DeprecationWarning
def _update_ui_relative_vars(physics: SnapshotPhysics, physic_vars: PhysicVariables, relative: SnapshotPhysics,
                             relative_vars: PhysicVariables):
    """Key: Location, Velocity, Rotation, Angular Velocity. Vector is a xyz object in the physics object"""
    o = calculate_relative(physics, relative)
    for key, vector in o.data.items():
        # Dimension/axis is x, y, z. Value is a float number
        for dimension, value in vector.items():
            # Push the values of the snapshot to the UI
            relative_vars[key][dimension].set(f'{(value):.2f}')


@DeprecationWarning
def _update_snapshot_physics_vars(physics, physic_vars: PhysicVariables):
    """Key: Location, Velocity, Rotation, Angular Velocity. Vector is a xyz object in the physics object"""
    for vector, vec3 in physic_vars.items():
        # Dimension/axis is x, y, z. Value is a float number
        for axis, value in vec3.items():
            item = value.get()
            if not item:
                item = 0
            try:
                # Some times users make errors when typing
                # Catching the error prevents crashing the loop
                physics.get(vector).set(axis, float(item))
            except (ValueError, AttributeError):
                continue


@DeprecationWarning
def _update_ui_physics_vars(physics, physic_vars: PhysicVariables):
    """Key: Location, Velocity, Rotation, Angular Velocity. Vector is a xyz object in the physics object"""
    for key, vector in physics.data.items():
        # Dimension/axis is x, y, z. Value is a float number
        for dimension, value in vector.items():
            # Push the values of the snapshot to the UI
            physic_vars[key][dimension].set(f'{value:.2f}')
