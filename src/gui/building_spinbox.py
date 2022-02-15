import tkinter as tk
from typing import Dict, List

from gui.building_blocks import make_spaced_label, _make_scrolling_event
from gui.gui_base import InterfaceVariables, PhysicVariables, ControlVariables
from snapshot.snapshot_base import Snapshot
from util.bin.relative_physics import RelativePhysics


def make_panel_physics(root, side=tk.TOP) -> Dict[str, Dict[str, tk.StringVar]]:
    """Makes a panel where the location, velocity, rotation, and angular velocity
    can be seen and adjusted. It returns a dictionary of a dictionary of tkinter
    StringVars. Those StringVars must be filled with valid number values inside strings. """
    frame = tk.Frame(root)
    frame.pack()
    spinbox_collection_vars = make_named_spinbox_collection(
        frame, ['Location', 'Velocity', 'Rotation', 'Angular Velocity'], ['x', 'y', 'z'], side)
    return spinbox_collection_vars


def make_named_spinbox_collection(root, group_list: List[str], name_list: List[str], side=tk.TOP):
    """Creates a group of groups of spinboxes. Does nothing more special"""
    spinbox_collection_vars = {}
    for collection in group_list:
        spinbox_collection_vars[collection] = make_named_spinbox_group(root, collection, name_list, side)
    return spinbox_collection_vars


def make_named_spinbox_group(root, group_name: str, name_list: List[str], side=tk.TOP):
    """Creates a group of special spinboxes.
    The group name identifies what the group stands for."""
    spinbox_group_vars = {}
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=1, side=side)
    make_spaced_label(frame, group_name)
    for name in name_list:
        spinbox_var = make_named_spinbox(frame, name)
        spinbox_group_vars[name] = spinbox_var
    return spinbox_group_vars


def make_named_spinbox(root, name: str):
    """Creates a spinbox with an explaining text to the left.
    This spinbox is scrollable so that the values are easily changed."""
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=1)
    label = tk.Label(frame, text=name)
    label.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    spinbox_var = tk.StringVar(frame, value='0.00')
    spinbox = tk.Spinbox(frame, textvariable=spinbox_var, from_=-10000, to=10000, increment=0.05)
    spinbox.bind('<MouseWheel>', _make_scrolling_event(spinbox_var, 5))
    spinbox.pack(side=tk.RIGHT)
    return spinbox_var


def _function_list_spinbox(function, interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                           selected: str):
    function_list = []
    for vector, spinbox_group_vars in spinbox_collection_vars.items():
        for axis, spinbox_var in spinbox_group_vars.items():
            bind = function(interface, spinbox_var, selected, vector, axis)
            function_list.append(bind)
    return function_list


def make_spinbox_bindings(root: tk.Tk, interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                          selected: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables and back"""
    function_list = _function_list_spinbox(_physics_spinbox_binding, interface, spinbox_collection_vars, selected)

    def loop():
        for binder in function_list:
            binder()

    interface.thread.add_task(loop)


def make_spinbox_updater(interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                         selected: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables"""
    updater_list = _function_list_spinbox(_physics_spinbox_updater, interface, spinbox_collection_vars, selected)

    def loop():
        for updater in updater_list:
            updater()

    interface.selector_updater[selected] = loop


def _physics_spinbox_updater(interface: InterfaceVariables, spinbox_var: tk.StringVar, selected: str, vector: str,
                             axis: str):
    """Creates a compiled function for updating the physic value to the spinbox_variable."""

    def spinbox_update():
        if interface.selector.get(selected) is None:  # If no item is selected yet
            return
        data = interface.selector.get(selected).data
        spinbox_var.set(f'{data[vector][axis]:.2f}')

    return spinbox_update


def _physics_spinbox_binding(interface: InterfaceVariables, spinbox_var: tk.StringVar, selected: str, vector: str,
                             axis: str):
    """Creates a compiled function for binding spinbox_variable to physics values."""

    def spinbox_bind():
        if interface.selector.get(selected) is None:  # If no item is selected yet
            return
        if interface.info(ControlVariables.freeze) or interface.info(ControlVariables.live):
            item = spinbox_var.get()
            if not item:
                item = 0
            try:
                value = interface.selector.get(selected).data[vector][axis]
                item = float(item)
                if value - item > 0.1 or value - item < - 0.1:
                    interface.selector.get(selected).get(vector).set(axis, item)
            except (ValueError, AttributeError):
                pass
        if not interface.info(ControlVariables.live):
            physics = interface.selector.get(selected).data
            spinbox_var.set(f'{physics[vector][axis]:.2f}')

    return spinbox_bind


def make_relative_spinbox_bindings(root: tk.Tk, interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                                   id1, id2, id3: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables and back"""

    function_list = _function_list_spinbox(_physics_spinbox_binding, interface, spinbox_collection_vars, id3)

    def loop():
        for binder in function_list:
            binder()
        setup()

    def setup():
        if interface.selector.get(id1) is None:  # If no item is selected yet
            interface.selector[id3] = None
            return
        if interface.selector.get(id2) is None:  # If no item is selected yet
            interface.selector[id3] = None
            return
        if interface.selector.get(id3) is None:  # If no item is selected yet
            interface.selector[id3] = RelativePhysics(interface.selector[id1], interface.selector[id2])
        physics = interface.selector[id3].get_normal()
        interface.selector[id2].update(physics)

    interface.thread.add_task(loop)


def make_relative_spinbox_updater(interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                                  id1, id2, id3: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables"""

    def setup():
        if interface.selector.get(id1) is None:  # If no item is selected yet
            interface.selector[id3] = None
            return
        if interface.selector.get(id2) is None:  # If no item is selected yet
            interface.selector[id3] = None
            return
        if interface.selector.get(id3) is None:  # If no item is selected yet
            interface.selector[id3] = RelativePhysics(interface.selector[id1], interface.selector[id2])
        elif interface.selector[id3].origin == interface.selector[id1] and \
                interface.selector[id3].target == interface.selector[id2]:
            interface.selector[id3].calculate()
        else:
            interface.selector[id3].refresh(interface.selector.get(id1), interface.selector.get(id2))

    updater_list = _function_list_spinbox(_physics_spinbox_updater, interface, spinbox_collection_vars, id3)

    def loop():
        setup()
        for updater in updater_list:
            updater()

    interface.selector_updater[id3] = loop
