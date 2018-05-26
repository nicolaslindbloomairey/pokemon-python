import unittest
import math
from sim.battle import Battle
from data import dex

class TestBurn(unittest.TestCase):
    def test_residual_damage(self):
        battle = Battle(debug=False, rng=False)

        battle.join(0, [{'species': 'pidgey'}])
        battle.join(1, [{'species': 'rattata', 'moves': ['willowisp']}])

        battle.choose(0, dex.Decision('move', 0))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pidgey = battle.sides[0].pokemon[0]
        self.assertEqual(pidgey.hp, pidgey.maxhp-math.floor(pidgey.maxhp*0.0625))

    def runTest(self):
        self.test_residual_damage()
