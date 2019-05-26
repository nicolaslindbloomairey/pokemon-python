'''
Nicolas Lindbloom-Airey

pokemon.py

This file contains functions that are limited in scope to a single
pokemon for the most part. A large part of this file is the getter
functions for the stats. We need these because there are many modifiers
for a pokemon stats in battle. These modifiers change often.

FUNCTIONS:
    get_attack
    get_defense
    get_specialattack
    get_specialdefense
    get_speed
    get_accuracy
    get_evasion

    can_z
    damage
    faint
    add_status
    cure_status
    boost
    mega_evolve
'''
import random
from sim.structs import *


def get_attack(P:Pokemon, weather:str, crit:bool=False) -> float:
    '''
    Returns modified attack stat.
    Requires info about weather.
    '''
    modifier = dex.boosts[P.boosts['atk']]
    if crit and modifier < 1:
        modifier = 1
    if P.ability == 'hugepower' or P.ability == 'purepower':
        modifier *= 2
    if P.ability == 'flowergift' and weather == 'sunny':
        modifier *= 2
    if P.ability == 'hustle':
        modifier *= 1.5
    if P.ability == 'guts' and P.status != '':
        modifier *= 1.5
    if P.ability == 'slowstart' and P.active_turns < 5:
        modifier = 0.5
    if P.ability == 'defeatist' and P.hp / P.stats.hp <= 0.5:
        modifier = 0.5
    if P.item == 'choiceband':
        modifier = 1.5
    if P.species == 'pikachu' and P.item == 'lightball':
        modifier = 2
    if P.species in {'cubone', 'marowak'} and P.item == 'thickclub':
        modifier = 2
    return P.stats.attack * modifier

def get_defense(P:Pokemon, crit:bool, terrain:str) -> float:
    '''
    Returns modified defense stat.
    Requires info about terrain.
    '''
    modifier = dex.boosts[P.boosts['def']]
    if crit and modifier > 1:
        modifier = 1
    if P.ability == 'marvelscale' and P.status != '':
        modifier *= 1.5
    if P.ability == 'grasspelt' and terrain == 'grassy':
        modifier *= 1.5
    if P.species == 'ditto' and P.item == 'metalpowder':
        modifier = 2
    #if self.template.evos is not None and self.item == 'eviolite':
    #    modifier = 1.5
    return P.stats.defense * modifier

def get_specialattack(P:Pokemon, crit:bool, weather:str) -> float:
    '''
    Returns modified special attack stat.
    Requires info about weather.
    '''
    modifier = dex.boosts[P.boosts['spa']]
    if crit and modifier < 1:
        modifier = 1
    if P.ability == 'solarpower' and weather == 'sunny':
        modifier *= 1.5
    if P.ability == 'defeatist' and P.hp / P.stats.hp <= 0.5:
        modifier = 0.5
    if P.item == 'choicespecs':
        modifier = 1.5
    if P.species == 'pikachu' and P.item == 'lightball':
        modifier = 2
    if P.species == 'clamperl' and P.item == 'deepseatooth':
        modifier = 2
    return P.stats.specialattack * modifier

def get_specialdefense(P:Pokemon, crit:bool, weather:str) -> float:
    '''
    Returns modified special defense stat.

    Requires info about weather.
    '''
    modifier = dex.boosts[P.boosts['spd']]
    if crit and modifier > 1:
        modifier = 1
    if P.ability == 'flowergift' and weather == 'sunny':
        modifier *= 2
    if 'Rock' in P.types and weather == 'sandstorm':
        modifier *= 1.5
    if P.item == 'assaultvest':
        modifier *= 1.5
    if P.species == 'clamperl' and P.item == 'deepseascale':
        modifier = 2
    #if self.template.evos is not None and self.item == 'eviolite':
    #    modifier = 1.5
    return P.stats.specialdefense * modifier

def get_speed(P:Pokemon, weather:str, terrain:str, trickroom:bool,
                tailwind:bool) -> float:
    '''
    Returns modified speed stat.

    Requires info about battle weather, terrain, tailwind, and trickroom.
    '''
    modifier = dex.boosts[P.boosts['spe']]
    if P.status == 'par' and P.ability != 'quickfeet':
        modifier *= 0.5
    if P.item == 'choicescarf':
        modifier *= 1.5
    if P.item in ['ironball', 'machobrace', 'powerbracer', 'powerbelt', 'powerlens', 'powerband', 'poweranklet', 'powerweight']:
        modifier *= 0.5
    if tailwind:
        modifier *= 2.0
    if P.species == 'ditto' and P.item == 'quickpowder':
        modifier = 2
    if P.ability == 'swiftswim' and weather == 'rainy':
        modifier *= 2
    if P.ability == 'chlorophyll' and weather == 'sunny':
        modifier *= 2
    if P.ability == 'sandrush' and weather == 'sandstorm':
        modifier *= 2
    if P.ability == 'slushrush' and weather == 'hail':
        modifier *= 2
    if P.ability == 'unburden' and P.lost_item:
        modifier *= 2
    if P.ability == 'surgesurfer' and terrain == 'electric':
        modifier *= 2
    if P.ability == 'quickfeet' and P.status != '':
        modifier *= 1.5
    if P.ability == 'slowstart' and P.active_turns < 5:
        modifier *= 0.5
    # this is effectively the negative
    # invert the order but keep everything in the range 0-12096
    if trickroom:
        return 12096 - (P.stats.speed * modifier)

    return P.stats.speed * modifier

def get_accuracy(P:Pokemon) -> float:
    '''
    Returns modified accuracy stat.
    '''
    modifier = dex.accuracy[P.boosts['accuracy']]
    return modifier

def get_evasion(P:Pokemon) -> float:
    '''
    Returns modified evasion stat.
    '''
    modifier = dex.evasion[P.boosts['evasion']]
    return modifier

def can_z(P:Pokemon, move:dex.Move) -> bool:
    '''
    Returns true if this pokemon can use a z move.
    '''
    item = dex.item_dex[P.item]
    # check the move type is correct.
    if item.zMoveType is not None and move.type != item.zMoveType:
        return False
    # check the move user is correct.
    if item.zMoveUser is not None and P.name not in item.zMoveUser:
        return False
    # check if the move is correct.
    if item.zMoveFrom is not None and move.name != item.zMoveFrom:
        return False
    return True

def damage(P:Pokemon, dmg:int, flag:str=None) -> int:
    '''
    Does damage equal to 'dmg'. If amount is negative, this method
    heals the pokemon.
    'flag' tells us how to damage/heal the pokemon

    Returns the number of hit points healed/damaged.
    '''
    old_hp = P.hp
    if P.fainted:
        return 0

    if flag in {'percentmax', 'percentmaxhp'}:
        dmg *= P.stats.hp
    elif flag == 'percentcurrent':
        dmg *= P.hp

    P.hp -= math.floor(dmg)

    if 'endure' in P.volatile_statuses and P.hp < 1:
        P.hp = 1
        #self.battle.log(self.name + ' endured with 1 hp')
    if P.hp > P.stats.hp:
        P.hp = P.stats.hp

    diff_hp = old_hp - P.hp
    #if diff_hp > 0:
        #self.battle.log(self.name + ' took ' + str(diff_hp) + ' dmg')
    #elif diff_hp < 0:
        #self.battle.log(self.name + ' healed ' + str(-(diff_hp)) + ' hp')

    if P.hp <= 0:
        faint(P)
    return diff_hp

def faint(P:Pokemon) -> None:
    '''
    Faints the pokemon. Removes statuses. Sets hp to 0.
    '''
    P.volatile_statuses = set()
    P.status = ''
    P.trapped = False
    P.hp = 0
    P.fainted = True
    #self.side.pokemon_left -= 1

    if P.debug:
        print(P.name + ' fainted')
    return

def add_status(P:Pokemon, status:str, source:Pokemon=None):
    if P.status != '':
        return False
    if status is None:
        return False
    #print(self.name + self.ability)

    if status == 'brn' and ('Fire' in P.types or dex.ability_dex[P.ability].prevent_burn):
        return False
    if status == 'par' and ('Electric' in P.types or dex.ability_dex[P.ability].prevent_par):
        return False
    if (status == 'psn' or status == 'tox') and ('Poison' in P.types or 'Steel' in P.types):
        if source is not None and source.ability == 'corrosion':
            pass
        else:
            return False
    if (status == 'psn' or status == 'tox') and dex.ability_dex[P.ability].prevent_psn:
        return False
    if status == 'slp' and dex.ability_dex[P.ability].prevent_slp:
        return False

    if status == 'slp':
        P.sleep_n = random.randint(1, 3)


    P.status = status
    return True

def cure_status(P:Pokemon) -> bool:
    '''
    Handles updates when status is cured
    eg. toxic number reset

    Returns true if a status was cured. False otherwise.
    '''
    if P.status == '':
        return False
    P.toxic_n = 1
    P.status = ''
    return True

def boost(P:Pokemon, boosts:Dict[str, int]) -> None:
    if boosts is None:
        return
    for stat in boosts:
        P.boosts[stat] += boosts[stat]
        if P.boosts[stat] > 6:
            P.boosts[stat] = 6
        if P.boosts[stat] < -6:
            P.boosts[stat] = -6
    return

def mega_evolve(P:Pokemon) -> None:
    '''
    If the pokemon's current item is its mega stone, mega evolve.
    Else, return doing nothing.
    '''
    if P.item == '': # no item
        return
    if not dex.item_dex[P.item].megaStone: # not a megastone
        return
    stone = re.sub(r'\W+', '', dex.item_dex[P.item].megaEvolves.lower())
    if stone != P.species: # not right megastone
        return

    # overwrite the current pokemon with the mega form
    mega = re.sub(r'\W+', '', dex.item_dex[P.item].megaStone.lower())
    P.species = mega
    P.template = dex.pokedex[P.species]
    P.base_ability = P.template.abilities.normal0
    P.base_ability = re.sub(r'\W+', '', P.base_ability.lower())
    P.ability = P.base_ability
    P.types = P.template.types
    P.calculate_stats()
    P.hp = P.stats.hp
    return
    
