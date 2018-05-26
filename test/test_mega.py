import unittest
from sim.battle import Battle
from data import dex

class TestMega(unittest.TestCase):

    def test_pidgeot(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pidgeot',
                         'item': 'pidgeotite',
                         'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'mew', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0, mega=True))
        battle.choose(1, dex.Decision('move', 0, mega=True))
        battle.do_turn()

        pidgeot = battle.sides[0].pokemon[0]
        self.assertEqual(pidgeot.species, 'pidgeotmega')
        self.assertEqual(pidgeot.hp, pidgeot.maxhp-23)

    def test_mewtwo_x(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'mewtwo',
                         'item': 'mewtwonitex',
                         'moves': ['tackle', 'protect']
                         }])
        battle.join(1, [{'species': 'charizard',
                         'item': 'charizarditex',
                         'moves': ['tackle']
                         }])

        battle.choose(0, dex.Decision('move', 0, mega=True))
        battle.choose(1, dex.Decision('move', 0, mega=False))
        battle.do_turn()

        mewtwo = battle.sides[0].pokemon[0]
        charizard = battle.sides[1].pokemon[0]
        self.assertEqual(mewtwo.species, 'mewtwomegax')
        self.assertEqual(mewtwo.hp, mewtwo.maxhp-17)
    
    def runTest(self):
        self.test_pidgeot()
        self.test_mewtwo_x
