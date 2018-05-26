import unittest
from sim.battle import Battle
from data import dex

class TestProtect(unittest.TestCase):

    def test_protect_invulnerable(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pidgeot',
                         'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'mew', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 1))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pidgeot = battle.sides[0].pokemon[0]
        self.assertEqual(pidgeot.hp, pidgeot.maxhp)
        self.assertTrue('protect' in pidgeot.volatile_statuses)

    def test_protect_fails(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pidgeot',
                         'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'mew', 'moves': ['tackle', 'protect']}])

        battle.choose(0, dex.Decision('move', 1))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        battle.choose(0, dex.Decision('move', 1))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pidgeot = battle.sides[0].pokemon[0]
        self.assertEqual(pidgeot.hp, pidgeot.maxhp-24)
        self.assertFalse('protect' in pidgeot.volatile_statuses)

    def test_protect_one_turn(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pidgeot',
                         'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'mew', 'moves': ['tackle', 'protect']}])

        battle.choose(0, dex.Decision('move', 1))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pidgeot = battle.sides[0].pokemon[0]
        self.assertEqual(pidgeot.hp, pidgeot.maxhp-24)
    def runTest(self):
        self.test_protect_invulnerable()
        self.test_protect_fails()
        self.test_protect_one_turn()
