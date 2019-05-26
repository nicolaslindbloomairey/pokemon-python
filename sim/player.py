'''
Nicolas Lindbloom-Airey

player.py

This file has the logic that is limited in scope to a single player/side/team.
This is mainly the switch function when a pokemon is thrown out into battle.

FUNCTIONS:
    switch
    default_decide
    pokemon_left
'''
import sys
from sim.pokemon import *

def switch(T:Player, user:Pokemon, position:int) -> bool:
    '''
    switch the active pokemon to the pokemon in index: position

    PRE: the pokemon at position is to is not fainted or active
    we do this so we don't have switch and default switch call each other

    RETURNS true if we were able to do the switch, false if we couldn't
    '''
    if 'cantescape' in user.volatile_statuses and not user.fainted:
        return False
    if 'partiallytrapped' in user.volatile_statuses and not user.fainted and 'Ghost' not in user.types:
        return False

    if not pokemon_left(T):
        sys.exit('No pokemon left and we are switching')

    # if the selected pokemon is fainted or is already on the field do a default switch
    if T.pokemon[position].fainted or T.pokemon[position].active:
        for pokemon in T.bench:
            if not pokemon.fainted and not pokemon.active:
                position = pokemon.position
        sys.exit('No valid pokemon to switch to and yet we called switch()')

    pokemon_out = user
    pokemon_in = T.pokemon[position]

    #switch
    # update the sides active pokemon
    pos = T.active_pokemon.index(pokemon_out)
    T.active_pokemon[pos] = pokemon_in

    # update the battles active pokemon
    #pos = self.battle.active_pokemon.index(pokemon_out)
    #self.battle.active_pokemon[pos] = pokemon_in

    pokemon_in.active = True
    pokemon_out.is_switching = False
    pokemon_out.aqua_ring = False
    pokemon_out.volatile_statuses = set()

    T.boosts = {
        'atk': 0,
        'def': 0,
        'spa': 0,
        'spd': 0,
        'spe': 0,
        'accuracy': 0,
        'evasion': 0
    }
    
    if T.debug:
        print(pokemon_out.name + ' switches out for ' + pokemon_in.name)

    #self.battle.log(pokemon_out.fullname
    #      + ' switches out for '
    #      + pokemon_in.fullname)
    return True

def default_decide(T:Player) -> None:
    '''
    Manipulation of the player.choice attribute. This method simulates
    when a player runs out of time to make a decision.
    If the request is for a switch, switch to first non-fainted pokemon.
    If the request is a pass, pass. Player doesn't have a choice anyway.
    If the request is a move, pick a random move.
    '''
    n = len(T.active_pokemon)
    for i in range(n):

        if T.request == 'switch':
            for pokemon in T.pokemon:
                if pokemon.fainted == False:
                    T.choice = Decision('switch', pokemon.position)

        elif T.request == 'pass':
            T.choice = Decision('pass', 0)

        elif T.request == 'move':
            if len(T.active_pokemon[i].moves) > 0:
                rand_int = random.randint(0, len(T.active_pokemon[i].moves)-1)
                T.choice = Decision('move', rand_int)
            else:
                sys.exit('No moves!')
    return

def pokemon_left(player:Player) -> int:
    '''
    Counts and returns the number of non-fainted pokemon.
    '''
    left = 0
    for p in player.pokemon:
        if p.fainted == False:
            left += 1
    return left
