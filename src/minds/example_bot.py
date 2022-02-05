from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.remove.ball_prediction_analysis import find_slice_at_time
from util.remove.drive import steer_toward_target
from util.remove.vec import Vec3


def example_controller(agent, packet: GameTickPacket) -> SimpleControllerState:
    my_car = packet.game_cars[agent.index]
    car_location = Vec3(my_car.physics.location)
    car_velocity = Vec3(my_car.physics.velocity)
    ball_location = Vec3(packet.game_ball.physics.location)

    # By default we will chase the ball, but target_location can be changed later
    target_location = ball_location

    if car_location.dist(ball_location) > 1000:
        # We're far away from the ball, let's try to lead it a little bit
        ball_prediction = agent.get_ball_prediction_struct()  # This can predict bounces, etc
        ball_in_future = find_slice_at_time(ball_prediction, packet.game_info.seconds_elapsed + 2)

        # ball_in_future might be None if we don't have an adequate ball prediction right now, like during
        # replays, so check it to avoid errors.
        if ball_in_future is not None:
            target_location = Vec3(ball_in_future.physics.location)
            agent.renderer.draw_line_3d(ball_location, target_location, agent.renderer.cyan())

    controls = SimpleControllerState()
    controls.steer = steer_toward_target(my_car, target_location)
    controls.throttle = 1.0
    # You can set more controls if you want, like controls.boost.

    return controls