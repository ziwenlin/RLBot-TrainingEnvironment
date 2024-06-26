from gui.building_blocks import make_spaced_label
from gui.gui_base import InterfaceVariables
from util.agent_base import BaseTrainingEnvironment
import tkinter.ttk as ttk


# TODO add comments to the whole file


def make_combobox(root, agent: BaseTrainingEnvironment, interface: InterfaceVariables, selector):
    make_spaced_label(root, 'Selected item:')
    combobox = ttk.Combobox(root)
    combobox.pack()
    combobox.set('None')

    combobox_event_select = build_combobox_select_event(combobox, agent, interface, selector)
    combobox_update_values = build_combobox_values_update(combobox, agent)
    combobox_update_select_items = build_combobox_select_update(combobox, agent, interface, selector)

    def update():
        combobox_update_values()
        combobox_update_select_items()

    for bindings in ('<<ComboboxSelected>>',):
        combobox.bind(bindings, combobox_event_select)
    interface.thread.add_task(update, name='Combobox')


def build_combobox_select_update(combobox: ttk.Combobox, agent: BaseTrainingEnvironment, interface: InterfaceVariables,
                                 selector):
    def combobox_select_update():
        physics = interface.selector.get(selector)
        cars = [car.physics for car in agent.snapshot.cars.values()]
        items = agent.snapshot.items
        if agent.snapshot.ball.physics == physics:
            combobox.set('Ball')
        elif physics in cars:
            index = cars.index(physics)
            combobox.set(f'Car {index + 1}')
        elif physics in items.values():
            for name, item in items.items():
                if physics == item:
                    combobox.set(name)
        else:
            combobox.set('None')

    return combobox_select_update


def build_combobox_values_update(combobox: ttk.Combobox, agent: BaseTrainingEnvironment):
    def combobox_update_values():
        values = ['None', 'Ball']
        for i in agent.snapshot.cars:
            values += [f'Car {i + 1}']
        for i in agent.snapshot.items:
            values += [i]
        combobox['values'] = values

    return combobox_update_values


def build_combobox_select_event(combobox: ttk.Combobox, agent: BaseTrainingEnvironment, interface: InterfaceVariables,
                                selector):
    def combobox_select_item(event):
        selected_item: str = combobox.get()
        if selected_item == 'Ball':
            physics = agent.snapshot.ball.physics
        elif 'Car ' in selected_item:
            index_car = selected_item.split(' ')[-1]
            index_car = int(index_car) - 1
            physics = agent.snapshot.cars[index_car].physics
        elif selected_item in agent.snapshot.items:
            physics = agent.snapshot.items[selected_item]
        else:
            physics = None
        interface.selector[selector] = physics
        interface.update()

    return combobox_select_item
