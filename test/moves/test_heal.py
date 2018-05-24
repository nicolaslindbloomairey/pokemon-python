import unittest
from sim.battle import Battle
from data import dex

class TestHeal(unittest.TestCase):

    def test_heal(self):
        b = Battle(debug=False, rng=False)
        b.join(0, [{'species': 'pikachuhoenn', 'item': 'pikashuniumz', 'moves': ['thunderbolt', 'protect']}])
        b.join(1, [{'species': 'magnemite', 'item': 'normaliumz', 'moves': ['tackle', 'recover']}])

        b.choose(0, dex.Decision('move', 0, zmove=True))
        b.choose(1, dex.Decision('move', 0, zmove=True))
        b.do_turn()

        b.choose(0, dex.Decision('move', 1))
        b.choose(1, dex.Decision('move', 1))
        b.do_turn()

        pikachu = b.sides[0].pokemon[0]
        magnemite = b.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(magnemite.hp, magnemite.maxhp-11)
        self.assertEqual(pikachu.hp, pikachu.maxhp-42)

    def runTest(self):
        self.test_heal()
