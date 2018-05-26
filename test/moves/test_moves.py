import unittest
from sim.battle import Battle
from data import dex

class TestDamageCalc(unittest.TestCase):

    def test_tackle(self):
        battle = Battle(debug=False, rng=False)
        """tests tackle with STAB and no STAB"""
        battle.join(0, [{'species': 'charmander', 'level': 5, 'moves': ['tackle']}])
        battle.join(1, [{'species': 'magnemite', 'level': 5, 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        nic = battle.sides[0]
        sam = battle.sides[1]

        #damage calcs were done by hand
        self.assertEqual(nic.pokemon[0].hp, nic.pokemon[0].maxhp-5)
        self.assertEqual(sam.pokemon[0].hp, sam.pokemon[0].maxhp-2)

    def test_fakeout(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'charmander', 'level': 5, 'moves': ['fakeout']}])
        battle.join(1, [{'species': 'magnemite', 'level': 5, 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        magnemite = battle.sides[1].pokemon[0]
        charmander = battle.sides[0].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(charmander.hp, charmander.maxhp-5)
        self.assertEqual(magnemite.hp, magnemite.maxhp-2)

    def test_level_difference(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'abomasnow', 'level': 50, 'moves': ['headbutt']}])
        battle.join(1, [{'species': 'wailord', 'level': 100, 'moves': ['surf']}])

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        nic = battle.sides[0]
        sam = battle.sides[1]

        #damage calcs were done by hand
        self.assertEqual(nic.pokemon[0].hp, nic.pokemon[0].maxhp-117)
        self.assertEqual(sam.pokemon[0].hp, sam.pokemon[0].maxhp-29)

    def runTest(self):
        self.test_tackle()
        self.test_level_difference()
        self.test_fakeout()

if __name__ == '__main__':
    unittest.main()
