import unittest
from sim.battle import Battle
from data import dex

class TestDrainMoves(unittest.TestCase):
        
    def test_drain_moves(self):
        b = Battle(debug=False, rng=False)
        b.join(0, [{'species': 'charmander', 'moves': ['tackle']}])
        b.join(1, [{'species': 'bulbasaur', 'moves': ['tackle', 'absorb']}])

        b.choose(0, dex.Decision('move', 0))
        b.choose(1, dex.Decision('move', 0))
        b.do_turn()

        b.choose(0, dex.Decision('move', 0))
        b.choose(1, dex.Decision('move', 1))
        b.do_turn()

        charmander = b.sides[0].pokemon[0]
        bulbasaur = b.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(charmander.hp, charmander.maxhp-30)
        self.assertEqual(bulbasaur.hp, bulbasaur.maxhp-36)
    def runTest(self):
        self.test_drain_moves() 
