import unittest
from sim.battle import Battle
from data import dex

class TestCrit(unittest.TestCase):
    def test_crit_damage(self):
        b = Battle(debug=False, rng=False)

        b.join(0, [{'species': 'spheal', 'moves': ['frostbreath']}])
        b.join(1, [{'species': 'rattata', 'moves': ['tackle']}])

        b.choose(0, dex.Decision('move', 0))
        b.choose(1, dex.Decision('move', 0))
        b.do_turn()

        rattata = b.sides[1].pokemon[0]

        self.assertEqual(rattata.hp, rattata.maxhp-85)
        
    def runTest(self):
        self.test_crit_damage()
