# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

tempdir = tempfile.mkdtemp()
for k, v in (('catalogint', 123),
             ('catalogstr', 'something'),
             ('catalogbool', True),
             ('prio0', 'catalog'),
             ('prio1', 'catalog')):
    with open(os.path.join(tempdir, k), 'w', encoding='utf-8') as f:
        f.write(repr(v))

os.environ['SETTINGSPY_MODULE'] = 'testmod'
os.environ['SETTINGSPY_CATALOG'] = tempdir

from settingspy import spy


class TestSpy(unittest.TestCase):

    def test_fallback(self):
        spy.setfallback('fallback_test', 123)
        self.assertEqual(spy.fallback_test, 123)

    def test_catalog(self):
        self.assertEqual(spy.catalogbool, True)
        self.assertEqual(spy.catalogint, 123)
        self.assertEqual(spy.catalogstr, 'something')

    def test_module(self):
        self.assertEqual(spy.modbool, True)
        self.assertEqual(spy.modint, 123)
        self.assertEqual(spy.modstr, 'something')

    def test_manual(self):
        from settingspy import spy
        spy['manualbool'] = True
        spy['manualint'] = 123
        spy['manualstr'] = 'something'
        self.assertEqual(spy.manualbool, True)
        self.assertEqual(spy.manualint, 123)
        self.assertEqual(spy.manualstr, 'something')

    def test_priority(self):
        spy.setfallback('prio0', 'fallback')
        spy.setfallback('prio1', 'fallback')
        spy.setfallback('prio2', 'fallback')
        spy.setfallback('prio3', 'fallback')
        spy['prio0'] = 'manual'

        self.assertEqual(spy.prio3, 'fallback')
        self.assertEqual(spy.prio2, 'mod')
        self.assertEqual(spy.prio1, 'catalog')
        self.assertEqual(spy.prio0, 'manual')

    def test_attrerror(self):
        f = lambda: spy.nonexistent
        self.assertRaises(AttributeError, f)


if __name__ == '__main__':
    unittest.main()
    shutil.rmtree(tempdir)
else:
    shutil.rmtree(tempdir)
