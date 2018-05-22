import unittest
from sim.battle import Battle
from data import dex

class TestAcrobatics(unittest.TestCase):
        
    def test_acrobatics(self):
        b = Battle(debug=False, rng=False)
        b.join(0, [{'species': 'charmander', 'moves': ['tackle']}])
        b.join(1, [{'species': 'pidgey', 'moves': ['acrobatics']}])

        b.choose(0, dex.Decision('move', 0))
        b.choose(1, dex.Decision('move', 0))
        b.do_turn()

        charmander = b.sides[0].pokemon[0]
        pidgey = b.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(charmander.hp, charmander.maxhp-76)

    def test_acrobatics_noitem(self):
        b = Battle(debug=False, rng=False)
        b.join(0, [{'species': 'charmander', 'moves': ['tackle']}])
        b.join(1, [{'species': 'pidgey', 'item': 'pokeball','moves': ['acrobatics']}])

        b.choose(0, dex.Decision('move', 0))
        b.choose(1, dex.Decision('move', 0))
        b.do_turn()

        charmander = b.sides[0].pokemon[0]
        pidgey = b.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(charmander.hp, charmander.maxhp-39)

    def runTest(self):
        self.test_acrobatics() 
        self.test_acrobatics_noitem()
