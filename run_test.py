from test.test_moves import TestSimpleMoves
import unittest

suite = unittest.TestSuite()
suite.addTest(TestSimpleMoves())

unittest.TextTestRunner().run(suite)
