import tkinter as tk
from typing import Dict

from gui.gui_base import InterfaceVariables, PhysicVariables, ControlVariables
from util.relative_physics import RelativePhysics


def spinbox_cluster_DIP(spinbox_cluster: Dict[str, Dict[str, tk.StringVar]]):
    """IDK what this is gonna do yet
    tkinter variables of spinbox binding to data of something but
    with a buffer inbetween
    """

    spinbox_buffer: Dict[str, Dict[str, float]] = {group: {name: 0 for name in items.keys()}
                                                   for group, items in spinbox_cluster.items()}

    task_list = []
    for vector_name, spinbox_group in spinbox_cluster.items():
        for axis, spinbox_var in spinbox_group.items():
            bind = task(interface, spinbox_var, selected, vector_name, axis)
            task_list.append(bind)

    def spinbox_update():
        if interface.selector.get(selected) is None:  # If no item is selected yet
            return
        data = interface.selector.get(selected).data
        spinbox_var.set(f'{data[vector][axis]:.2f}')

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


def spinbox_bindings(interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables, identifier: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables and back"""
    function_list = build_spinbox_task_list(
        build_spinbox_physics_binding, interface, spinbox_collection_vars, identifier)

    def loop():
        for binder in function_list:
            binder()

    interface.thread.add_task(loop, 10, 'SpinboxBinder')


def spinbox_updater(interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables, identifier: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables"""
    updater_list = build_spinbox_task_list(
        build_spinbox_physics_updater, interface, spinbox_collection_vars, identifier)

    def loop():
        for updater in updater_list:
            updater()

    interface.selector_updater[identifier] = loop


def build_spinbox_task_list(task, interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                            selected: str):
    task_list = []
    for vector, spinbox_group_vars in spinbox_collection_vars.items():
        for axis, spinbox_var in spinbox_group_vars.items():
            bind = task(interface, spinbox_var, selected, vector, axis)
            task_list.append(bind)
    return task_list


def build_spinbox_physics_updater(interface: InterfaceVariables, spinbox_var: tk.StringVar, selected: str, vector: str,
                                  axis: str):
    """Creates a compiled function for updating the physic value to the spinbox_variable."""

    def spinbox_update():
        if interface.selector.get(selected) is None:  # If no item is selected yet
            return
        data = interface.selector.get(selected).data
        spinbox_var.set(f'{data[vector][axis]:.2f}')

    return spinbox_update


def build_spinbox_physics_binding(interface: InterfaceVariables, spinbox_var: tk.StringVar, selected: str, vector: str,
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


def spinbox_bindings_relative(root: tk.Tk, interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                              id1, id2, id3: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables and back"""

    function_list = build_spinbox_task_list(build_spinbox_physics_binding, interface, spinbox_collection_vars, id3)

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

    interface.thread.add_task(loop, 10, 'SpinboxRelative')


def spinbox_updater_relative(interface: InterfaceVariables, spinbox_collection_vars: PhysicVariables,
                             id1, id2, id3: str):
    """Takes the physics of an item and bind the physic variables to the spinbox_variables"""

    def check():
        selector_1 = interface.selector.get(id1)
        selector_2 = interface.selector.get(id2)
        selector_3 = interface.selector.get(id3)
        if selector_1 is None:  # If no item is selected yet
            return 0
        if selector_2 is None:  # If no item is selected yet
            return 0
        if selector_3 is None:  # If no item is selected yet
            return 1
        if selector_3.origin == selector_1 and selector_3.target == selector_2:
            return 2
        else:
            return 3

    def process(id):
        if id == 0:  # If no item is selected yet
            interface.selector[id3] = None
        elif id == 1:  # If no item is selected yet
            interface.selector[id3] = RelativePhysics(interface.selector[id1], interface.selector[id2])
        elif id == 2:
            interface.selector[id3].calculate()
        elif id == 3:
            interface.selector[id3].refresh(interface.selector.get(id1), interface.selector.get(id2))

    updater_list = build_spinbox_task_list(build_spinbox_physics_updater, interface, spinbox_collection_vars, id3)

    def loop():
        result = check()
        process(result)
        for updater in updater_list:
            updater()

    interface.selector_updater[id3] = loop
