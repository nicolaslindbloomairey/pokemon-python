'''
Nicolas Lindbloom-Airey

structs.py

This file defines all the data containers for the simulator. It also contains
a handful of functions at the bottom to help with initialization of these
containers. I use pythons dataclass decorator which lets me write less
source code when defining a data class. These data class have no methods.

Data Classes:
    PokemonSet
    TeamSet => List[PokemonSet]
    Decision
    Stats
    Action
    Pokemon
    Player

Functions:
    dict_to_team_set
    calculate_stats 
    get_active_pokemon
'''
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

# this class holds all data about a pokemon during battle
@dataclass
class Pokemon:
    player_uid : int # one indexed
    position : int
    poke : InitVar[PokemonSet] = None 
    packed : InitVar[str] = None
    debug : bool = False

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

        self.stats = calculate_stats(self, poke.evs, poke.ivs)

        self.hp = self.stats.hp
        self.maxhp = self.stats.hp
        self.types = dex.pokedex[self.species].types

        for move in self.moves:
            self.pp[move] = dex.move_dex[move].pp
        return

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

    spikes : int - number of spike layers
    toxic_spikes : int - number of toxic spike layers, independent of spikes
    stealth_rock : bool - is stealth rock up
    sticky_web : bool - is sticky web up
    tailwind : bool - is tailwind active
    tailwind_n : int - turns left for tailwind
    '''

    name : str
    uid : int # one indexed
    team : InitVar[List[PokemonSet]] = None
    debug : bool = False

    pokemon : List[Pokemon] = field(repr=False, default_factory=list)
    bench : List[Pokemon] = field(repr=False, default_factory=list)
    active_pokemon : List[Pokemon] = field(repr=False, default_factory=list)

    #pokemon_left : int = 0
    # old field conditions
    volatile_statuses : Set[str] = field(default_factory=set)
    side_conditions : Set[str] = field(default_factory=set)

    # new field conditions
    spikes : int = 0
    toxic_spikes : int = 0
    stealth_rock : bool = False
    sticky_web : bool = False
    tailwind : bool = False
    tailwind_n : int = 0 

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

    def __post_init__(self, team:List[PokemonSet]):
        i = 0
        for poke in team:
            pokemon = Pokemon(self.uid, i, poke, debug=self.debug)
            self.pokemon.append(pokemon) 
            i += 1 
        return

@dataclass
class Battle:
    '''
    Contains all info related to this pokemon battle

    FIELDS:
    turn : int - The turn counter. Increments in turn_start()
    pseudo_turn : bool - Pseudo turns are for when a pokemon faints and
        new pokemon switch in, we still use the action queue because the 
        order of the pokemon switching in matters.
    doubles : bool - Not using this rn?
    rng : bool - Some random numbers are rigged if rng is False.
    debug : bool - Not using this either.
    p1 : Player - pointer to player 1 object
    p2 : Player - pointer to player 2 object
    weather : str - what weather is currently on the field, options are as
        follows, {clear, sunlight, heavy_sunlight, rain, heavy_rain,
        sandstorm, hail, wind}
    weather_n : int - how many turns are left for the weather
    terrain : str - what terrain is currently on the field, options are,
        {grassy, electric, psychic...
    trickroom : bool - Is trickroom in effect? This flag lasts for 5 turns.
    trickroom_n : int - how many turns are left for trickroom
    started : bool - has the battle started
    ended : bool - is the battle over
    winner : str - who won
    setup_ran : bool - has the set up method run yet

    '''

    format_str : InitVar[str] = 'single'
    name1 : InitVar[str] = 'Nic'
    name2 : InitVar[str] = 'Sam'
    team1 : InitVar[List[PokemonSet]] = None
    team2 : InitVar[List[PokemonSet]] = None
    debug : bool = False

    #maintenance variables
    turn : int = 0
    pseudo_turn : bool = False
    doubles : bool = False
    rng : bool = True
    winner : str = None
    ended : bool = False
    started : bool = False
    setup_ran : bool = False
    log : List[str] = field(default_factory=list)

    # players
    p1 : Player = field(init=False)
    p2 : Player = field(init=False)
    # should i have a map of player ids to player objects?

    # game field effects
    weather : str = 'clear'
    weather_n : int = 0
    terrain : str = ''
    trickroom : bool = False
    trickroom_n : int = 0

    def __post_init__(self, format_str, name1, team1, name2, team2,):
        if format_str == 'double':
            self.doubles = True
        self.p1 = Player(name1, 1 , team1, debug=self.debug)
        self.p2 = Player(name2, 2 , team2, debug=self.debug)

        self.set_up()
        return

    def set_up(self):
        self.p1.active_pokemon.append(self.p1.pokemon[0])
        self.p2.active_pokemon.append(self.p2.pokemon[0])
        for i in range(len(self.p1.pokemon)-1):
            self.p1.bench.append(self.p1.pokemon[i+1])

        for i in range(len(self.p2.pokemon)-1):
            self.p2.bench.append(self.p2.pokemon[i+1])

        self.setup_ran = True
        return

'''
HELPER FUNCTIONS FOR STRUCTS
'''

def get_active_pokemon(B:Battle) -> List[Pokemon]:
    '''
    Returns a list of pointers to all the active pokemon in this battle
    '''
    active = []
    for pokemon in B.p1.active_pokemon:
        active.append(pokemon)
    for pokemon in B.p2.active_pokemon:
        active.append(pokemon)
    return active

# dont think this works
def packed_str_to_pokemon_set(packed : str) -> PokemonSet:
    a = packed.split('|')
    m = a[4].split(',')
    e = a[6].split(',')
    i = a[8].split(',')
    poke = PokemonSet(a[0], a[1], a[2], a[3], m, a[5], e, a[7], i, a[9], a[10], a[11])

def dict_to_team_set(in_team : List) -> List[PokemonSet]:
    '''
    Takes dict format of pokemon sets and returns a list of PokemonSets
    '''
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

def calculate_stats(P:Pokemon, evs:List[int], ivs:List[int]) -> Stats:
    '''
    Called in init of a pokemon so it must be defined here.
    Also called in mega_evolve()
    '''
    base_stats = dex.pokedex[P.species].baseStats
    # hp
    lvl = P.level
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
        nature_mod = dex.nature_dex[P.nature].values[stat]
        cal.append(math.floor(math.floor((((iv + (2 * base) + (ev/4)) * (lvl/100)) + 5)) * nature_mod))
        i += 1

    return Stats(hp, cal[0], cal[1], cal[2], cal[3], cal[4])
