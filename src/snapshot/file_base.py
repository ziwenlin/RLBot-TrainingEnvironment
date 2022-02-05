import json


def _file_exist(path):
    try:
        with open(path, 'r'):
            # print('File not existing')
            return True
    except (FileExistsError, FileNotFoundError):
        # print('File is existing')
        return False


def _create_file_if_not_exist(path, text=''):
    if not _file_exist(path):
        with open(path, 'w') as f:
            f.write(text)
            print('Created file:', path)


def _read_file(path):
    with open(path, 'r') as f:
        return f.read()


def __read_json(path):
    return json.loads(
        _read_file(path))


def _pretty_json(text):
    objectcount = 0
    new_text = ''
    for index, char in enumerate(text):
        if char in ['{', '[']:
            objectcount += 1
        if char in ['}', ']']:
            objectcount -= 1
        if objectcount > 2:
            if char in ['\n', '\r']:
                continue
        new_text += char
    return new_text


def _write_json(path, data):
    text = json.dumps(data, indent=0)
    text = _pretty_json(text)
    with open(path, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    path = '../../settings.json'
    _create_file_if_not_exist(path, '{}')
    with open(path, 'r') as file:
        data = file.read()
    print(data)
    path = '../../stored_game_state.json'
    _create_file_if_not_exist(path, text='[]')
    with open(path, 'r') as file:
        data = file.read()
    print(data)
