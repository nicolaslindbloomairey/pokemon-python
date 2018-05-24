import json
import time
from collections import namedtuple
import random
import re


#this module is for searching the dex, aka all the game data

#missing statuses, scripts, rulesets(formats), formatsdata( event pokemon and thespeed move_dex), aliases

with open('data/abilities.json') as f:
    abilities_raw_data = json.load(f)
with open('data/formats.json') as f:
    formats_raw_data = json.load(f)
with open('data/items.json') as f:
    items_raw_data = json.load(f)
with open('data/moves.json') as f:
    moves_raw_data = json.load(f)
with open('data/pokedex.json') as f:
    pokemon_raw_data = json.load(f)
with open('data/typechart.json') as f:
    typecharts_raw_data = json.load(f)
with open('data/natures.json') as f:
    natures_raw_data = json.load(f)


class Decision(namedtuple('Decision', ['type', 'selection', 'mega', 'zmove'])):
    def __new__(cls, type, selection, mega=False, zmove=False):
        return super(Decision, cls).__new__(cls, type, selection, mega, zmove)
        
class Action(namedtuple('Action', ['user', 'move', 'target', 'zmove', 'base_move'])):
    def __new__(cls, user, move, target=None, zmove=False, base_move=None):
        return super(Action, cls).__new__(cls, user, move, target, zmove, base_move)

#-------------
#POKEDEX
#-------------

pokemonAttributes = ['id', 'num', 'species', 'baseSpecies', 'forme', 'formeLetter', 'types', 
                        'genderRatio', 'baseStats', 'abilities', 'heightm', 'weightkg', 'color',
                        'prevo', 'evos', 'evoLevel', 'eggGroups', 'otherFormes', 'tier', 'requiredItem']
pokedex = {}

Pokemon = namedtuple('Pokemon', pokemonAttributes)
GenderRatio = namedtuple('GenderRatio', 'male female')
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')
BaseAbilities = namedtuple('BaseAbilities', 'normal0 normal1 hidden')

for i in pokemon_raw_data:
    for a in pokemonAttributes:
        if a not in pokemon_raw_data[i]:
            pokemon_raw_data[i][a] = None
        else:
            if a == 'genderRatio':
                pokemon_raw_data[i][a] = GenderRatio(pokemon_raw_data[i][a]['M'], pokemon_raw_data[i][a]['F'])
            elif a == 'baseStats':
                pokemon_raw_data[i][a] = Stats(pokemon_raw_data[i][a]['hp'], pokemon_raw_data[i][a]['atk'], pokemon_raw_data[i][a]['def'], pokemon_raw_data[i][a]['spa'],  pokemon_raw_data[i][a]['spd'], pokemon_raw_data[i][a]['spe'])
            elif a == 'abilities':
                pokemon_raw_data[i][a] = BaseAbilities(pokemon_raw_data[i][a].get('0'), pokemon_raw_data[i][a].get('1'), pokemon_raw_data[i][a].get('H'))

    pokemon_raw_data[i]['id'] = i

    pokedex[i] = Pokemon._make([pokemon_raw_data[i][j] for j in pokemonAttributes])


#------------
#ABILITIES
#------------
abilityAttributes = ['id', 'desc', 'shortDesc', 'name', 'rating', 'num', 'prevent_burn', 'prevent_par', 'prevent_slp', 'prevent_psn'] 
ability_dex = {}

Ability = namedtuple('Ability', abilityAttributes) #way more props, supressweather, onmodifymovepriority, onbasepowerpriority

for i in abilities_raw_data:
    for a in abilityAttributes:
        if a not in abilities_raw_data[i]:
            abilities_raw_data[i][a] = None

    ability_dex[i] = Ability._make([abilities_raw_data[i][j] for j in abilityAttributes])


#---------
#Format
#---------
formatAttributes = ['id', 'name', 'desc', 'mod', 'gameType', 'forcedLevel', 'teamLength', 'timer', 'ruleset', 'banlist'] 
format_dex = {}

Format = namedtuple('Format', formatAttributes)
TeamLength = namedtuple('TeamLength', 'validate battle')
Timer = namedtuple('Timer', 'starting perTurn maxPerTurn maxFirstTurn timeoutAutoChoose')

for i in formats_raw_data:
    for a in formatAttributes:
        if a not in formats_raw_data[i]:
            formats_raw_data[i][a] = None
        else:
            if a == 'teamLength':
                formats_raw_data[i][a] = TeamLength(formats_raw_data[i][a]['validate'], formats_raw_data[i][a]['battle'])
            elif a == 'timer':
                formats_raw_data[i][a] = Timer(formats_raw_data[i][a]['starting'], formats_raw_data[i][a]['perTurn'], formats_raw_data[i][a]['maxPerTurn'], formats_raw_data[i][a]['maxFirstTurn'],  formats_raw_data[i][a]['timeoutAutoChoose'])

    formats_raw_data[i]['id'] = i

    format_dex[i] = Format._make([formats_raw_data[i][j] for j in formatAttributes])

#--------
#items_raw_data
#---------

itemAttributes = ['id', 'name', 'spritenum', 'isBerry', 'naturalGift', 'zMove', 'zMoveFrom', 'zMoveUser', 'zMoveType', 'megaStone', 'megaEvolves', 'num', 'gen', 'desc']
item_dex = {}

Item = namedtuple('Item', itemAttributes) #some missing props

for i in items_raw_data:
    for a in itemAttributes:
        if a not in items_raw_data[i]:
            items_raw_data[i][a] = None

    item_dex[i] = Item._make([items_raw_data[i][j] for j in itemAttributes])


#--------
#moves_raw_data
#---------

move_attributes = ['num', 'accuracy', 'category', 'desc', 'id', 'name', 'pp',
                   'priority', 'flags', 'type', 'terrain', 'crit_ratio',
                   'ignore_accuracy', 'weather', 'drain', 'heal', 'recoil',
                   'target_type', 'base_power', 'short_desc', 'ignore_ability',
                   'ignore_defensive', 'ignore_evasion', 'ignore_immunity', 
                   'breaks_protect', 'defensive_category', 'force_switch', 
                   'future_move', 'unreleased', 'viable', 'multi_hit',
                   'no_faint', 'no_pp_boosts', 'no_sketch', 'pseudo_weather',
                   'thaws_target', 'self_switch', 'side_condition', 'sleep_usable',
                   'true_damage', 'primary', 'secondary', 'z_move']
flags = ['pulse', 'bullet', 'sound', 'powder', 'authentic', 'nonsky', 'distance',
         'dance', 'mystery', 'protect', 'snatch', 'recharge', 'gravity', 'mirror',
         'contact', 'punch', 'defrost', 'charge', 'bite', 'reflectable', 'heal']
recoil_attributes = ['damage', 'type', 'condition']
z_move = ['boosts', 'crystal', 'effect', 'base_power']
move_dex = {}

Move = namedtuple('Move', move_attributes) #some missing props
Flags = namedtuple('Flags', flags)
Recoil = namedtuple('Recoil', recoil_attributes)
ZMove = namedtuple('ZMove', z_move)
        
for move in moves_raw_data:
    moves_raw_data[move]['flags'] = Flags._make([moves_raw_data[move]['flags'][flag] for flag in flags])
    moves_raw_data[move]['recoil'] = Recoil._make([moves_raw_data[move]['recoil'][attribute] for attribute in recoil_attributes])
    moves_raw_data[move]['z_move'] = ZMove._make([moves_raw_data[move]['z_move'][attribute] for attribute in z_move])
    move_dex[move] = Move._make([moves_raw_data[move][attribute] for attribute in move_attributes])

zmove_chart = {
    'normaliumz': 'breakneckblitz',
    'fightiniumz': 'alloutpummeling',
    'flyiniumz': 'supersonicskystrike',
    'poisoniumz': 'aciddownpour',
    'groundiumz': 'tectonicrage',
    'rockiumz': 'continentalcrush',
    'buginiumz': 'savagespinout',
    'ghostiumz': 'neverendingnightmare',
    'steeliumz': 'corkscrewcrash',
    'firiumz': 'infernooverdrive',
    'wateriumz': 'hydrovortex',
    'grassiumz': 'bloomdoom',
    'electriumz': 'gigavolthavoc',
    'psychiumz': 'shatteredpsyche',
    'iciumz': 'subzeroslammer',
    'dragoniumz': 'devastatingdrake',
    'darkiniumz': 'blackholeeclipse',
    'fariumz': 'twinkletackle'
}

#--------
#TypeChart
#---------

typechartAttributes = ['damage_taken', 'HPivs']
damagetakenAttributes = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

typechart_dex = {}

TypeChart = namedtuple('TypeChart', typechartAttributes)
DamageTaken = namedtuple('DamageTaken', 'prankster par brn trapped powder sandstorm hail frz psn tox Bug Dark Dragon Electric Fairy Fighting Fire Flying Ghost Grass Ground Ice Normal Poison Psychic Rock Steel Water')

for i in typecharts_raw_data:
    for a in typechartAttributes:
        if a not in typecharts_raw_data[i]:
            typecharts_raw_data[i][a] = None
#        else:
#            if a == 'damage_taken':
#                for y in damagetakenAttributes:
#                    if y not in typecharts_raw_data[i][a]:
#                        typecharts_raw_data[i][a][y] = None
#                typecharts_raw_data[i][a] = DamageTaken._make([typecharts_raw_data[i][a][j] for j in damagetakenAttributes])

    typechart_dex[i] = TypeChart._make([typecharts_raw_data[i][j] for j in typechartAttributes])


#--------
#natures_raw_data
#---------
natureAttributes = ['id', 'name', 'plus', 'minus']
nature_dex = {}

temp = ['id', 'name', 'plus', 'minus', 'values']
Nature = namedtuple('Nature', temp)

for i in natures_raw_data:
    for a in natureAttributes:
        if a not in natures_raw_data[i]:
            natures_raw_data[i][a] = None

    args = [natures_raw_data[i][j] for j in natureAttributes]

    values = {}
    stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
    for stat in stats:
        if args[2] == stat:
            values[stat] = 1.1
        elif args[3] == stat:
            values[stat] = 0.9
        else:
            values[stat] = 1
    args.append(values)

    nature_dex[i] = Nature._make(args)


#---------------------
#ACCURACY AND BOOSTS
#---------------------

accuracy = {
    -6: 0.333,
    -5: 0.375,
    -4: 0.430,
    -3: 0.500,
    -2: 0.600,
    -1: 0.750,
    0: 1.000,
    1: 1.3333,
    2: 1.6667,
    3: 2.000,
    4: 2.3333,
    5: 2.6667,
    6: 3.000,
}

evasion = {
    6: 0.333,
    5: 0.375,
    4: 0.430,
    3: 0.500,
    2: 0.600,
    1: 0.750,
    0: 1.000,
    -1: 1.3333,
    -2: 1.6667,
    -3: 2.000,
    -4: 2.3333,
    -5: 2.6667,
    -6: 3.000,
}

boosts = {
    -6: 0.25,
    -5: 0.28,
    -4: 0.33,
    -3: 0.40,
    -2: 0.50,
    -1: 0.66,
    0: 1.0,
    1: 1.5,
    2: 2.0,
    3: 2.5,
    4: 3.0,
    5: 3.5,
    6: 4.0,
}

crit = {
    0: 1/24,
    1: 1/8,
    2: 1/2,
    3: 1
}
no_metronome = {
    "afteryou",
    "assist",
    "belch",
    "bestow",
    "celebrate",
    "chatter",
    "copycat",
    "counter",
    "covet",
    "craftyshield",
    "destinybond",
    "detect",
    "diamondstorm",
    "dragonascent",
    "endure",
    "feint",
    "focuspunch",
    "followme",
    "freezeshock",
    "happyhour",
    "helpinghand",
    "holdhands",
    "hyperspacefury",
    "hyperspacehole",
    "iceburn",
    "kingsshield",
    "lightofruin",
    "matblock",
    "mefirst",
    "metronome",
    "mimic",
    "mirrorcoat",
    "mirrormove",
    "naturepower",
    "originpulse",
    "precipiceblades",
    "protect",
    "quash",
    "quickguard",
    "ragepowder",
    "relicsong",
    "secretsword",
    "sketch",
    "sleeptalk",
    "snarl",
    "snatch",
    "snore",
    "spikyshield",
    "steameruption",
    "struggle",
    "switcheroo",
    "technoblast",
    "thief",
    "thousandarrows",
    "thousandwaves",
    "transform",
    "trick",
    "vcreate",
    "wideguard"
}

# i shouldn't be using this, instead, i should be using the info in items.json
fling = {
    'flameorb': 30,
    'kingsrock': 30,
    'lightball': 30,
    'mentalherb': 10,
    'poisonbarb': 70,
    'razorfang': 30,
    'toxicorb': 30,
    'whiteherb': 10,
    'ironball': 130,
    'hardstone': 100,
    'rarebone': 100,
}

magnitude_power = [10, 30, 30, 50, 50, 50, 50, 70, 70, 70, 70, 70, 70, 90, 90, 90, 90, 110, 110, 150]
