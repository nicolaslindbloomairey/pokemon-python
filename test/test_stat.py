import unittest
from sim.battle import Battle
from data import dex

class TestStatCalc(unittest.TestCase):

    def test_case1(self):
        battle = Battle(debug=False, rng=False)

        battle.join(0, [{'species': 'mew', 'level': 76, }])
        stats = battle.sides[0].pokemon[0].stats

        #stat calcs were checked by smogon
        self.assertEqual(stats.hp, 261)
        self.assertEqual(stats.attack, 180)
        self.assertEqual(stats.defense, 180)
        self.assertEqual(stats.specialattack, 180)
        self.assertEqual(stats.specialdefense, 180)
        self.assertEqual(stats.speed, 180)

    def test_case2(self):
        battle = Battle(debug=False, rng=False)

        battle.join(0, [{'species': 'mew', 'level': 76, 'ivs': dex.Stats(15, 0, 8, 7, 1, 31)}])
        stats = battle.sides[0].pokemon[0].stats

        #stat calcs were checked by smogon
        self.assertEqual(stats.hp, 249)
        self.assertEqual(stats.attack, 157)
        self.assertEqual(stats.defense, 163)
        self.assertEqual(stats.specialattack, 162)
        self.assertEqual(stats.specialdefense, 157)
        self.assertEqual(stats.speed, 180)

    def test_case3(self):
        battle = Battle(debug=False, rng=False)

        battle.join(0, [{'species': 'mew', 'level': 76, 'ivs': dex.Stats(15, 0, 8, 7, 1, 31),
                              'evs': dex.Stats(252, 0, 0, 4, 0, 252)}])
        stats = battle.sides[0].pokemon[0].stats

        #stat calcs were checked by smogon
        self.assertEqual(stats.hp, 297)
        self.assertEqual(stats.attack, 157)
        self.assertEqual(stats.defense, 163)
        self.assertEqual(stats.specialattack, 163)
        self.assertEqual(stats.specialdefense, 157)
        self.assertEqual(stats.speed, 228)

    def test_case4(self):
        battle = Battle(debug=False, rng=False)

        battle.join(0, [{'species': 'mew', 'level': 76, 'ivs': dex.Stats(15, 0, 8, 7, 1, 31),
                              'evs': dex.Stats(252, 0, 0, 4, 0, 252), 'nature': 'adamant'}])
        stats = battle.sides[0].pokemon[0].stats

        #stat calcs were checked by smogon
        self.assertEqual(stats.hp, 297)
        self.assertEqual(stats.attack, 172)
        self.assertEqual(stats.defense, 163)
        self.assertEqual(stats.specialattack, 146)
        self.assertEqual(stats.specialdefense, 157)
        self.assertEqual(stats.speed, 228)

    def maximum_inbattle_speed(self):
        battle = Battle(debug=False, rng=False)
        battle.join(0, [{'species': 'deoxysspeed', 'ability': 'swiftswim', 'level': 100, 'ivs': dex.Stats(0, 0, 0, 0, 0, 31),
                         'evs': dex.Stats(0, 0, 0, 0, 0, 252), 'nature': 'jolly', 'item': 'choicescarf'}])
        battle.sides[0].pokemon[0].boosts['spe'] = 6
        battle.weather = 'rainy'
        battle.sides[0].volatile_statuses.add('tailwind')

        self.assertEqual(battle.sides[0].pokemon[0].get_speed(), 12096)

    def runTest(self):
        self.test_case1()
        self.test_case2()
        self.test_case3()
        self.test_case4()
        self.maximum_inbattle_speed()

if __name__ == '__main__':
    unittest.main()
