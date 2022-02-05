from snapshot.snapshot_structs import StructSnapshot, StructPhysics


def dev_0_2(json_snapshot):
    return json_snapshot


def dev_0_1(json_snapshot):
    items = {}
    for name, vector in json_snapshot['Items'].items():
        items[name] = StructSnapshot.copy_physics()
        items[name][StructPhysics.location] = vector
    json_snapshot['Items'] = items
    return json_snapshot


VERSION_FUNCTIONS = [
    # dev_0_3,
    dev_0_2,
    dev_0_1,
]

VERSIONS = [
    # 'DEV0.3',
    'DEV0.2',
    'DEV0.1',
]


def get_snapshot(json_snapshot):
    """Retrieve snapshot from loaded json save"""
    index = 0
    for version in VERSIONS:
        if json_snapshot['Version'] == version:
            break
        index += 1
    while index > 0:
        json_snapshot = VERSION_FUNCTIONS[index](json_snapshot)
        index += -1
    return json_snapshot


def dev_pre1(json_snapshot):
    d = json_snapshot['Data'].copy()
    json_snapshot['Data'] = d[0]
    json_snapshot['Items'] = d[1]
    return json_snapshot


def dev_pre0(json_snapshot):
    d = json_snapshot['Data'].copy()
    json_snapshot['Data'] = [d, {}]
    return json_snapshot


def get_snapshot_pre_version(json_snapshot):
    """Retrieve snapshot from really old (pre-version) json save"""
    index = len(VERSIONS)
    converter = VERSION_FUNCTIONS + [dev_pre1, dev_pre0]
    if type(json_snapshot['Data']) is dict:
        index += 1
    while index > 0:
        json_snapshot = converter[index](json_snapshot)
        index += -1
    return json_snapshot
