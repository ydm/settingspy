# settingspy #

Easy settings for projects, written in Python

## Description ##

This module provides a `spy` object that resolves an attribute by
searching sequentially in following places:

1. manually set settings
2. settings catalog
3. user-provided settings module
4. manually set fallbacks


### Examples ###

#### Manally set settings ####

```python
from settingspy import spy
spy['this_is_int'] = 123
spy['this_is_str'] = 'string'
print(spy.this_is_int, spy.this_is_str)
```

#### Settings catalog ####

Inside the directory specified by the SETTINGSPY_CATALOG environment
variable, a file named `something` may exist with the desired value.
File contents are restricted to booleans, integers, floats, strings.
They are parsed as if eval()ed, so strings should be wrapped in
parentheses.

```bash
$ echo 123 > "$SETTINGSPY_CATALOG/this_is_int"
$ echo "'string'" > "$SETTINGSPY_CATALOG/this_is_str"
```

#### User provided settings module ####

In mysettings.py:
```python
this_is_int = 123
this_is_str = 'string'
```

Then, from another package:
```python
import os
os.environ['SETTINGSPY_MODULE'] = 'mysettings'

from settingspy import spy
print(spy.this_is_int, spy.this_is_str)
```

#### Manually set fallbacks

In case a setting attribute isn't defined anywhere else.

```python
from settingspy import spy
spy.setfallback('this_is_int', 123)
spy.setfallback('this_is_str', 'string')
```

### Example usage ###

Below you can find implemented a simple logging system that allows
clients to set appropriate ENABLED flag, LEVEL and FILE depending on
their needs.

```python
# log.py:
import sys
from functools import partial
from settingspy import spy

# Default setting client may override using settingspy
spy.setfallback('LOGENABLED', True)
spy.setfallback('LOGFILE', sys.stderr)
spy.setfallback('LOGLEVEL', 0)


_LEVELS = ['message', 'info', 'debug', 'warning', 'error']


def _log(level, *args):
    if spy.LOGENABLED and level >= spy.LOGLEVEL:
        print('[%s]' % _LEVELS[level], *args, file=spy.LOGFILE)


m = partial(_log, 0)
i = partial(_log, 1)
d = partial(_log, 2)
w = partial(_log, 3)
e = partial(_log, 4)

# main.py:
from settingspy import spy
import log

spy['LOGLEVEL'] = 3

log.m("this won't be printed")
log.i("this won't be printed too")
log.d("neither will be this")
log.w("but this WILL be printed")
log.e("as well as this")
```
