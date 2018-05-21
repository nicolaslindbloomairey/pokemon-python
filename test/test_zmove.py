import unittest
from sim.battle import Battle
from data import dex

class TestZMove(unittest.TestCase):

    def test_zmove(self):
        battle = Battle(debug=False, rng=False)
        """tests tackle with STAB and no STAB"""
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

    def test_zmove_protect(self):
        battle = Battle(debug=False, rng=False)
        """tests tackle with STAB and no STAB"""
        battle.join(0, [{'species': 'pikachuhoenn', 'item': 'pikashuniumz', 'moves': ['thunderbolt']}])
        battle.join(1, [{'species': 'magnemite', 'moves': ['protect']}])

        battle.choose(0, dex.Decision('move', 0, zmove=True))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pikachu = battle.sides[0].pokemon[0]
        magnemite = battle.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(magnemite.hp, magnemite.maxhp-15)

    def test_zmove_twice(self):
        battle = Battle(debug=False, rng=False)
        """tests tackle with STAB and no STAB"""
        battle.join(0, [{'species': 'pikachuhoenn', 'item': 'pikashuniumz', 'moves': ['thunderbolt']}])
        battle.join(1, [{'species': 'magnemite', 'moves': ['tackle']}])

        battle.choose(0, dex.Decision('move', 0, zmove=True))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        battle.choose(0, dex.Decision('move', 0, zmove=True))
        battle.choose(1, dex.Decision('move', 0))
        battle.do_turn()

        pikachu = battle.sides[0].pokemon[0]
        magnemite = battle.sides[1].pokemon[0]

        #damage calcs were done by hand
        self.assertEqual(magnemite.hp, magnemite.maxhp-89)

    def runTest(self):
        self.test_zmove()
        self.test_zmove_protect()
        self.test_zmove_twice()
