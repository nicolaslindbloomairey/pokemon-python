from data import dex
import random
import math
import re

class Pokemon(object):
    def __init__(self, pokemon_set, side_id, side=None, battle=None):
        self.side_id = side_id
        self.side = side
        self.battle = battle

        self.pokemon_set = pokemon_set

        self.species = re.sub(r'\W+', '', pokemon_set['species'].lower())

        self.nature = self.pokemon_set.get('nature', 'hardy')

        self.template = dex.pokedex[self.species]

        self.name = pokemon_set.get('name', self.template.species)

        self.moves = pokemon_set['moves']
        self.base_moves = self.moves

        self.fainted = False
        self.status = ''
        self.position = 0
        self.burned = False

        self.accuracy = 0
        self.evasion = 0
        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
        }
        self.volatile_statuses = set()
        
        self.active = False

        self.level = pokemon_set.get('level', 50)

        self.base_ability = self.pokemon_set.get('ability', self.template.abilities.normal0)
        self.base_ability = re.sub(r'\W+', '', self.base_ability.lower())
        self.ability = self.base_ability
        self.item = pokemon_set.get('item', None)

        self.types = self.template.types

        if 'evs' not in pokemon_set:
            self.pokemon_set['evs'] = dex.Stats(0, 0, 0, 0, 0, 0)
        if 'ivs' not in pokemon_set:
            self.pokemon_set['ivs'] = dex.Stats(31, 31, 31, 31, 31, 31)

        self.calculate_stats()
        self.hp = self.stats.hp
        self.maxhp = self.hp


    def __str__(self):
        return self.name + '|' + str(self.nature) + '|' + str(self.ability) +  '|' + str(self.level) + '|' + str(self.status) + '|'+ 'hp' + str(self.hp) 

    def calculate_stats(self):
#       hp
        hp = math.floor(( (self.pokemon_set['ivs'].hp + (2 * self.template.baseStats.hp) + (self.pokemon_set['evs'].hp/4) ) * (self.level/100) ) + 10 + self.level )

        stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
        cal = []
        for stat in stats:
            cal.append(math.floor((((getattr(self.pokemon_set['ivs'],stat) + (2 * getattr(self.template.baseStats, stat)) + (getattr(self.pokemon_set['evs'],stat)/4) ) * (self.level/100) ) + 5) * dex.nature_dex[self.nature].values[stat] ))

        self.stats = dex.Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])


#        print(self.name, self.nature, self.pokemon_set['evs'], self.stats)

    def faint(self):
        self.hp = 0
        self.fainted = True
        self.side.pokemon_left -= 1
    
