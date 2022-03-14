import tkinter as tk
from typing import Dict, List


def make_check_button(root, name, data_vars: dict=None):
    check_var = tk.IntVar(root, value=0)
    check_button = tk.Checkbutton(root, text=name, variable=check_var)
    check_button.pack(anchor='w')
    if data_vars is not None:
        data_vars[name] = check_var
    return check_var


def make_slider(root, name, data_vars: dict=None):
    make_spaced_label(root, name)
    scale_var = tk.StringVar(root, value=0)
    scale = tk.Scale(root, variable=scale_var, orient=tk.HORIZONTAL)
    scale.bind('<MouseWheel>', build_scrolling_event(scale_var, -1))
    scale.pack(fill=tk.BOTH)
    if data_vars is not None:
        data_vars[name] = scale_var
    return scale_var


def make_label(root, text):
    label = tk.Label(root, text=text, anchor='sw', padx=5, height=1)
    label.pack(fill=tk.BOTH)


def make_spaced_label(root, text):
    make_spacer(root, 5)
    make_label(root, text)


def make_labeled_entry(root, name):
    make_spaced_label(root, name)
    entry = tk.Entry(root)
    entry.pack(fill=tk.BOTH)
    return entry


def make_spacer(root, size):
    spacer = tk.Frame(root, height=size)
    spacer.pack()


def make_button(root, text, command):
    button = tk.Button(root, text=text, command=command, height=2, anchor='w', padx=8)
    button.pack(fill=tk.BOTH)


def make_base_frame(root):
    frame = tk.Frame(root, width=1600)
    frame.pack(
        expand=True,
        fill=tk.BOTH,
        side=tk.LEFT
    )
    return frame


def build_scrolling_event(string_var: tk.StringVar, multiplier=1):
    def scrolling(event):
        value = string_var.get()
        try:
            value = float(value) + multiplier * (event.delta / 120)
            string_var.set(f'{value:.2f}')
        except:
            pass

    return scrolling


def make_named_spinbox(root, name: str):
    """Creates a spinbox with an explaining text to the left.
    This spinbox is scrollable so that the values are easily changed."""
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=1)
    label = tk.Label(frame, text=name)
    label.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    spinbox_var = tk.StringVar(frame, value='0.00')
    spinbox = tk.Spinbox(frame, textvariable=spinbox_var, from_=-10000, to=10000, increment=0.05)
    spinbox.bind('<MouseWheel>', build_scrolling_event(spinbox_var, 5))
    spinbox.pack(side=tk.RIGHT)
    return spinbox_var


def make_named_spinbox_cluster(root, structure: Dict[str, List[str]], side=tk.TOP):
    """Creates a group of groups of spinboxes. Does nothing more special"""
    frame = tk.Frame(root)
    frame.pack()
    spinbox_collection_vars = {}
    for group_name, name_list in structure.items():
        spinbox_collection_vars[group_name] = make_named_spinbox_group(root, group_name, name_list, side)
    return spinbox_collection_vars


def make_named_spinbox_collection(root, group_list: List[str], name_list: List[str], side=tk.TOP):
    """Creates a group of groups of spinboxes. Does nothing more special"""
    frame = tk.Frame(root)
    frame.pack()
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