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

        self.nature = pokemon_set.get('nature', 'hardy')

        self.template = dex.pokedex[self.species]

        self.name = pokemon_set.get('name', self.template.species)

        self.moves = pokemon_set.get('moves', ['tackle']*4)
        self.base_moves = self.moves

        self.fainted = False
        self.status = ''
        self.position = 0
        self.burned = False
        self.protect_n = 0

        self.is_switching = False

        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
        }
        self.volatile_statuses = set()

        self.active = False
        self.active_turns = 0

        self.level = pokemon_set.get('level', 50)

        self.base_ability = pokemon_set.get('ability', self.template.abilities.normal0)
        self.base_ability = re.sub(r'\W+', '', self.base_ability.lower())
        self.ability = self.base_ability
        self.item = pokemon_set.get('item', 'pokeball')
        self.lost_item = False

        self.types = self.template.types

        if 'evs' not in pokemon_set:
            self.pokemon_set['evs'] = dex.Stats(0, 0, 0, 0, 0, 0)
        if 'ivs' not in pokemon_set:
            self.pokemon_set['ivs'] = dex.Stats(31, 31, 31, 31, 31, 31)

        self.calculate_stats()
        self.hp = self.stats.hp
        self.maxhp = self.hp


    def __str__(self):
        info = [self.name, self.nature, self.ability, self.level, self.status, self.hp]
        info.append(self.volatile_statuses)
        out = ''
        for each in info:
            out += str(each)+ '|'
        return out

    def mega_evolve(self):
        canmega = False
        if dex.item_dex[self.item].megaStone is not None:
            megaspecies = re.sub(r'\W+', '', dex.item_dex[self.item].megaStone.lower())
            if re.sub(r'\W+', '', dex.item_dex[self.item].megaEvolves.lower()) == self.species:
                canmega = True


        if canmega:
            # overwrite the current pokemon with the mega form
            self.species = megaspecies
            self.template = dex.pokedex[self.species]
            self.base_ability = self.template.abilities.normal0
            self.ability = self.base_ability
            self.types = self.template.types
            self.calculate_stats()
            self.hp = self.stats.hp
            self.maxhp = self.hp

    def boost(self, boosts):
        for stat in boosts:
            self.boosts[stat] += boosts[stat]
            if self.boosts[stat] > 6:
                self.boosts[stat] = 6
            if self.boosts[stat] < -6:
                self.boosts[stat] = -6


    def get_attack(self):
        modifier = dex.boosts[self.boosts['atk']]
        if self.ability == 'hugepower' or self.ability == 'purepower':
            modifier *= 2
        if self.ability == 'flowergift' and self.battle.weather == 'sunny':
            modifier *= 2
        if self.ability == 'hustle':
            modifier *= 1.5
        if self.ability == 'guts' and self.status != '':
            modifier *= 1.5
        if self.ability == 'slowstart' and self.active_turns < 5:
            modifier = 0.5
        if self.ability == 'defeatist' and self.hp / self.maxhp <= 0.5:
            modifier = 0.5
        if self.item == 'choiceband':
            modifier = 1.5
        if self.species == 'pikachu' and self.item == 'lightball':
            modifier = 2
        if (self.species == 'cubone' or self.species == 'marowak') and self.item == 'thickclub':
            modifier = 2
        return self.stats.attack * modifier

    def get_defense(self):
        modifier = dex.boosts[self.boosts['def']]
        if self.ability == 'marvelscale' and self.status != '':
            modifier *= 1.5
        if self.ability == 'grasspelt' and self.battle.terrain == 'grassy':
            modifier *= 1.5
        if self.species == 'ditto' and self.item == 'metalpowder':
            modifier = 2
        if self.template.evos is not None and self.item == 'eviolite':
            modifier = 1.5
        return self.stats.defense * modifier

    def get_specialattack(self):
        modifier = dex.boosts[self.boosts['spa']]
        if self.ability == 'solarpower' and self.battle.weather == 'sunny':
            modifier *= 1.5
        if self.ability == 'defeatist' and self.hp / self.maxhp <= 0.5:
            modifier = 0.5
        if self.item == 'choicespecs':
            modifier = 1.5
        if self.species == 'pikachu' and self.item == 'lightball':
            modifier = 2
        if self.species == 'clamperl' and self.item == 'deepseatooth':
            modifier = 2
        return self.stats.specialattack * modifier

    def get_specialdefense(self):
        modifier = dex.boosts[self.boosts['spd']]
        if self.ability == 'flowergift' and self.battle.weather == 'sunny':
            modifier *= 2
        if 'Rock' in self.types and self.battle.weather == 'sandstorm':
            modifier *= 1.5
        if self.item == 'assaultvest':
            modifier *= 1.5
        if self.species == 'clamperl' and self.item == 'deepseascale':
            modifier = 2
        if self.template.evos is not None and self.item == 'eviolite':
            modifier = 1.5
        return self.stats.specialdefense * modifier

    def get_speed(self):
        modifier = dex.boosts[self.boosts['spe']]
        if self.status == 'par' and self.ability != 'quickfeet':
            modifier *= 0.5
        if self.item == 'choicescarf':
            modifier *= 1.5
        if self.item in ['ironball', 'machobrace', 'powerbracer', 'powerbelt', 'powerlens', 'powerband', 'poweranklet', 'powerweight']:
            modifier *= 0.5
        if 'tailwind' in self.side.volatile_statuses:
            modifier *= 2.0
        if self.species == 'ditto' and self.item == 'quickpowder':
            modifier = 2
        if self.ability == 'swiftswim' and self.battle.weather == 'rainy':
            modifier *= 2
        if self.ability == 'chlorophyll' and self.battle.weather == 'sunny':
            modifier *= 2
        if self.ability == 'sandrush' and self.battle.weather == 'sandstorm':
            modifier *= 2
        if self.ability == 'slushrush' and self.battle.weather == 'hail':
            modifier *= 2
        if self.ability == 'unburden' and self.lost_item:
            modifier *= 2
        if self.ability == 'surgesurfer' and self.battle.terrain == 'electric':
            modifier *= 2
        if self.ability == 'quickfeet' and self.status != '':
            modifier *= 1.5
        if self.ability == 'slowstart' and self.active_turns < 5:
            modifier *= 0.5
        if self.battle.trickroom:
            # this is effectively the negative
            # invert the order but keep everything in the range 0-12096
            return 12096 - (self.stats.speed * modifier)

        return self.stats.speed * modifier

    def get_accuracy(self):
        modifier = dex.accuracy[self.boosts['accuracy']]
        return modifier

    def get_evasion(self):
        modifier = dex.evasion[self.boosts['evasion']]
        return modifier

    def calculate_stats(self):
        # hp
        hp = math.floor(( (self.pokemon_set['ivs'].hp + (2 * self.template.baseStats.hp) + (self.pokemon_set['evs'].hp/4) ) * (self.level/100) ) + 10 + self.level )

        stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
        cal = []
        for stat in stats:
            # other stat calculation
            cal.append(math.floor(math.floor((((getattr(self.pokemon_set['ivs'],stat) + (2 * getattr(self.template.baseStats, stat)) + (getattr(self.pokemon_set['evs'],stat)/4) ) * (self.level/100) ) + 5)) * dex.nature_dex[self.nature].values[stat] ))

        self.stats = dex.Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])

    def faint(self):
        self.hp = 0
        self.fainted = True
        self.side.pokemon_left -= 1
