import unittest
from sim.battle import Battle
from data import dex

class TestSimpleMoves(unittest.TestCase):
    def setUp(self):
        self.battle = Battle(debug=False, rng=False)

    def test_tackle(self):
        self.battle.join(0, [{'species': 'charmander', 'level': 5, 'moves': ['tackle']}])
        self.battle.join(1, [{'species': 'magnemite', 'level': 5, 'moves': ['tackle']}])

        self.battle.choose(0, dex.Decision('move', 0))
        self.battle.choose(1, dex.Decision('move', 0))
        self.battle.do_turn()

        nic = self.battle.sides[0]
        sam = self.battle.sides[1]

        #damage calcs were done by hand
        self.assertEqual(nic.pokemon[0].hp, nic.pokemon[0].maxhp-5)
        self.assertEqual(sam.pokemon[0].hp, sam.pokemon[0].maxhp-2)

    def runTest(self):
        self.test_tackle()

if __name__ == '__main__':
    unittest.main()
