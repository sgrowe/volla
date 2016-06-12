from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured
import re


def simple_url(url_pattern, view, kwargs=None, name=None):
    regex = _construct_regex(url_pattern, is_prefix=isinstance(view, (list, tuple)))
    return url(regex, view, kwargs, name)


def _construct_regex(pattern, is_prefix):
    if not pattern.startswith('/'):
        raise ImproperlyConfigured('simple_url pattern should start with a forward slash '
                                   '({!r} does not).'.format(pattern))
    pattern = pattern[1:]
    pieces = [_path_piece_to_regex_pattern(piece) for piece in pattern.split('/')]
    wrapper = '^{}' if is_prefix else '^{}$'
    return wrapper.format('/'.join(pieces))


def _path_piece_to_regex_pattern(piece):
    return _dynamic_path_piece(piece) if piece.startswith(' ') else re.escape(piece)


def _dynamic_path_piece(piece):
    name, _, piece_type = piece.strip().partition(': ')
    _validate_path_piece_name(name)
    pattern = _pattern_for_path_piece(piece_type.strip())
    regex = '(?P<{}>{})'.format(name, pattern)
    return regex


def _validate_path_piece_name(name):
    if not name or not re.match(r'^[a-zA-Z_]+$', name):
        raise ImproperlyConfigured('Bad path piece name in simple_url pattern: {!r}'.format(name))


def _pattern_for_path_piece(path_piece_type):
    path_type_patterns = {
        '': '[^/]+',
        'int': '\d+',
        'alpha': '[a-zA-Z]+',
        'multi': '.+',
    }
    try:
        type_pattern = path_type_patterns[path_piece_type]
    except KeyError:
        valid_types = ', '.join(repr(path_type_patterns.keys()))
        raise ImproperlyConfigured('simple_url path piece has unknown type: "{!r}". '
                                   'Valid options are: {}.'.format(path_piece_type, valid_types))
    return type_pattern
