import dex as Dex
import random
import math
import re
from collections import namedtuple
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')

class Pokemon:
    def __init__(self, pokemonSet, sideNum, side=None, battle=None):
        self.sideNum = sideNum
        self.side = side
        self.battle = battle

        self.pokemonSet = pokemonSet

        self.species = re.sub(r'\W+', '', pokemonSet['species'].lower())

        self.nature = self.pokemonSet.get('nature', 'hardy')

        self.template = Dex.pokemon[self.species]

        self.name = pokemonSet.get('name', self.template.species)

        self.moves = pokemonSet['moves']
        self.baseMoves = self.moves
        #self.movepp = {}

        #self.trapped = False
        #self.maybeTrapped = False
        #self.maybeDisable = False
        #self.illusion = None
        self.fainted = False
        #self.faintQueued = False
        #self.lastItem = ''
        #self.ateBerry = False
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
        self.volatileStatuses = set()
        
        #self.lastMove = ''
        #self.moveThisTurn = ''

        #self.lastDamage = 0
        #self.lastAttackedBy = None
        #self.usedItemThisTurn = False
        #self.newlySwitched = False
        #self.beingCalledBack = False
        self.active = False
        #self.activeTurns = 0

        #self.isStarted = False
        #self.transformed = False
        #self.duringMove = False
        #self.speed = 0
        #self.abilityOrder = 0

        self.level = pokemonSet.get('level', 50)

        #self.gender = 'N'

        #self.statusData = {}
        #self.volatiles = {}


        self.baseAbility = self.pokemonSet.get('ability', self.template.abilities.normal0)
        self.baseAbility = re.sub(r'\W+', '', self.baseAbility.lower())
        self.ability = self.baseAbility
        self.item = pokemonSet.get('item', None)

        self.types = self.template.types
        #self.addedType = ''
        #self.knownType = True

        if 'evs' not in pokemonSet:
            self.pokemonSet['evs'] = Stats(0, 0, 0, 0, 0, 0)
        if 'ivs' not in pokemonSet:
            self.pokemonSet['ivs'] = Stats(31, 31, 31, 31, 31, 31)

#        self.set['boosts'] = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0}
#        self.set['stats'] = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}


        self.calculateStats()
        self.hp = self.stats.hp
        self.maxhp = self.hp


    def __str__(self):
        return self.name + '|' + str(self.nature) + '|' + str(self.ability) +  '|' + str(self.level) + '|' + str(self.status) + '|'+ 'hp' + str(self.hp) 

    def calculateStats(self):
#       hp
        hp = math.floor(( (self.pokemonSet['ivs'].hp + (2 * self.template.baseStats.hp) + (self.pokemonSet['evs'].hp/4) ) * (self.level/100) ) + 10 + self.level )

        stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
        cal = []
        for stat in stats:
            cal.append(math.floor((((getattr(self.pokemonSet['ivs'],stat) + (2 * getattr(self.template.baseStats, stat)) + (getattr(self.pokemonSet['evs'],stat)/4) ) * (self.level/100) ) + 5) * Dex.natures[self.nature].values[stat] ))

        self.stats = Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])


#        print(self.name, self.nature, self.pokemonSet['evs'], self.stats)

    def faint(self):
        self.hp = 0
        self.fainted = True
        self.side.pokemonLeft -= 1
    
