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


# packed str format:
# name|species|item|ability|moves|nature|evs|gender|ivs|shiny|level|happiness]
# we will not allow empty fields
@dataclass
class PokemonSet:
    '''
    This class is all the info about a pokemon prior to battle start.
    This is the 'set' the player is running for this pokemon.
    '''
    name : str 
    species : str
    item : str
    ability : str
    moves : List[str]
    nature : str = 'hardy'
    evs : Tuple[int, int, int, int, int, int]= (0, 0, 0, 0, 0, 0)
    gender : str = ''
    ivs : Tuple[int, int, int, int, int, int] = (31, 31, 31, 31, 31, 31)
    shiny : bool = False
    level : int = 50 
    happiness : int = field(init=False)

    def __post_init__(self):
        if 'frustration' in self.moves:
            self.happiness = 0
        else:
            self.happiness = 255

TeamSet = List[PokemonSet]

@dataclass
class Decision:
    type : str
    selection : int
    target : str = 'foe0'
    mega : bool = False
    zmove : bool = False

    def __repr__(self):
        return self.type + ' ' + str(self.selection)

@dataclass
class Stats:
    '''
    Simple container class to reference the fields by name instead of 
    index.
    '''
    hp : int
    attack : int
    defense : int
    specialattack : int
    specialdefense : int
    speed : int

@dataclass
class Action:
    '''
    These are basically like 'events' that the battle creates
    and then executes in the correct order.
    
    When both players have made decisions, the engine creates all
    'actions' that will take place that turn and then updates
    the battle, pokemon, flags for each action.
    '''
    # action_type is 'move', 'switch', or 'mega'
    action_type : str 
    user : Any = field(repr=False, default=None) #pointer to Pokemon
    move : Any = field(repr=False, default=None) #move class from dex.py
    pos : int = None #pos for switch action
    target : str = 'foe0'
    
    def __repr__(self):
        return '(' + self.action_type + ' action)'

# dont think this works
def packed_str_to_pokemon_set(packed : str) -> PokemonSet:
    a = packed.split('|')
    m = a[4].split(',')
    e = a[6].split(',')
    i = a[8].split(',')
    poke = PokemonSet(a[0], a[1], a[2], a[3], m, a[5], e, a[7], i, a[9], a[10], a[11])

def dict_to_team_set(in_team : List) -> List[PokemonSet]:
    team = []
    for in_poke in in_team:
        name = in_poke['species']
        species = in_poke['species']
        moves = in_poke['moves']
        item = in_poke['item']
        nature = in_poke['nature']
        ability = in_poke['ability']
        evs = in_poke['evs']
        ivs = in_poke['ivs']
        poke = PokemonSet(name, species, item, ability, moves, nature, evs, gender='', ivs=ivs)
        team.append(poke)
    return team
