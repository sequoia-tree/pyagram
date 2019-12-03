from . import encode

TERMINAL_HEIGHT = 58
TERMINAL_WIDTH = 80

def separator(title=''):
    """
    <summary>

    :param title:
    :return:
    """
    title = f'{title.upper()} ' if title else ''
    return f'{title}{"-" * (TERMINAL_WIDTH - len(title))}'

def prepend(prefix, text):
    """
    <summary> # prepend prefix to every line in text

    :param text:
    :param prefix:
    :return:
    """
    return prefix + text.replace('\n', f'\n{prefix}')

def mapped_len(function):
    """
    <summary>

    :param function:
    :return:
    """
    return lambda object: len(function(object))

def get_binding(max_key_len, max_value_len):
    """
    <summary>

    :param max_key_len:
    :param max_value_len:
    :return:
    """
    return lambda key, value: f'|{key:>{max_key_len}}: {encode.reference_str(value):<{max_value_len}}|'
