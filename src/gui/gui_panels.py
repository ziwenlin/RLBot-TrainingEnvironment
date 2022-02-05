import tkinter as tk

from gui.building_blocks import make_check_button, make_slider, make_button, make_base_frame, make_spacer, \
    make_labeled_entry, make_spaced_label
from gui.building_spinbox import make_panel_physics, make_spinbox_bindings, make_spinbox_updater, \
    make_relative_spinbox_updater, make_relative_spinbox_bindings
from gui.display_panel import panel_display
from gui.gui_base import InterfaceVariables, CONTROL_CHECKBOXES, CONTROL_SLIDERS, ControlVariables, \
    PHYSICS_PANEL_PRIMARY, PHYSICS_PANEL_SECONDARY, PHYSICS_PANEL_SECONDARY_RELATIVE
from gui.building_combobox import make_combobox
from gui.gamestate_functions import game_state_fetch_snapshot, game_state_push_snapshot
from snapshot.file_functions import save_snapshot, load_snapshot
from util.agent_base import BaseTrainingAgent
from util.bin.relative_physics import RelativePhysics


def panel_main_overview(base, agent: BaseTrainingAgent, interface: InterfaceVariables):
    """Left panel
    It contains a canvas for the field overlay/overview
    And it has the editable fields for ball physics"""
    frame = make_base_frame(base)
    panel_display(frame, agent, interface)

    label = tk.Label(frame, text='Ball')
    label.pack()
    interface.selector_vars['Ball'] = make_panel_physics(frame, side=tk.LEFT)
    interface.selector['Ball'] = agent.snapshot.ball.physics
    make_spinbox_bindings(frame, interface, interface.selector_vars['Ball'], 'Ball')
    make_spinbox_updater(interface, interface.selector_vars['Ball'], 'Ball')


def panel_primairy_selector(base, agent: BaseTrainingAgent, interface: InterfaceVariables):
    """Mid panel
    Selecting item based on normal physics"""
    frame = make_base_frame(base)
    identifier = PHYSICS_PANEL_PRIMARY
    make_combobox(frame, agent, interface, identifier)
    interface.selector_vars[identifier] = make_panel_physics(frame, side=tk.TOP)
    make_spinbox_bindings(frame, interface, interface.selector_vars[identifier], identifier)
    make_spinbox_updater(interface, interface.selector_vars[identifier], identifier)

    make_spacer(frame, 10)
    make_slider(frame, interface.car_data, 'Boost')

    # TODO setting jumped and doubble jumped is not supported by RLbot
    # make_spacer(frame, 10)
    # for check_name in ['Jumped', 'Double Jumped']:
    #     make_check_button(frame, data_vars.car_data, check_name)


def panel_secondary_selector(base, agent: BaseTrainingAgent, interface: InterfaceVariables):
    """Mid panel
    Selecting item based on relative physics"""
    frame = make_base_frame(base)
    identifier = PHYSICS_PANEL_SECONDARY
    identifier_relative = PHYSICS_PANEL_SECONDARY_RELATIVE
    make_combobox(frame, agent, interface, identifier)
    interface.selector_vars[identifier] = make_panel_physics(frame, side=tk.TOP)
    make_relative_spinbox_bindings(frame, interface, interface.selector_vars[identifier],
                                  PHYSICS_PANEL_PRIMARY, identifier, identifier_relative)
    make_relative_spinbox_updater(interface, interface.selector_vars[identifier],
                                  PHYSICS_PANEL_PRIMARY, identifier, identifier_relative)


def panel_controls(base, agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    """Right panel"""
    frame = make_base_frame(base)
    make_spaced_label(frame, 'Control panel')

    for check_name in CONTROL_CHECKBOXES:
        make_check_button(frame, data_vars.game_info, check_name)

    for slider_name in CONTROL_SLIDERS:
        make_spacer(frame, 10)
        make_slider(frame, data_vars.game_info, slider_name)

    # TODO make a building base for debugging in tkinter
    make_spacer(frame, 10)
    data_vars.game_info[ControlVariables.debug] = debug_text = tk.StringVar(frame, value='Nothing yet')
    debug_label = tk.Label(frame, textvariable=debug_text, anchor='w', padx=5)
    debug_label.pack(fill=tk.BOTH)


def panel_training(base, agent: BaseTrainingAgent, data_vars: InterfaceVariables):
    frame = make_base_frame(base)

    def next_exercise():
        agent.training.exercise_next = True

    def save_command():
        name = snapshot_entry.get()
        save_snapshot(name, agent)

    def load_command():
        name = snapshot_entry.get()
        load_snapshot(name, agent)

    def start_training():
        agent.training.start_training(training_entry)

    snapshot_entry = make_labeled_entry(frame, 'Snapshot name')
    make_button(frame, save_command, 'Save')
    make_button(frame, load_command, 'Load')

    c = lambda: game_state_fetch_snapshot(agent, data_vars)
    make_button(frame, c, "New snapshot")
    c = lambda: game_state_push_snapshot(agent, data_vars)
    make_button(frame, c, "Set snapshot")

    # make_spacer(frame, 10)
    training_entry = make_labeled_entry(frame, 'Training pack')

    make_button(frame, start_training, 'Start training')
    make_button(frame, agent.training.stop_training, 'Stop training')
    make_button(frame, agent.training.resume_training, 'Resume training')
    make_button(frame, next_exercise, 'Next exercise')


def panel_load(base, data_vars):
    # TODO load configuration panel
    window = tk.Toplevel(base)
    left_frame = tk.Frame(window)
    left_frame.pack(side=tk.LEFT)
    mid_frame = tk.Frame(window)
    mid_frame.pack(side=tk.LEFT)
    right_frame = tk.Frame(window)
    right_frame.pack(side=tk.LEFT)

    listbox = tk.Listbox(left_frame)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar = tk.Scrollbar(left_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    data_frame = tk.Frame(mid_frame)
    data_frame.pack()


