import datetime
import tkinter.messagebox
from traceback import print_exc
from typing import List

from snapshot.file_base import _create_file_if_not_exist, __read_json, _write_json
from snapshot.file_versions import VERSIONS, get_snapshot_pre_version, get_snapshot

"""
Stored games states:
[
    {
        'name': 'name to select a specific game state using the interface',
        'date': 'date of creation',
        'tags': 'tags and stuff for search filters'
        'data': {game_state},
    },
    repeat
]
"""


def save_snapshot(name, agent):
    data = {
        'Name': name,
        'Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Tags': 'Currently not used',
        'Items': agent.snapshot.items_data.copy(),
        'Data': agent.snapshot.data.copy(),
        'Version': VERSIONS[0],
    }
    success = save_snapshot_to_file(name, data)
    if success:
        return
    answer = tkinter.messagebox.askokcancel(
        'Save already exists',
        'Do you want to overwrite existing save?'
    )
    if answer:
        overwrite_snapshot_in_file(name, data)


def load_snapshot(name, agent):
    json_snapshot = load_snapshot_from_file(name)
    agent.snapshot_load_flag = True
    if not json_snapshot:
        agent.snapshot_load_flag = False
        print(f'No snapshot found with the name: "{name}"')
        return
    if 'Version' in json_snapshot:
        data = get_snapshot(json_snapshot)
    else:
        data = get_snapshot_pre_version(json_snapshot)
    agent.snapshot.update(data['Data'])
    agent.snapshot.update_items(data['Items'])


def overwrite_snapshot_in_file(name, data):
    path = './stored_game_state.json'
    _create_file_if_not_exist(path, '[]')
    existing_data: List[dict] = __read_json(path)
    for snapshot in existing_data:
        if snapshot['Name'] == name:
            snapshot.update(data)
            break
    try:
        _write_json(path, existing_data)
    except:
        print_exc()
        return False
    return True


def save_snapshot_to_file(name, data):
    path = './stored_game_state.json'
    _create_file_if_not_exist(path, '[]')
    existing_data: List = __read_json(path)
    for snapshot in existing_data:
        if snapshot['Name'] == name:
            return False
    existing_data.append(data)
    try:
        _write_json(path, existing_data)
    except:
        print_exc()
        return False
    return True


def load_snapshot_from_file(name):
    path = './stored_game_state.json'
    _create_file_if_not_exist(path, '[]')
    existing_data: List = __read_json(path)
    for snapshot in existing_data:
        if snapshot['Name'] == name:
            return snapshot
    return None
