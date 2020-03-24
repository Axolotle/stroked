_settings = {
    'linestyle': {
        'linecap': 1,
        'linejoin': 1,
        'linewidth': 1,
    },
    'guides': {
        'ascender': 2,
        'baseline': 7,
        'descender': 9,
    },
    'grid': {
        'size': (5, 9),
        'margin': (1, 1),
    },
}


def get_by_path(data, keys_name):
    """Access a nested object in dict by keys_name sequence."""
    for key in keys_name:
        data = data[key]
    return data


def set_by_path(data, keys_name, value):
    """Set a value in a nested object in dict by keys_name sequence."""
    for key in keys_name[:-1]:
        data = data.setdefault(key, {})
    data[keys_name[-1]] = value


def get(key_name):
    if key_name is not None:
        if '.' in key_name:
            key_name = key_name.split('.')
        if isinstance(key_name, list):
            return get_by_path(_settings, key_name)
        return _settings[key_name]
    else:
        return _settings


def set(key_name, value):
    if '.' in key_name:
        key_name = key_name.split('.')
    if isinstance(key_name, list):
        set_by_path(_settings, key_name, value)
    else:
        _settings[key_name] = value
