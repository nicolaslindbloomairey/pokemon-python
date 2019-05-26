from typing import List
from typing import Set
from typing import Dict
from typing import Tuple
from typing import Any
from typing import NewType
from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from data import dex
import math
import random
from new_sim.structs import *

# this class holds all data about a pokemon during battle
@dataclass
class Pokemon:
    player_uid : int # one indexed
    position : int
    poke : InitVar[PokemonSet] = None 
    packed : InitVar[str] = None

    id : str = ''
    name : str = ''
    species : str = ''
    nature : str = ''
    moves : List[str] = field(init=False)
    base_moves : List[str] = field(init=False)
    ability : str = ''
    base_ability : str = field(init=False)
    item : str = ''

    stats : Stats = field(init=False)
    hp : int = field(init=False)
    maxhp : int = field(init=False)

    lost_item : bool = False
    last_used_item : str = ''

    pp : Dict[str, int] = field(default_factory=dict)

    fainted : bool = False
    status : str = ''
    #burned : bool = False
    # counters for various status efects
    protect_n : int = 0
    toxic_n : int = 1
    sleep_n : int = 0
    bound_n : int = 0
    encore_n : int = 0
    perishsong_n : int = 0
    taunt_n : int = 0

    is_switching : bool = False
    trapped : bool = False
    aqua_ring : bool = False
    substitute : bool = False
    substitute_hp : int = 0
    stockpile : int = 0

    # move that most recently did damage to this pokemon
    last_damaging_move : str = ''
    last_used_move : str = None

    consecutive_move_uses : int = 0
    crit_chance : int = 0
    boosts : Dict[str, int] = field(init=False)
    volatile_statuses : Set[str] = field(default_factory=set)

    active : bool = False
    active_turns : int = 0

    level : int = 50

    types : List[str] = field(init=False)

    def __post_init__(self, poke, packed):
        if poke is None:
            poke = packed_str_to_pokemon_set(packed)
        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
        }
        self.name = poke.name
        self.species = poke.species
        self.id = poke.species
        self.item = poke.item
        self.ability = poke.ability
        self.base_ability = self.ability 
        self.moves = poke.moves
        self.base_moves = self.moves 
        self.nature = poke.nature

        self.stats = self.calculate_stats(poke.evs, poke.ivs)

        self.hp = self.stats.hp
        self.maxhp = self.stats.hp
        self.types = dex.pokedex[self.species].types

        for move in self.moves:
            self.pp[move] = dex.move_dex[move].pp

    def can_z(self, move):
        item = dex.item_dex[self.item]
        #if self.side.used_zmove:
        #    return False
        if item.zMoveType is not None and move.type != item.zMoveType:
            return False
        if item.zMoveUser is not None and self.name not in item.zMoveUser:
            return False
        if item.zMoveFrom is not None and move.name != item.zMoveFrom:
            return False
        return True

    def calculate_stats(self, evs, ivs) -> Stats:
        base_stats = dex.pokedex[self.species].baseStats
        # hp
        lvl = self.level
        iv = ivs[0] #hp iv
        ev = evs[0] #hp ev
        hp = math.floor(((iv + (2 * base_stats.hp) + (ev/4)) * (lvl/100)) + 10 + lvl)

        stats = ['attack', 'defense', 'specialattack', 'specialdefense', 'speed']
        cal = []
        i = 1
        for stat in stats:
            # other stat calculation
            base = getattr(base_stats, stat)
            iv = ivs[i]
            ev = evs[i]
            nature_mod = dex.nature_dex[self.nature].values[stat]
            cal.append(math.floor(math.floor((((iv + (2 * base) + (ev/4)) * (lvl/100)) + 5)) * nature_mod))
            i += 1

        return Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])

    def get_attack(self, crit=False) -> float:
        '''
        Returns modified attack stat.
        '''
        modifier = dex.boosts[self.boosts['atk']]
        if crit and modifier < 1:
            modifier = 1
        if self.ability == 'hugepower' or self.ability == 'purepower':
            modifier *= 2
        #if self.ability == 'flowergift' and self.battle.weather == 'sunny':
        #    modifier *= 2
        if self.ability == 'hustle':
            modifier *= 1.5
        if self.ability == 'guts' and self.status != '':
            modifier *= 1.5
        if self.ability == 'slowstart' and self.active_turns < 5:
            modifier = 0.5
        if self.ability == 'defeatist' and self.hp / self.stats.hp <= 0.5:
            modifier = 0.5
        if self.item == 'choiceband':
            modifier = 1.5
        if self.species == 'pikachu' and self.item == 'lightball':
            modifier = 2
        if (self.species == 'cubone' or self.species == 'marowak') and self.item == 'thickclub':
            modifier = 2
        return self.stats.attack * modifier

    def get_defense(self, crit) -> float:
        '''
        Returns modified defense stat.
        '''
        modifier = dex.boosts[self.boosts['def']]
        if crit and modifier > 1:
            modifier = 1
        if self.ability == 'marvelscale' and self.status != '':
            modifier *= 1.5
        #if self.ability == 'grasspelt' and self.battle.terrain == 'grassy':
        #    modifier *= 1.5
        if self.species == 'ditto' and self.item == 'metalpowder':
            modifier = 2
        #if self.template.evos is not None and self.item == 'eviolite':
        #    modifier = 1.5
        return self.stats.defense * modifier

    def get_specialattack(self, crit) -> float:
        '''
        Returns modified special attack stat.
        '''
        modifier = dex.boosts[self.boosts['spa']]
        if crit and modifier < 1:
            modifier = 1
        #if self.ability == 'solarpower' and self.battle.weather == 'sunny':
        #    modifier *= 1.5
        if self.ability == 'defeatist' and self.hp / self.stats.hp <= 0.5:
            modifier = 0.5
        if self.item == 'choicespecs':
            modifier = 1.5
        if self.species == 'pikachu' and self.item == 'lightball':
            modifier = 2
        if self.species == 'clamperl' and self.item == 'deepseatooth':
            modifier = 2
        return self.stats.specialattack * modifier

    def get_specialdefense(self, crit) -> float:
        '''
        Returns modified special defense stat.
        '''
        modifier = dex.boosts[self.boosts['spd']]
        if crit and modifier > 1:
            modifier = 1
        #if self.ability == 'flowergift' and self.battle.weather == 'sunny':
        #    modifier *= 2
        #if 'Rock' in self.types and self.battle.weather == 'sandstorm':
        #    modifier *= 1.5
        if self.item == 'assaultvest':
            modifier *= 1.5
        if self.species == 'clamperl' and self.item == 'deepseascale':
            modifier = 2
        #if self.template.evos is not None and self.item == 'eviolite':
        #    modifier = 1.5
        return self.stats.specialdefense * modifier

    def get_speed(self) -> float:
        '''
        Returns modified speed stat.
        '''
        modifier = dex.boosts[self.boosts['spe']]
        if self.status == 'par' and self.ability != 'quickfeet':
            modifier *= 0.5
        if self.item == 'choicescarf':
            modifier *= 1.5
        if self.item in ['ironball', 'machobrace', 'powerbracer', 'powerbelt', 'powerlens', 'powerband', 'poweranklet', 'powerweight']:
            modifier *= 0.5
        #if 'tailwind' in self.side.volatile_statuses:
        #    modifier *= 2.0
        if self.species == 'ditto' and self.item == 'quickpowder':
            modifier = 2
        #if self.ability == 'swiftswim' and self.battle.weather == 'rainy':
        #    modifier *= 2
        #if self.ability == 'chlorophyll' and self.battle.weather == 'sunny':
        #    modifier *= 2
        #if self.ability == 'sandrush' and self.battle.weather == 'sandstorm':
        #    modifier *= 2
        #if self.ability == 'slushrush' and self.battle.weather == 'hail':
        #    modifier *= 2
        if self.ability == 'unburden' and self.lost_item:
            modifier *= 2
        #if self.ability == 'surgesurfer' and self.battle.terrain == 'electric':
        #    modifier *= 2
        if self.ability == 'quickfeet' and self.status != '':
            modifier *= 1.5
        if self.ability == 'slowstart' and self.active_turns < 5:
            modifier *= 0.5
        #if self.battle.trickroom:
            # this is effectively the negative
            # invert the order but keep everything in the range 0-12096
        #    return 12096 - (self.stats.speed * modifier)

        return self.stats.speed * modifier

    def get_accuracy(self) -> float:
        '''
        Returns modified accuracy stat.
        '''
        modifier = dex.accuracy[self.boosts['accuracy']]
        return modifier

    def get_evasion(self) -> float:
        '''
        Returns modified evasion stat.
        '''
        modifier = dex.evasion[self.boosts['evasion']]
        return modifier

    def damage(self, amount : int, flag : str =None) -> int:
        '''
        Does damage equal to 'amount'. If amount is negative, this method
        heals the pokemon.
        'flag' tells us how to damage/heal the pokemon

        Returns the number of hit points healed/damaged.
        '''
        old_hp = self.hp
        if self.fainted:
            return 0
        if flag is None:
            self.hp -= math.floor(amount)
        elif flag == 'percentmax':
            damage = math.floor(self.stats.hp*amount)
            self.hp -= damage
        elif flag == 'percentmaxhp':
            damage = math.floor(self.stats.hp*amount)
            self.hp -= damage
        elif flag == 'percentcurrent':
            damage = math.floor(self.hp*amount)
            self.hp -= damage

        if 'endure' in self.volatile_statuses and self.hp < 1:
            self.hp = 1
            #self.battle.log(self.name + ' endured with 1 hp')
        if self.hp > self.stats.hp:
            self.hp = self.stats.hp

        diff_hp = old_hp - self.hp
        #if diff_hp > 0:
            #self.battle.log(self.name + ' took ' + str(diff_hp) + ' dmg')
        #elif diff_hp < 0:
            #self.battle.log(self.name + ' healed ' + str(-(diff_hp)) + ' hp')

        if self.hp <= 0:
            self.faint()
        return diff_hp

    def faint(self) -> None:
        '''
        Faints the pokemon. Removes statuses. Sets hp to 0.
        '''
        self.volatile_statuses = set()
        self.status = ''
        self.trapped = False
        self.hp = 0
        self.fainted = True
        #self.side.pokemon_left -= 1

        print(self.name + ' fainted')
        return

    def add_status(self, status, source=None):
        if self.status != '':
            return False
        if status is None:
            return False
        #print(self.name + self.ability)

        if status == 'brn' and ('Fire' in self.types or dex.ability_dex[self.ability].prevent_burn):
            return False
        if status == 'par' and ('Electric' in self.types or dex.ability_dex[self.ability].prevent_par):
            return False
        if (status == 'psn' or status == 'tox') and ('Poison' in self.types or 'Steel' in self.types):
            if source is not None and source.ability == 'corrosion':
                pass
            else:
                return False
        if (status == 'psn' or status == 'tox') and dex.ability_dex[self.ability].prevent_psn:
            return False
        if status == 'slp' and dex.ability_dex[self.ability].prevent_slp:
            return False

        if status == 'slp':
            self.sleep_n = random.randint(1, 3)


        self.status = status
        return True

    def boost(self, boosts):
        if boosts is None:
            return
        for stat in boosts:
            self.boosts[stat] += boosts[stat]
            if self.boosts[stat] > 6:
                self.boosts[stat] = 6
            if self.boosts[stat] < -6:
                self.boosts[stat] = -6

    def cure_status(self) -> bool:
        '''
        Handles updates when status is cured
        eg. toxic number reset
        '''
        if self.status == '':
            return False
        self.toxic_n = 1
        self.status = ''
        return True

    def mega_evolve(self) -> None:
        '''
        If the pokemon's current item is its mega stone, mega evolve.
        Else, return doing nothing.
        '''
        if self.item == '': # no item
            return
        if not dex.item_dex[self.item].megaStone: # not a megastone
            return
        stone = re.sub(r'\W+', '', dex.item_dex[self.item].megaEvolves.lower())
        if stone != self.species: # not right megastone
            return

        # overwrite the current pokemon with the mega form
        mega = re.sub(r'\W+', '', dex.item_dex[self.item].megaStone.lower())
        self.species = mega
        self.template = dex.pokedex[self.species]
        self.base_ability = self.template.abilities.normal0
        self.base_ability = re.sub(r'\W+', '', self.base_ability.lower())
        self.ability = self.base_ability
        self.types = self.template.types
        self.calculate_stats()
        self.hp = self.stats.hp
        return
