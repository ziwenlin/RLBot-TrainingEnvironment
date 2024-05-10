import tkinter as tk

from rlbot.utils.game_state_util import GameState
from rlbot.utils.structures.game_data_struct import PlayerInfo, GameTickPacket, Physics

from gui.gui_base import InterfaceVariables, ControlVariables
from gui.gui_panels import panel_training, panel_primairy_selector, panel_main_overview, panel_controls, \
    panel_secondary_selector
from util.agent_base import BaseTrainingEnvironment
from gui.gui_snapshot import game_state_error_correction, game_state_render_snapshot, \
    game_state_update_snapshot, game_state_update_ui, game_state_push_snapshot, game_state_fetch_snapshot


def build_interface_base(agent: BaseTrainingEnvironment):
    top = tk.Tk()
    interface = InterfaceVariables()
    interface.agent = agent
    agent.snapshot.update(agent.game_state)
    panel_main_overview(top, agent, interface)
    panel_primairy_selector(top, agent, interface)
    # panel_secondary_selector(top, agent, interface)
    panel_controls(top, agent, interface)
    panel_training(top, agent, interface)

    top.data = interface
    return top, interface


def build_interface(agent: BaseTrainingEnvironment):
    top, interface = build_interface_base(agent)

    loop_snapshot = build_task_snapshot_loop(top, agent, interface)
    loop_check = build_task_check(top, agent, interface)

    interface.thread.add_task(loop_snapshot, 60, 'InterfaceLoop')
    interface.thread.add_task(loop_check, 3, 'InterfaceChecker')
    interface.thread.start()

    def close(event=None):
        interface.thread.stop()
        print("Reload/closing")
        top.after(100, top.destroy)

    top.wm_protocol('WM_DELETE_WINDOW', close)
    top.event_add('<<close>>', 'WM_DELETE_WINDOW')
    top.bind('<<close>>', close)
    # top.after(2000, lambda: top.event_generate('<<close>>'))
    return top, interface


def build_task_snapshot_loop(root, agent: BaseTrainingEnvironment, interface: InterfaceVariables):
    def loop_snapshot():
        # Tkinter main loop. Check for errors and correct them at the start
        game_state_error_correction(agent, interface)

        is_frozen = interface.info(ControlVariables.freeze)
        is_live = interface.info(ControlVariables.live)
        is_preview = interface.info(ControlVariables.preview)
        is_loading = agent.snapshot_load_flag

        if not is_frozen and not is_live and not is_preview and not is_loading:
            game_state_fetch_snapshot(agent, interface)
            # game_state_update_snapshot(agent, interface)
            agent.snapshot_live_flag = False
        elif is_loading:
            if not is_frozen:  # When not frozen the load button can override the game state
                game_state_push_snapshot(agent, interface)
            agent.snapshot_load_flag = False
            interface.update()
        # elif is_frozen:
        # game_state_update_snapshot(agent, interface)
        # interface.update()
        elif is_live:
            agent.snapshot_live_flag = True
            # game_state_update_snapshot(agent, interface)
            game_state_push_snapshot(agent, interface)
            interface.update()
        elif is_preview:
            game_state_render_snapshot(agent, interface)
            interface.update()

    return loop_snapshot


def build_task_check(root, agent: BaseTrainingEnvironment, interface: InterfaceVariables):
    def loop_check():
        # Because I did not want to reload the agent every time a change happened
        # Hot reload can be controlled when needed
        hot_reload = interface.game_info[ControlVariables.hot_reload].get() == 1
        bot_example = interface.game_info[ControlVariables.psyonix_bot].get() == 0

        agent.agent_is_reloadable = hot_reload
        agent.agent_is_driving_example = bot_example

        if hot_reload:
            interface.thread.stop()

    return loop_check


def build_task_standalone(agent: BaseTrainingEnvironment, interface: InterfaceVariables):
    def move(physics: Physics, multiplier=1):
        physics.location.y += multiplier
        if physics.location.y > 5000:
            physics.location.y = -5000
            physics.location.x +=multiplier
        if physics.location.x > 3000:
            physics.location.x = -3000
    def loop():
        ball = agent.game_packet.game_ball.physics
        car = agent.game_packet.game_cars[0].physics
        move(ball)
        move(car, 10)
        agent.game_state = GameState.create_from_gametickpacket(agent.game_packet)

    return loop


def build_interface_standalone(agent: BaseTrainingEnvironment):
    # Filling the missing data when running the program without Rocket League
    agent.game_state.ball.physics.location.y = 1000
    agent.snapshot.update(agent.game_state)
    agent.game_packet = GameTickPacket()
    agent.game_packet.num_cars = 5
    agent.game_packet.game_cars[0] = PlayerInfo(team=0)
    top, interface = build_interface(agent)

    loop_development = build_task_standalone(agent, interface)
    interface.thread.add_task(loop_development, 100, 'MovingObjects')
    # Plan to make a load panel for loading training packs or stored snapshots
    # data_vars = top.data_vars
    # panel_load(top, data_vars)
    return top
