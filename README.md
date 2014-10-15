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


This module provides a `spy` object that resolves a setting attribute by
searching sequentially in following places: manually set settings,
directory variables (also known as variable catalog), user-provided
settings module, manually set fallback settings.
