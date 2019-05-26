#--------------
# instead of using this file
# just run
# python3 -m unittest discover test/
# or
# python3 -m unittest discover -v test/
from test.test_moves import TestDamageCalc
from test.test_stat import TestStatCalc
from test.test_decisions import TestDecisions
from test.test_mega import TestMega
from test.test_protect import TestProtect
from test.test_zmove import TestZMove
import unittest

suite = unittest.TestSuite()
suite.addTest(TestDamageCalc())
suite.addTest(TestStatCalc())
suite.addTest(TestDecisions())
suite.addTest(TestMega())
suite.addTest(TestProtect())
suite.addTest(TestZMove())

unittest.TextTestRunner().run(suite)
