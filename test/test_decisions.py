import unittest
from sim.battle import Battle
from data import dex

class TestDecisions(unittest.TestCase):

    def test_switch(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'mew'}, {'species': 'mewtwo'}, {'species': 'magnezone'}])
        battle.join(1, [{'species': 'pidgey', 'moves': ['peck']}])

        battle.choose(0, dex.Decision('switch', 2))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        mew = battle.sides[0].pokemon[0]
        mewtwo = battle.sides[0].pokemon[1]
        magnezone = battle.sides[0].pokemon[2]

        pidgey = battle.sides[1].pokemon[0]


        self.assertEqual(battle.sides[0].active_pokemon[0].species, 'magnezone')
        self.assertEqual(mew.hp, mew.maxhp)
        self.assertEqual(magnezone.hp, magnezone.maxhp-3)
    
    def runTest(self):
        self.test_switch()
