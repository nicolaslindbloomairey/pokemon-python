from test.test_moves import TestDamageCalc
from test.test_stat import TestStatCalc
import unittest

suite = unittest.TestSuite()
suite.addTest(TestDamageCalc())
suite.addTest(TestStatCalc())

unittest.TextTestRunner().run(suite)
