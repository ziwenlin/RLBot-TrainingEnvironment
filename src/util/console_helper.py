from typing import Union

NEXT_EPISODE_MAX = 50

def display_episode(data: Union[dict, str]):
    """ I did not like the way how data got printed in the console
    This function will print a table dedicated to this trainer """
    if type(data) is str:
        return print(data)
    msg = " "
    # Shows data in this specific order
    order = ['name', 'episode', 'phase', 'reward', 'score', 'penalty', 'duration',
             'accuracy', 'closest', 'distance',
    ]
    if data['episode'] % NEXT_EPISODE_MAX == 0:
        for key in order:
            if key == 'name':
                print(f'\n {"Stopped reason:": ^18}', end=' ')
                continue
            if key not in data:
                # Do not print keys which are not even present in the data
                continue
            print(f'{key.capitalize():>{len(key) + 2}}', end='  ')
        print()
    for key in order:
        if key not in data:
            # Do not print keys which are not even present in the data
            continue
        value = data[key]
        length = len(key) + 2
        if key == 'name':
            msg += f'{value:18} '
        if type(value) is int:
            msg += f'{value:{length}d}  '
        if type(value) is float:
            if value > 100 or value < -100:
                msg += f"{value: {length}.1f}  "
                continue
            # if value < 0.1 and value > -0.1:
            #     msg += f"{value: {length}.4f}  "
            #     continue
            # if value < 1 and value > -1:
            #     msg += f"{value: {length}.3f}  "
            #     continue
            msg += f"{value: {length}.2f}  "
    print(msg)