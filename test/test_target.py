import unittest
from sim.battle import Battle
from data import dex

class TestTarget(unittest.TestCase):

    def test_normal(self):
        b = Battle(doubles=True, debug=False, rng=False)
        b.join(0, [{'species': 'pidgey',  'moves': ['thunderbolt', 'protect']},
                   {'species': 'charmander', 'moves': ['tackle']}])
        b.join(1, [{'species': 'rattata',  'moves': ['thunderbolt', 'protect']},
                   {'species': 'squirtle', 'moves': ['tackle', 'watergun']}])

        b.choose(0, [dex.Decision('move', 0, 'foe1'), dex.Decision('move', 0, 'foe1')])
        b.choose(1, [dex.Decision('move', 0), dex.Decision('move', 0)])
        b.do_turn()

        pidgey = b.sides[0].pokemon[0]
        charmander = b.sides[0].pokemon[1]
        rattata = b.sides[1].pokemon[0]
        squirtle = b.sides[1].pokemon[1]

        #damage calcs were done by hand
        self.assertEqual(rattata.hp, rattata.maxhp)
        self.assertEqual(squirtle.hp, squirtle.maxhp-70)

    def test_spread(self):
        b = Battle(doubles=True, debug=False, rng=False)
        b.join(0, [{'species': 'pidgey',  'moves': ['protect']},
                   {'species': 'charmander', 'moves': ['heatwave']}])
        b.join(1, [{'species': 'rattata',  'moves': ['thunderbolt', 'protect']},
                   {'species': 'squirtle', 'moves': ['tackle', 'watergun']}])

        b.choose(0, [dex.Decision('move', 0, 'foe1'), dex.Decision('move', 0)])
        b.choose(1, [dex.Decision('move', 0), dex.Decision('move', 0)])
        b.do_turn()

        pidgey = b.sides[0].pokemon[0]
        charmander = b.sides[0].pokemon[1]
        rattata = b.sides[1].pokemon[0]
        squirtle = b.sides[1].pokemon[1]

        #damage calcs were done by hand
        self.assertEqual(rattata.hp, rattata.maxhp-69)
        self.assertEqual(squirtle.hp, squirtle.maxhp-23)

    def runTest(self):
        self.test_normal()
        self.test_spread()
