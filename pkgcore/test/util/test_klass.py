# Copyright: 2006 Brian Harring <ferringb@gmail.com>
# License: GPL2

from pkgcore.test import TestCase
from pkgcore.util import klass


class Test_native_GetAttrProxy(TestCase):
    kls = staticmethod(klass.native_GetAttrProxy)
    
    def test_it(self):
        class foo1(object):
            def __init__(self, obj):
                self.obj = obj
            __getattr__ = self.kls('obj')

        class foo2(object):
            pass
        
        o2 = foo2()
        o = foo1(o2)
        self.assertRaises(AttributeError, getattr, o, "blah")
        self.assertEqual(o.obj, o2)
        o2.foon = "dar"
        self.assertEqual(o.foon, "dar")
        o.foon = "foo"
        self.assertEqual(o.foon, 'foo')


class Test_CPY_GetAttrProxy(Test_native_GetAttrProxy):

    kls = staticmethod(klass.GetAttrProxy)
    if klass.GetAttrProxy is klass.native_GetAttrProxy:
        skip = "cpython extension isn't available"

    def test_sane_recursion_bail(self):
        # people are stupid; if protection isn't in place, we wind up blowing
        # the c stack, which doesn't result in a friendly Exception being
        # thrown.
        # results in a segfault.. so if it's horked, this will bail the test
        # runner.

        class c(object):
            __getattr__ = self.kls("obj")
        
        o = c()
        o.obj = o
        # now it's cyclical.
        self.assertRaises(RuntimeError, getattr, o, "hooey")


class Test_native_contains(TestCase):
    func = staticmethod(klass.native_contains)
    
    def test_it(self):
        class c(dict):
            __contains__ = self.func
        d = c({"1":2})
        self.assertIn("1", d)
        self.assertNotIn(1, d)


class Test_CPY_contains(Test_native_contains):
    func = staticmethod(klass.contains)
    
    if klass.contains is klass.native_contains:
        skip = "cpython extension isn't available"


class Test_native_get(TestCase):
    func = staticmethod(klass.native_get)
    
    def test_it(self):
        class c(dict):
            get = self.func
        d = c({"1":2})
        self.assertEqual(d.get("1"), 2)
        self.assertEqual(d.get("1", 3), 2)
        self.assertEqual(d.get(1), None)
        self.assertEqual(d.get(1, 3), 3)

class Test_CPY_get(Test_native_get):
    func = staticmethod(klass.get)
    
    if klass.get is klass.native_get:
        skip = "cpython extension isn't available"
    