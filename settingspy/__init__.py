# -*- coding: utf-8 -*-

"""
This module provides a `spy` object that resolves an attribute by
searching sequentially in following places:

0. manually set settings
1. settings catalog
2. user-provided settings module
3. manually set fallbacks


Examples:

0. Manally set settings:

from settingspy import spy
spy['this_is_int'] = 123
spy['this_is_str'] = 'string'
print(spy.this_is_int, spy.this_is_str)


1. Settings catalog

Inside the directory specified by the SETTINGSPY_CATALOG environment
variable, a file named `something` may exist with the desired value.
File contents are restricted to booleans, integers, floats, strings.
They are parsed as if eval()ed, so strings should be wrapped in
parentheses.

$ echo 123 > "$SETTINGSPY_CATALOG/this_is_int"
$ echo "'string'" > "$SETTINGSPY_CATALOG/this_is_str"


2. User provided settings module

in file mysettings.py:
this_is_int = 123
this_is_str = 'string'

import os; os.environ['SETTINGSPY_MODULE'] = 'mysettings'
from settingspy import spy; print(spy.this_is_int, spy.this_is_str)


3. Manually set fallbacks

In case a setting attribute isn't defined anywhere else.

from settingspy import spy
spy.setfallback('this_is_int', 123)
spy.setfallback('this_is_str', 'string')
"""

from collections.abc import Mapping
from importlib import import_module

import operator
import os


__version__ = '1.1.1'


MODULE_VAR = 'SETTINGSPY_MODULE'
CATALOG_VAR = 'SETTINGSPY_CATALOG'


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


class SettingsCatalog(Mapping):

    def __init__(self, catalog):
        self._wrapped = {}
        if catalog:
            try:
                files = os.listdir(catalog)
            except FileNotFoundError as e:
                raise ImproperlyConfigured(e)
            else:
                for var in files:
                    fpath = os.path.join(catalog, var)
                    if os.path.isfile(fpath):
                        with open(fpath, encoding='utf-8') as f:
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

    def __init__(self, catalog=None, module=None):
        super(Settings, self).__init__()
        self.init(catalog, module)

    def init(self, catalog=None, module=None):
        self.manual = {}
        self.catalog = SettingsCatalog(catalog)
        self.mod = import_module(module) if module else None
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
    os.environ.get(CATALOG_VAR),
    os.environ.get(MODULE_VAR)
)
