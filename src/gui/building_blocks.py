import tkinter as tk


def make_check_button(root, data_vars: dict, name):
    data_vars[name] = check_var = tk.IntVar(root, value=0)
    check_button = tk.Checkbutton(root, text=name, variable=check_var)
    check_button.pack(anchor='w')


def make_slider(root, data_vars: dict, name):
    make_spaced_label(root, name)
    data_vars[name] = scale_var = tk.StringVar(root, value=0)
    scale = tk.Scale(root, variable=scale_var, orient=tk.HORIZONTAL)
    scale.bind('<MouseWheel>', _make_scrolling_event(scale_var, -1))
    scale.pack(fill=tk.BOTH)


def make_spaced_label(root, text):
    make_spacer(root, 5)
    label = tk.Label(root, text=text, anchor='sw', padx=5, height=1)
    label.pack(fill=tk.BOTH)


def make_labeled_entry(root, name):
    make_spaced_label(root, name)
    entry = tk.Entry(root)
    entry.pack(fill=tk.BOTH)
    return entry


def make_spacer(root, size):
    spacer = tk.Frame(root, height=size)
    spacer.pack()


def make_button(root, command, text):
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


def _make_scrolling_event(string_var: tk.StringVar, multiplier=1):
    def scrolling(event):
        value = string_var.get()
        try:
            value = float(value) + multiplier * (event.delta / 120)
            string_var.set(f'{value:.2f}')
        except:
            pass

    return scrolling
