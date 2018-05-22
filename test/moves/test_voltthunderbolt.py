import unittest
from sim.battle import Battle
from data import dex

class TestVoltThunderbolt(unittest.TestCase):

    def test_voltthunderbolt(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pikachuhoenn', 'item': 'pikashuniumz', 'moves': ['thunderbolt']}])
        battle.join(1, [{'species': 'magnemite', 'item': 'normaliumz', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0, zmove=True))
        battle.choose(1, dex.Decision('move', 0, zmove=True))
        battle.do_turn()

        pikachu = battle.sides[0].pokemon[0]
        magnemite = battle.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(magnemite.hp, magnemite.maxhp-61)
        self.assertEqual(pikachu.hp, pikachu.maxhp-42)
    def runTest(self):
        self.test_voltthunderbolt()
