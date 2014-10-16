from distutils.core import setup

LONG_DESCRIPTION = '''\
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

For more details see the source code at
https://github.com/ydm/settingspy
'''


setup(
    author='Yordan Miladinov',
    author_email='yordan@4web.bg',
    description='Easy settings for Python projects',
    license='LGPLv3',
    long_description=LONG_DESCRIPTION,
    name='settingspy',
    packages=['settingspy'],
    url='https://github.com/ydm/settingspy',
    version='1.1.1',
)
