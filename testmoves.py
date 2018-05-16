import unittest
from battle import Battle
from collections import namedtuple
Decision = namedtuple('Decision', ['type', 'selection'])

class TestSimpleMoves(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(debug=False, rng=False)

    def test_tackle(self):
        self.battle.join(0, [{'species': 'charmander', 'level': 5, 'moves': ['tackle']}])
        self.battle.join(1, [{'species': 'magnemite', 'level': 5, 'moves': ['tackle']}])

        self.battle.choose(0, Decision('move', 0))
        self.battle.choose(1, Decision('move', 0))
        self.battle.doTurn()

        #damage calcs were done by hand
        self.assertEqual(self.battle.sides[0].pokemon[0].hp, self.battle.sides[0].pokemon[0].maxhp-5)
        self.assertEqual(self.battle.sides[1].pokemon[0].hp, self.battle.sides[1].pokemon[0].maxhp-2)
