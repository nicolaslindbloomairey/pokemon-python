from test.test_moves import TestDamageCalc
from test.test_stat import TestStatCalc
from test.test_decisions import TestDecisions
from test.test_mega import TestMega
from test.test_protect import TestProtect
import unittest

suite = unittest.TestSuite()
suite.addTest(TestDamageCalc())
suite.addTest(TestStatCalc())
suite.addTest(TestDecisions())
suite.addTest(TestMega())
suite.addTest(TestProtect())

unittest.TextTestRunner().run(suite)
