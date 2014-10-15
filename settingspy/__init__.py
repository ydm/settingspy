# -*- coding: utf-8 -*-

"""
This module provides a `spy` object that resolves an attribute by
searching sequentially in following places:

0. manually set settings
1. variable catalog
2. user-provided settings module
3. manually set fallbacks


Examples:

0. Manally set settings:

from settingspy import spy
spy['this_is_int'] = 123
spy['this_is_str'] = 'string'


1. Variable catalog

Inside the directory specified by the SETTINGSPY_VARIABLE_CATALOG
environment variable, a file named `something` may exist with the
desired value.  File contents are restricted to booleans, integers,
floats, strings.  They are parsed as if eval()ed, so strings should be
wrapped in parentheses.

$ echo 123 > "$SETTINGSPY_VARIABLE_CATALOG/this_is_int"
$ echo "'string'" > "$SETTINGSPY_VARIABLE_CATALOG/this_is_str"


2. User provided settings module

in file mysettings.py:
this_is_int = 123
this_is_str = 'string'

import os; os.environ['SETTINGSPY_SETTINGS_MODULE'] = 'mysettings'
from settingspy import spy; print(spy.this_is_int, spy.this_is_str)


3. Manually set fallbacks -- in case everything else fails

from settingspy import spy
spy.setfallback('this_is_int', 123)
spy.setfallback('this_is_str', 'string')
"""

from collections.abc import Mapping
from importlib import import_module

import operator
import os


SETTINGS_MODULE_VAR = 'SETTINGSPY_SETTINGS_MODULE'
VARIABLE_CATALOG_VAR = 'SETTINGSPY_VARIABLE_CATALOG'


class ImproperlyConfigured(Exception):
    pass


def _parse_bool(s):
    if s == 'False':
        return False
    elif s == 'True':
        return True
    raise ValueError


def _parse_str(s):
    wrappers = [
        "'",
        "'''",
        '"""',
        '"'
    ]
    for w in wrappers:
        if s.startswith(w) and s.endswith(w):
            length = len(w)
            return s[length:-length]
    raise ValueError


def _parse_content(s):
    stripped = s.strip()
    for p in (int, float, _parse_bool, _parse_str):
        try:
            return p(stripped)
        except ValueError:
            pass
    raise ValueError('content cannot be parsed: {}'.format(stripped))


def _method_proxy(fn):
    def inner(self, *args):
        return fn(self._wrapped, *args)
    return inner


class VariableCatalog(Mapping):

    def __init__(self, variable_catalog):
        self._wrapped = {}
        if variable_catalog:
            try:
                files = os.listdir(variable_catalog)
            except FileNotFoundError as e:
                raise ImproperlyConfigured(e)
            else:
                for var in files:
                    fpath = os.path.join(variable_catalog, var)
                    with open(fpath) as f:
                        content = f.read()
                    self._wrapped[var] = _parse_content(content)

    # This object is actually a mapping and should provide these
    # methods, as defined by ABC
    __getitem__ = _method_proxy(operator.getitem)
    __iter__ = _method_proxy(iter)
    __len__ = _method_proxy(len)
    __contains__ = _method_proxy(operator.contains)
    keys = _method_proxy(lambda self: self.keys())
    items = _method_proxy(lambda self: self.items())
    values = _method_proxy(lambda self: self.values())
    get = _method_proxy(lambda self, *args: self.get(*args))
    __eq__ = _method_proxy(operator.eq)
    __ne__ = _method_proxy(operator.ne)


class Settings(object):

    def __init__(self, variable_catalog=None, settings_module=None):
        super(Settings, self).__init__()
        self.init(variable_catalog, settings_module)

    def init(self, variable_catalog=None, settings_module=None):
        self.manual = {}
        self.catalog = VariableCatalog(variable_catalog)
        self.mod = import_module(settings_module) if settings_module else None
        self.fallback = {}

    def __getattr__(self, name):
        for d in (self.manual, self.catalog):
            try:
                return d[name]
            except KeyError:
                pass
        try:
            return getattr(self.mod, name)
        except AttributeError:
            pass
        try:
            return self.fallback[name]
        except KeyError:
            pass
        raise AttributeError('no setting named `{}`'.format(name))

    def __setitem__(self, name, value):
        self.manual[name] = value

    def setfallback(self, name, value):
        self.fallback[name] = value


spy = Settings(
    os.environ.get(VARIABLE_CATALOG_VAR),
    os.environ.get(SETTINGS_MODULE_VAR)
)
