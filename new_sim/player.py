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
import sys

from new_sim.structs import *
from new_sim.pokemon import *

@dataclass
class Player:
    '''
    Player specific info and their pokemon in this struct

    FIELDS:
    name : str - player name
    uid : int - one indexed id value, 1 for player 1, 2 for player 2...
    pokemon : List[Pokemon] - List of pokemon objects that belong to this
        player.
    bench : List[Pokemon] - List of pokemon pointers that are not active
    active_pokemon : List[Pokemon] - List of pokemon pointers that are active
    volatile_statuses : Set[str] - i forget what volatile statuses the player
        can have.
    side_conditions : Set[str] - i forget what side conditions the player
        can have.
    request : str - the type of decision this player needs to make next
    choice : str - the type of decision this player has made for the current
        turn.
    used_zmove : bool - Has this player used their 1 zmove yet.
    '''

    name : str
    uid : int # one indexed
    team : InitVar[List[PokemonSet]] = None

    pokemon : List[Pokemon] = field(repr=False, default_factory=list)
    bench : List[Pokemon] = field(repr=False, default_factory=list)
    active_pokemon : List[Pokemon] = field(repr=False, default_factory=list)

    #pokemon_left : int = 0
    volatile_statuses : Set[str] = field(default_factory=set)
    side_conditions : Set[str] = field(default_factory=set)

    '''
    request[0] is for one active pokemon
    request[1] is for the next active pokemon
    current request is one of
    move - move request
    switch - fainted pokemon or for u-turn and what not
    teampreview - beginning of battle pick which pokemon
    '' - no request
    '''
    request : str = 'move'
    choice : Decision = None

    used_zmove : bool = False

    def __post_init__(self, team):
        i = 0
        for poke in team:
            pokemon = Pokemon(self.uid, i, poke)
            self.pokemon.append(pokemon) 
            i += 1 
        return

    # switch the active pokemon to the pokemon in index: position
    def switch(self, user, position):
        if 'cantescape' in user.volatile_statuses and not user.fainted:
            return False
        if 'partiallytrapped' in user.volatile_statuses and not user.fainted and 'Ghost' not in user.types:
            return False

        #if self.battle.doubles and self.pokemon_left == 1:
        #    self.active_pokemon.remove(user)
        #    self.battle.active_pokemon.remove(user)
        #    return

        # if the selected pokemon is fainted or is already on the field do a default switch
        if self.pokemon[position].fainted or self.pokemon[position].active:
            sys.exit('pokemon we are switching to is fainted or active')
            return self.default_switch(user)

        pokemon_out = user
        pokemon_in = self.pokemon[position]

        #switch
        # update the sides active pokemon
        pos = self.active_pokemon.index(pokemon_out)
        self.active_pokemon[pos] = pokemon_in

        # update the battles active pokemon
        #pos = self.battle.active_pokemon.index(pokemon_out)
        #self.battle.active_pokemon[pos] = pokemon_in

        pokemon_in.active = True
        pokemon_out.is_switching = False
        pokemon_out.aqua_ring = False
        pokemon_out.volatile_statuses = set()

        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
        }
        print(pokemon_out.name + ' switches out for ' + pokemon_in.name)

        #self.battle.log(pokemon_out.fullname
        #      + ' switches out for '
        #      + pokemon_in.fullname)
        return True

    # switch to the first non-fainted pokemon on your team
    def default_switch(self, user):
        if not pokemon_left(self):
            sys.exit('No pokemon left and we are switching')

        for pokemon in self.bench:
            if not pokemon.fainted and not pokemon.active:
                self.switch(user, pokemon.position)
                return True

    def default_decide(self):
        #n = 2 if self.battle.doubles else 1
        n = len(self.active_pokemon)
        for i in range(n):

            if self.request == 'switch':
                for pokemon in self.pokemon:
                    if pokemon.fainted == False:
                        self.choice = Decision('switch', pokemon.position)

            elif self.request == 'pass':
                self.choice = Decision('pass', 0)

            elif self.request == 'move':
                if len(self.active_pokemon[i].moves) > 0:
                    rand_int = random.randint(0, len(self.active_pokemon[i].moves)-1)
                    self.choice = Decision('move', rand_int)
                else:
                    sys.exit('No moves!')

def pokemon_left(player : Player) -> int:
    '''
    Returns the number of non-fainted pokemon.
    '''
    left = 0
    for p in player.pokemon:
        if p.fainted == False:
            left += 1
    return left
