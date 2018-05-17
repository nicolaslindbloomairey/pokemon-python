import unittest
from sim.battle import Battle
from data import dex

class TestMega(unittest.TestCase):

    def test_pidgeot(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'pidgeot', 'item': 'pidgeotite', 'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'mew', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0, mega=True))
        battle.choose(1, dex.Decision('move', 0, mega=True))
        battle.do_turn()

        self.assertEqual(battle.sides[0].active_pokemon.species, 'pidgeotmega')
        self.assertEqual(battle.sides[0].active_pokemon.hp, battle.sides[0].active_pokemon.maxhp-23)

    def test_mewtwo_x(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'mewtwo', 'item': 'mewtwonitex', 'moves': ['tackle', 'protect']}])
        battle.join(1, [{'species': 'charizard', 'item': 'charizarditex', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0, mega=True))
        battle.choose(1, dex.Decision('move', 0, mega=True))
        battle.do_turn()

        self.assertEqual(battle.sides[0].active_pokemon.species, 'mewtwomegax')
        self.assertEqual(battle.sides[1].active_pokemon.species, 'charizarditex')
        self.assertEqual(battle.sides[0].active_pokemon.hp, battle.sides[0].active_pokemon.maxhp-30)
    
    def runTest(self):
        self.test_pidgeot()
        self.test_mewtwo_x
