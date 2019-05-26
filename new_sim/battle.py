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
import heapq
import sys
import random

from new_sim.structs import *
from new_sim.player import *
from new_sim.pokemon import *

MAX_TURNS = 500

@dataclass
class Battle:
    '''Contains all info related to this pokemon battle'''

    format_str : InitVar[str] = 'single'
    name1 : InitVar[str] = 'Nic'
    name2 : InitVar[str] = 'Sam'
    team1 : InitVar[List[PokemonSet]] = None
    team2 : InitVar[List[PokemonSet]] = None

    turn : int = 0
    pseudo_turn : bool = False
    doubles : bool = False
    rng : bool = True
    debug : bool = False
    p1 : Player = field(init=False)
    p2 : Player = field(init=False)
    # weather options - clear, sunlight, heavy_sunlight, rain, heavy_rain
    #                   , sandstorm, hail, wind
    weather : str = 'clear'
    # terrain options - grassy, elect...
    terrain : str = ''
    trickroom : bool = False
    winner : str = None
    ended : bool = False
    started : bool = False
    setup_ran : bool = False
    log : List[str] = field(default_factory=list)

    def __post_init__(self, format_str, name1, team1, name2, team2,):
        #print("hello")
        if format_str == 'double':
            self.doubles = True
        self.p1 = Player(name1, 1 , team1)
        self.p2 = Player(name2, 2 , team2)

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

    def choose(self, player_uid, choice):
        '''
        Sets the player's choice to the given choice.
        '''
        choice = choice.split(' ')
        c = Decision(choice[0], int(choice[1]))
        if player_uid == 1:
                self.p1.choice = c
        if player_uid == 2:
                self.p2.choice = c

    def run(self):
        '''
        Runs the Battle from start to finish as if each player ran out of time
        '''
        while not self.ended:
            self.p1.default_decide()
            self.p2.default_decide()
            self.do_turn()
            if self.turn > MAX_TURNS:
                sys.exit("Battle reached max number of allowed turns")
                break
        return

    def do_turn(self):
        '''
        To be called once both sides have made their decisions.
        Updates the game state according to the decisions. This method
        is the meat of the simulator, some of the logic is separated
        to other methods but the idea is as follows:

            * update fields that need updating before any 'actions' happen
            * build and then execute all 'actions' for the turn
            * update fields that need updating after all 'actions'
                eg. burn damage, weather...
            * check if someone won the game on this turn
            * update the request for new decisions from player/ai

        Note: Pseudo turns exist for when either player needs to throw out
        another pokemon due to fainting

        PRE: self.p1.choice is valid
        PRE: self.p2.choice is valid
        '''
        if self.p1.choice is None or self.p2.choice is None:
            sys.exit('BATTLE ERROR: one or more sides has invalid decision')


        self.turn_start()

        print('---Turn ' + str(self.turn) + '---')
        print(self.p1.choice)
        print(self.p2.choice)

        # create and populate action queue
        # elements of queue are in form (priority : int, action : Action)
        q : List[Tuple[float, Action]] = []
        for player in [self.p1,self.p2]:
            for i in range(len(player.active_pokemon)):
                poke = player.active_pokemon[i]
                choice = player.choice
                move = self.create_move(poke, choice)
                populate_action_queue(q, poke, choice, move)

        # run each each action in the queue
        print(q)
        print()
        while q:
            priority, next_action = heapq.heappop(q) 
            self.run_action(next_action)
        
        if not self.pseudo_turn:
            self.turn_end()

        #check for a winner
        if not pokemon_left(self.p1):
            self.ended = True
            self.winner = 'p2'
            print('p2 won')
        if not pokemon_left(self.p2):
            self.ended = True
            self.winner = 'p1'
            print('p1 won')

        #request the next turns move
        self.pseudo_turn = False
        self.request = 'move'
        self.p1.request = 'move'
        self.p2.request = 'move'
        #self.p1.request = ['move', 'move'] if self.doubles else ['move']
        #self.p2.request = ['move', 'move'] if self.doubles else ['move']

        #check if a pokemon fainted and insert a pseudo turn
        for pokemon in self.active_pokemon():
            if pokemon.fainted:
                self.pseudo_turn = True
                
        if self.pseudo_turn:
            # check player 1's pokemon
            for i in range(len(self.p1.active_pokemon)):
                if self.p1.active_pokemon[i].fainted:
                    self.p1.request = 'switch'
                else:
                    self.p1.request = 'pass'

            # check player 2's pokemon
            for i in range(len(self.p2.active_pokemon)):
                if self.p2.active_pokemon[i].fainted:
                    self.p2.request = 'switch'
                else:
                    self.p2.request = 'pass'
        print('---End of Turn ' + str(self.turn) + '---')
        return

    def turn_start(self):
        '''
        ONLY CALLED IN do_turn()

        Returns early if this is a pseudo turn
        Updates volatile statuses that only last one turn
        Resets the pokemon.pokemon_hit_this_turn for every active pokemon
        '''
        self.turn += 1
        self.turn = math.floor(self.turn)

        if self.pseudo_turn:
            self.turn -= 0.5
            return
        for pokemon in self.active_pokemon():
            pokemon.active_turns += 1
            pokemon.pokemon_hit_this_turn = 0
            # remove volatile statuses that only last one turn
            one_turn_statuses = {None, 'flinch', 'endure', 'protect',
                                'banefulbunker', 'spikyshield'}
            pokemon.volatile_statuses -= one_turn_statuses
        return

    def turn_end(self):
        '''
        ONLY CALLED IN do_turn()

        Updates flags after all actions are done.

        PRE: self.pseudo_turn = False
        '''
        if self.pseudo_turn:
            sys.exit('ERROR: turn_end() called on pseudo turn')

        # tick weather counter down
        if self.weather in ['sunlight', 'rain', 'sandstorm', 'hail']:
            self.weather_n -= 1
            if self.weather_n == 0:
                self.weather = 'clear'

        # weather damage
        for pokemon in self.active_pokemon():
            if pokemon.item == 'safteygoggles':
                continue
            if self.weather == 'sandstorm': 
                if {'Steel','Rock','Ground'}.isdisjoint(pokemon.types):
                    pokemon.damage(1/16, flag='percentmaxhp')
            if self.weather == 'hail': 
                if 'Ice' not in pokemon.types:
                    pokemon.damage(1/16, flag='percentmaxhp')


        # volatile statuses
        for pokemon in self.active_pokemon():
            # bound
            if 'partiallytrapped' in pokemon.volatile_statuses:
                pokemon.damage(pokemon.bound_damage, flag='percentmaxhp')
                pokemon.bound_n -= 1
                if pokemon.bound_n == 0:
                    pokemon.volatile_statuses -= {'partiallytrapped'}
            # aqua ring
            if pokemon.aqua_ring:
                if pokemon.item == 'bigroot':
                    pokemon.damage(-1/16 * 1.3, 'percentmaxhp')
                else:
                    pokemon.damage(-1/16, 'percentmaxhp')
            # leech seed
            if 'leechseed' in pokemon.volatile_statuses:
                foe = self.sides[0 if pokemon.side_id else 1].active_pokemon[0]
                foe.damage(-(pokemon.damage(1/8, 'percentmaxhp')) * (1.3 if foe.item == 'bigroot' else 1))
            # nightmare
            if 'nightmare' in pokemon.volatile_statuses:
                if pokemon.status == 'slp':
                    pokemon.damage(1/4, 'percentmaxhp')
            # perish song
            if 'perishsong' in pokemon.volatile_statuses:
                pokemon.perishsong_n -= 1
                if pokemon.perishsong_n == 0:
                    pokemon.faint()
            # encore 
            if 'encore' in pokemon.volatile_statuses:
                pokemon.encore_n -= 1
                if pokemon.encore_n == 0:
                    pokemon.volatile_statuses -= {'encore'}
            # taunt
            if 'taunt' in pokemon.volatile_statuses:
                pokemon.taunt_n -= 1
                if pokemon.taunt_n == 0:
                    pokemon.volatile_statuses.remove('taunt')
            # curse
            if 'curse' in pokemon.volatile_statuses:
                if 'Ghost' in pokemon.types:
                    pokemon.damage(1/4, flag='percentmaxhp')

        # do major status checks
        for pokemon in self.active_pokemon():
            if pokemon.status == 'brn':
                pokemon.damage(1/16, flag='percentmax')
            elif pokemon.status == 'psn':
                pokemon.damage(1/8, flag='percentmax')
            elif pokemon.status == 'tox':
                damage = 1/16*pokemon.toxic_n
                pokemon.damage(damage, flag='percentmax')
                pokemon.toxic_n += 1
            elif pokemon.status == 'frz':
                #twenty percent chance to be thawed
                if random.random() < 0.20:
                    pokemon.cure_status()
                if self.weather == 'sunlight':
                    pokemon.cure_status()
            elif pokemon.status == 'slp':
                pokemon.sleep_n -= 1
                if pokemon.sleep_n == 0:
                    pokemon.cure_status()
        return

    def run_action(self, a : Action) -> None:
        '''
        Takes Action object and if it is a switch, calls player.switch().
        If it is a mega evolution, call pokemon.mega_evolve().
        Lastly, if the action is a move, find the target pokemon's pointer
        and call battle.run_move(Pokemon, Move, Pokemon)
        '''
        #user, move, target, zmove, base_move = action
        # action is set up three different ways

        # one way for switches
        if a.action_type == 'switch':
            if a.user.player_uid == 1:
                self.p1.switch(a.user, a.pos)
            if a.user.player_uid == 2:
                self.p2.switch(a.user, a.pos)
            return

        # another for mega evolutions
        if a.action_type == 'mega':
            a.user.mega_evolve()
            return

        # if it is a single battle and target starts with 'foe'
        if not self.doubles and a.target[0:3] == 'foe':
            p = a.user.player_uid
            if p == 1:
                self.run_move(a.user, a.move, self.p2.active_pokemon[0])
            if p == 2:
                self.run_move(a.user, a.move, self.p1.active_pokemon[0])
            return

        if a.target == 'all': 
            move = move._replace(base_power = move.base_power * 0.75)
            for pokemon in self.active_pokemon():
                self.run_move(user, move, pokemon)
            return

        # and lastly for moves
        #
        # Targeting needs to be fixed
        '''
        if target == 'foe0':
            foe_side = self.sides[0 if user.side_id else 1]
            try:
                target_pokemon = foe_side.active_pokemon[0]
                self.run_move(user, move, target_pokemon)
            except IndexError:
                self.log(move.name + ' failed because there is no target')
            return
        elif target == 'foe1':
            foe_side = self.sides[0 if user.side_id else 1]
            try:
                target_pokemon = foe_side.active_pokemon[1]
                self.run_move(user, move, target_pokemon)
            except IndexError:
                self.log(move.name + ' failed because there is no target')
            return
        elif target == 'ally':
            ally_side = self.sides[user.side_id]
            ally_index = 0 if ally_side.active_pokemon.index(user) else 1
            target_pokemon = ally_side.active_pokemon[ally_index]
            self.run_move(user, move, target_pokemon)
            return
        elif target == 'self':
            self.run_move(user, move, user)
            return

        elif target == 'foes':
            foe_side = self.sides[0 if user.side_id else 1]
            for pokemon in foe_side.active_pokemon:
                self.run_move(user, move, pokemon)
            return
        elif target == 'allies':
            ally_side = self.sides[user.side_id]
            for pokemon in ally_side.active_pokemon:
                self.run_move(user, move, pokemon)
            return

        elif target == 'adjacent':
            # foe side
            foe_side = self.sides[0 if user.side_id else 1]
            for pokemon in foe_side.active_pokemon:
                self.run_move(user, move, pokemon)
            # ally pokemon
            ally_side = self.sides[user.side_id]
            ally_index = 0 if ally_side.active_pokemon.index(user) else 1
            try:
                target_pokemon = ally_side.active_pokemon[ally_index]
                self.run_move(user, move, target_pokemon)
            except IndexError:
                self.log(move.name + ' failed because there is no target')
            return

        elif target == 'all':
            move = move._replace(base_power = move.base_power * 0.75)
            for pokemon in self.active_pokemon:
                self.run_move(user, move, pokemon)
            return
        '''
        return
                
    def run_move(self, user : Pokemon, move : dex.Move, target : Pokemon) -> None:
        '''
        Does the move logic.
        '''
        # Fainted pokemon can't use their move.
        if user.fainted:
            #self.log(user.name + " fainted before they could move")
            return

        # subtract pp
        # struggle and zmoves do not have pp
        if move.id != 'struggle' and move.z_move.crystal is None:
            if move.id in user.pp:
                user.pp[move.id] -= 1
                # remove the move from the pokemons move list if it has no pp left
                #if user.pp[move.id] == 0:
                #    if move.id in user.moves:
                #        user.moves.remove(move.id)
        # update last used move
        user.last_used_move = move.id

        move = self.update_move_before_running(user, move, target)

        # ACCURACY CHECK
        if not self.accuracy_check(user, move, target):
            print(user.name + ' used ' + move.id + ' and missed')
            # move missed! do nothing
            return

        # zmove pp
        if move.z_move.crystal is not None:
            pass
            #user.side.used_zmove = True

        # Handle multi hit moves.
        # move.multi_hit is a probability distribution of number of hits in
        #  increasing order.
        # move.multi_hit[-1] is last element.
        number_hits = 1
        if move.multi_hit is not None:
            number_hits = random.choice(move.multi_hit)
            if user.ability == 'skilllink':
                number_hits = move.multi_hit[-1]

        #---------------
        # do damage
        #---------------

        for i in range(number_hits):
            # Triplekick checks accuracy for every hit
            if i != 1 and move.id == 'triplekick':
                if not self.accuracy_check(user, move, target):
                    return

            # damage calculation
            damage = self.damage(user, move, target)
            # do the damage
            # how much damage was actually done
            # is limited by how much hp the target had left
            damage = target.damage(damage)

        if damage > 0:
            target.last_damaging_move = move.id

        # do unique move things
        self.unique_moves_after_damage(user, move, target, damage)
        # handle boosts and statuses
        self.boosts_statuses(user, move, target)
        print(user.name + ' used ' + move.id + '')
        return

    def damage(self, user : Pokemon, move : dex.Move, target : Pokemon) -> int:
        '''
        Calculates the amount of damage done to the target by the user
        using the move.
        ''' 
        # status moves do zero dmg, return early
        if move.category == 'Status':
            return 0
        damage = 0

        # Was it a critical hit? -> Make local var.
        crit = False
        move_crit = move.crit_ratio if move.crit_ratio is not None else 0
        crit_chance = user.crit_chance + move_crit
        random_crit = random.random() < (dex.crit[crit_chance] if crit_chance <= 3 else 1) and self.rng
        if crit_chance >= 3 or random_crit:
            crit = True

        # Set up power, attack, defense variables
        power = move.base_power
        if move.category == 'Special':
            attack = user.get_specialattack(crit)
            defense = target.get_specialdefense(crit)
        elif move.category == 'Physical':
            attack = user.get_attack(crit)
            defense = target.get_defense(crit)

        # Main damage formula.
        damage = (math.floor(math.floor(math.floor(((2 * user.level) / 5) + 2) * attack * power / defense) / 50) + 2) 

        # multiply the damage by each modifier
        modifier = 1

        # CRITICAL DAMAGE
        if crit:
            modifier *= 1.5

        # RANDOMNESS
        if self.rng:
            modifier *= random.uniform(0.85, 1.0)

        # STAB (same type attack bonus)
        if move.type in user.types:
            modifier *= 1.5

        # TYPE EFFECTIVENESS
        type_modifier = 1
        for each in target.types:
            type_effect = dex.typechart_dex[each].damage_taken[move.type]
            type_modifier *= type_effect
            modifier *= type_effect

        # moves that hit multiple pokemon do less damage
        if self.doubles and move.target_type in ['foeSide', 'allyTeam', 'allAdjacent', 'allAdjacentFoes', 'allySide']:
            modifier *= 0.75

        # WEATHER
        if self.weather in ['rain', 'heavy_rain']:
            if move.type == 'Water':
                modifier *= 1.5
            elif move.type == 'Fire':
                modifier *= 0.5
        elif self.weather in ['sunlight', 'heavy_sunlight']:
            if move.type == 'Water':
                modifier *= 0.5
            elif move.type == 'Fire':
                modifier *= 1.5



        # burn
        if user.status == 'brn' and \
            move.category == 'Physical' and \
            user.ability != 'guts':
            modifier *= 0.5

        # zmove goes through protect at 1/4 damage
        if move.z_move.crystal is not None and 'protect' in target.volatile_statuses:
            modifier *= 0.25

        # aurora veil, lightscreen, reflect
        #if 'auroraveil' in target.side.side_conditions and not crit and user.ability != 'infiltrator':
            #double battle this should be 0.66
        #    modifier *= 0.5
        #elif 'lightscreen' in target.side.side_conditions and move.category == 'Special' and not crit and user.ability != 'infiltrator':
            #double battle this should be 0.66
        #    modifier *= 0.5
        #elif 'reflect' in target.side.side_conditions and move.category == 'Physical'and not crit and user.ability != 'infiltrator':
            #double battle this should be 0.66
        #    modifier *= 0.5

        if 'minimize' in target.volatile_statuses:
            if move.id in ['dragonrush', 'bodyslam', 'heatcrash', 'heavyslam', 'phantomforce', 'shadowforce', 'stomp']:
                modifier *= 2

        #magnitude, earthquake, surf, whirlpool do double dmg to dig and dive states
        
        # ABILITIES
        if target.ability == 'fluffy':
            if move.flags.contact and move.type != 'Fire':
                modifier *= 0.5
            elif not move.flags.contact and move.type == 'Fire':
                modifier *= 2
        elif target.ability == 'filter' or target.ability == 'prismarmor':
            if type_modifier > 1:
                modifier *= 0.75
        # friend guard
        elif target.ability in ['multiscale', 'shadowshield', 'solidrock']:
            if target.hp == target.maxhp:
                modifier *= 0.5

        if user.ability == 'sniper' and crit:
            modifier *= 1.5
        
        elif user.ability == 'tintedlens':
            if type_modifier < 1:
                modifier *= 2

        # ITEMS    
        if target.item == 'chilanberry' and move.type == 'Normal':
            modifier *= 0.5
        if user.item == 'expertbelt' and type_modifier > 1:
            modifier *= 1.2
        if user.item == 'lifeorb':
            modifier *= 1.3
        if user.item == 'metronome':
            modifier *= (1+(user.consecutive_move_uses*0.2))
        # type-resist berries
        if target.item in list(dex.type_resist_berries.keys()):
            if dex.type_resist_berries[target.item] == move.type:
                if type_modifier > 1:
                    modifier *= 0.5

        #floor damage before and after applying modifier
        damage = math.floor(damage)
        damage *= modifier
        damage = math.floor(damage)
        return damage

    def accuracy_check(self, user, move, target) -> bool:
        '''
        ONLY CALLED IN run_move??
        Check if the move hits(true) or misses(false).
        Check specific move requirements to not fail
        at the end.

        A False return here ends the run_move method.
        '''

        # full paralyze
        if user.status == 'par' and random.random() < 0.25:
            return False
        # asleep pokemon miss unless they use snore or sleeptalk
        elif user.status == 'slp' and not move.sleep_usable:
            return False

        # Is the target protected?
        if 'protect' in target.volatile_statuses and move.flags.protect:
            return False
        if 'banefulbunker' in target.volatile_statuses and move.flags.protect:
            return False
        if 'spikyshield' in target.volatile_statuses and move.flags.protect:
            return False
        if 'kingsshield' in target.volatile_statuses and move.flags.protect and move.category != 'Status':
            return False

        # protect moves accuracy
        if move.id in ['protect', 'detect', 'endure', 'wide guard', 'quick guard', 'spikyshield', 'kingsshield', 'banefulbunker']:
            rand_float = random.random()
            n = user.protect_n
            user.protect_n += 3
            if not self.rng and n > 0:
                return False
            if n == 0 or rand_float < (1.0 / n):
                return True
            return False
        else:
            # if the move is not a protect move, reset the counter
            user.protect_n = 0

        # flinched
        if 'flinch' in user.volatile_statuses:
            return False

        # fake out fails after 1 turn active
        if move.id == 'fakeout' and user.active_turns > 1:
            return False

        # if user is taunted, status moves fail
        if move.category == 'Status' and 'taunt' in user.volatile_statuses:
            return False

        # these moves dont check accuracy in certain weather
        if move.id == 'thunder' and self.weather == 'rain':
            return True
        if move.id == 'hurricane' and self.weather == 'rain':
            return True
        if move.id == 'blizzard' and self.weather == 'hail':
            return True

        # some moves don't check accuracy
        if move.accuracy is True:
            return True

        # returns a boolean whether the move hit the target
        # if temp < check then the move hits
        temp = random.randint(0, 99)
        accuracy = user.get_accuracy()
        evasion = target.get_evasion()
        check = 100
        if self.rng:
            check = (move.accuracy * accuracy * evasion)
        return temp < check 

    def boosts_statuses(self, user, move, target) -> None:
        '''
        ONLY CALLED in run_move()
        Handles boosts and statuses.
        '''
        # stat changing moves 
        user_volatile_status = ''
        target_volatile_status = ''
        # primary effects
        if move.primary['boosts'] is not None:
            target.boost(move.primary['boosts'])
        if move.primary['volatile_status'] is not None:
            target_volatile_status = move.primary['volatile_status']
            target.volatile_statuses.add(target_volatile_status)

        if move.primary['self'] is not None:
            if 'boosts' in move.primary['self']:
                user.boost(move.primary['self']['boosts'])
            if 'volatile_status' in move.primary['self']:
                user_volatile_status = move.primary['self']['volatile_status']
                user.volatile_statuses.add(user_volatile_status)

        if move.primary['status'] is not None:
            target.add_status(move.primary['status'])

        # secondary effects
        for effect in move.secondary:
            if not target.fainted:
                temp = random.randint(0, 99)
                check = effect['chance']
                if check != 100 and not self.rng:
                    check = 0
                if temp < check:
                    if 'boosts' in effect:
                        target.boost(effect['boosts'])
                    if 'status' in effect:
                        target.add_status(effect['status'], user)
                    if 'volatile_status' in effect:
                        target_volatile_status = effect['volatile_status']
                        target.volatile_statuses.add(target_volatile_status)

        if target_volatile_status == 'partiallytrapped':
            target.bound_n = 4 if random.random() < 0.5 else 5
            target.bound_damage = 1/16
            if user.item == 'gripclaw':
                target.bound_n = 7
            if user.item == 'bindingband':
                target.bound_damage = 1/8

        if target_volatile_status == 'taunt':
            target.taunt_n = 3

        if target_volatile_status == 'encore':
            target.encore_n = 3
        return

    def update_move_before_running(self, user, move, target) -> dex.Move:
        '''
        ONLY CALLED IN run_move()
        Returns the new move reference

        Some moves need to have their info updated based on the current state
        before running. the namedtuple._replace returns a new namedtuple
        instance with updated values so we dont have to worry about ruining the 
        game data
        '''
        # update the moves power

        # acrobatics
        if move.id == 'acrobatics' and user.item == '':
            power = move.base_power * 2
            move = move._replace(base_power = power)

        elif move.id == 'beatup':
            power = 0
            #for pokemon in user.side.pokemon:
            #    power += (dex.pokedex[pokemon.id].baseStats.attack / 10) + 5
            move = move._replace(base_power = power)
        
        elif move.id == 'crushgrip' or move.id == 'wringout':
            power = math.floor(120 * (target.hp / target.maxhp))
            if power < 1:
                power = 1
            move = move._replace(base_power = power)

        elif move.id == 'electroball':
            power = 1
            speed = target.stats.speed / user.stats.speed
            if speed <= 0.25:
                power = 150
            if speed > 0.25:
                power = 120
            if speed > .3333:
                power = 80
            if speed > 0.5:
                power = 60
            if speed > 1:
                power = 40
            move = move._replace(base_power = power)

        elif move.id == 'eruption' or move.id == 'waterspout':
            power = math.floor(150 * (user.hp / user.maxhp))
            if power < 1:
                power = 1
            move = move._replace(base_power = power)

        elif move.id == 'flail' or move.id == 'reversal':
            power = 1
            hp = user.hp / user.maxhp
            if hp < 0.0417:
                power = 200
            if hp >= 0.0417:
                power = 150
            if hp > 0.1042:
                power = 100
            if hp > 0.2083:
                power = 80
            if hp > 0.3542:
                power = 40
            if hp >= 0.6875:
                power = 20
            move = move._replace(base_power = power)

        elif move.id == 'fling':
            #default base power will be 30
            power = dex.fling.get(user.item, 30)
            move = move._replace(base_power = power)
            if user.item == 'kingsrock' or user.item == 'razorfang':
                move = move._replace(primary= {'boosts': None, 'status': None, 'volatile_status': 'flinch', 'self': None})
            elif user.item == 'flameorb':
                move = move._replace(primary= {'boosts': None, 'status': 'brn', 'volatile_status': None, 'self': None})
            elif user.item == 'toxicorb':
                move = move._replace(primary= {'boosts': None, 'status': 'tox', 'volatile_status': None, 'self': None})
            elif user.item == 'lightball':
                move = move._replace(primary= {'boosts': None, 'status': 'par', 'volatile_status': None, 'self': None})
            elif user.item == 'poisonbarb':
                move = move._replace(primary= {'boosts': None, 'status': 'psn', 'volatile_status': None, 'self': None})

        # assume max base_power for return and frustration
        elif move.id == 'frustration' or move.id == 'return':
            move = move._replace(base_power = 102)

        elif move.id == 'grassknot':
            power = 1
            weight = dex.pokedex[target.species].weightkg
            if weight >= 200:
                power = 120
            if weight < 200:
                power = 100
            if weight < 100:
                power = 80
            if weight < 50:
                power = 60
            if weight < 25:
                power = 40
            if weight < 10:
                power = 20
            move = move._replace(base_power = power)

        elif move.id == 'heatcrash' or move.id == 'heavyslam':
            power = 1
            weight = dex.pokedex[target.id].weightkg / dex.pokedex[user.id].weightkg
            if weight > 0.5:
                power = 40
            if weight < 0.5:
                power = 60
            if weight < 0.333:
                power = 80
            if weight < 0.25:
                power = 100
            if weight < 0.20:
                power = 120
            move = move._replace(base_power = power)

        elif move.id == 'gyroball':
            power = math.floor(25 * (target.get_speed() / user.get_speed()))
            if power < 1:
                power = 1
            move = move._replace(base_power = power)

        elif move.id == 'magnitude':
            power = random.choice(dex.magnitude_power)
            move = move._replace(base_power = power)

        elif move.id == 'naturalgift':
            item = dex.item_dex[user.item]
            if item.isBerry:
                move = move._replace(base_power = item.naturalGift['basePower'])
                move = move._replace(type = item.naturalGift['type'])
        
        elif move.id == 'powertrip' or move.id == 'storedpower':
            power = 20
            for stat in user.boosts:
                if user.boosts[stat] > 0:
                    power += (user.boosts[stat] * 20)
            move = move._replace(base_power = power)

        elif move.id == 'present':
            power = random.choice([0, 0, 120, 80, 80, 80, 40, 40, 40, 40])
            move = move._replace(base_power = power)

        elif move.id == 'punishment':
            power = 60
            for stat in target.boosts:
                if target.boosts[stat] > 0:
                    power += (target.boosts[stat] * 20)
            if power > 200:
                power = 200
            move = move._replace(base_power = power)

        elif move.id == 'spitup':
            power = 100 * user.stockpile
            move = move._replace(base_power = power)
            user.stockpile = 0

        # assist
        elif move.id == 'assist':
            # it hink this is broken
            #move = dex.move_dex[random.choice(target.moves)]
            pass
        
        # metronome
        elif move.id == 'metronome':
            while move.id in dex.no_metronome:
                move = dex.move_dex[random.choice(list(dex.move_dex.keys()))]

        # mimic
        elif move.id == 'mimic':
            if target.last_used_move is not None:
                if 'mimic' in user.moves:
                    user.moves.remove('mimic')
                user.moves.append(target.last_used_move)
                move = dex.move_dex[target.last_used_move]

        # copycat
        elif move.id == 'copycat':
            if target.last_used_move is not None:
                move = dex.move_dex[target.last_used_move]

        elif move.id == 'naturepower':
            move = dex.move_dex['triattack']

        # mirror move
        elif move.id == 'mirror move':
            if target.last_used_move is not None:
                move = dex.move_dex[target.last_used_move]

        # check non unique stuff
        # baneful bunker
        if 'banefulbunker' in target.volatile_statuses:
            if move.flags.contact:
                user.add_status('psn')

        # spiky shield
        if 'spikeyshield' in target.volatile_statuses:
            user.damage(0.125, flag='percentmaxhp')

        # RECOIL DAMAGE
        if move.recoil.damage != 0:
            if move.recoil.condition == 'always':
                if move.recoil.type == 'maxhp':
                    user.damage(move.recoil.damage, flag='percentmaxhp')
        return move

    def unique_moves_after_damage(self, user, move, target, damage):
        '''
        ONLY CALLED IN run_move()
        '''
        #drain moves
        if user.item == 'bigroot':
            user.damage(-(math.floor(damage * move.drain * 1.3)))
        else:
            user.damage(-(math.floor(damage * move.drain)))

        #heal moves
        if move.heal > 0:
            user.damage(-(move.heal), flag='percentmaxhp')

        #heal moves that depend on weather
        if move.id in ['moonlight', 'morningsun', 'synthesis']:
            if self.weather == 'clear':
                user.damage(-(0.5), flag='percentmaxhp')
            elif self.weather == 'sunlight':
                user.damage(-(0.66), flag='percentmaxhp')
            else:
                user.damage(-(0.25), flag='percentmaxhp')
        if move.id == 'shoreup':
            if self.weather == 'sandstorm':
                user.damage(-(0.66), flag='percentmaxhp')
            else:
                user.damage(-(0.50), flag='percentmaxhp')

        #recoil moves
        if move.recoil.damage != 0:
            if move.recoil.condition == 'hit':
                if move.recoil.type == 'maxhp':
                    user.damage(move.recoil.damage, flag='percentmaxhp')
                if move.recoil.type == 'damage':
                    user.damage(damage* move.recoil.damage)

        # terrain moves 
        if move.terrain is not None:
            self.terrain = move.terrain

        # weather moves
        if move.weather is not None and self.weather != move.weather:
            self.weather = move.weather
            self.weather_n = 5
            if user.item == 'heatrock' and self.weather == 'sunlight':
                self.weather_n = 8
            if user.item == 'damprock' and self.weather == 'rain':
                self.weather_n = 8
            if user.item == 'smoothrock' and self.weather == 'sandstorm':
                self.weather_n = 8
            if user.item == 'icyrock' and self.weather == 'hail':
                self.weather_n = 8

        # accupressure
        if move.id == 'acupressure':
            possible_stats = [stat for stat in user.boosts if user.boosts[stat] < 6]
            if len(possible_stats) > 0:
                rand_int = random.randint(0, len(possible_stats)-1)
                boost_stat = possible_stats[rand_int]
                user.boosts[boost_stat] += 2
                if user.boosts[boost_stat] > 6:
                    user.boosts[boost_stat] = 6

        # aqua ring
        if move.id == 'aquaring':
            user.aqua_ring = True

        # ingrain
        if move.id == 'ingrain':
            user.aqua_ring = True
            user.trapped = True

        # aromatherapy
        #if move.id == 'aromatherapy' or move.id == 'healbell': 
        #    for pokemon in user.side.pokemon:
        #        pokemon.cure_status()


        # belly drum
        if move.id == 'bellydrum' and user.hp > (0.5 * user.maxhp):
            user.boost({'atk': 6})
            user.damage(0.5, flag='percentmax')

        # bestow
        if move.id == 'bestow':
            if user.item != '' and target.item == '':
                target.item = user.item
                user.item = ''

        # camouflage
        # every battle played using the sim is a 'link battle'
        if move.id == 'camouflage':
            user.types = ['Normal']

        # conversion
        move_types = []
        if move.id == 'conversion':
            for user_move in user.moves:
                if dex.move_dex[user_move].type not in user.types:
                    move_types.append(dex.move_dex[user_move].type)
            if len(move_types) > 0:
                user.types = [move_types[random.randint(0, len(move_types)-1)]]

        # this causes an attribute error and i dont know why
        # attrubiteError starts here
        # I THINK I FIGURED IT OUT
        # conversion 2
        #print(str(move))
        if move.id == 'conversion2':
            if user.last_damaging_move is not None:
                for type in dex.typechart_dex[dex.move_dex[user.last_damaging_move].type].damage_taken:
                    if type not in user.types:
                        move_types.append(type)
            if len(move_types) > 0:
                user.types = [move_types[random.randint(0, len(move_types)-1)]]

        # curse
        if move.id == 'curse' and 'Ghost' not in user.types:
            user.boost({'atk': 1, 'def': 1, 'spe': -1})

        # defog
        if move.id == 'defog':
            target.boost({'evasion': -1})
            #target.side.side_condition = set()

        # entrainment
        if move.id == 'entrainment':
            target.ability = user.ability

        # flower shield
        if move.id == 'flowershield':
            if 'Grass' in user.types:
                user.boost({'def': 1})
            if 'Grass' in target.types:
                target.boost({'def': 1})

        # focus energy
        if move.id == 'focusenergy':
            user.crit_chance += 2

        # forests curse
        if move.id == 'forestscurse':
            target.types.append('Grass')

        # gastro acid
        if move.id == 'gastroacid':
            if target.ability not in ['multitype', 'stancechance', 'schooling', 'comatose', 'shieldsdown', 'disguise', 'rkssystem', 'battlebond', 'powerconstruct']:
                target.ability = 'suppressed'

        # guard split
        if move.id == 'guardsplit':
            avg_def = (user.stats.defense + target.stats.defense)/2
            avg_spd = (user.stats.specialdefense + target.stats.specialdefense)/2

            user.stats.defense =  avg_def
            target.stats.defense = avg_def

            user.stats.specialdefense = avg_spd
            target.stats.specialdefense = avg_spd

        # guard swap
        if move.id == 'guardswap':
            user_def = user.stats.defense
            target_def = target.stats.defense

            user_spd = user.stats.specialdefense
            target_spd = target.stats.specialdefense

            user.stats.defense = target_def
            target.stats.defense = user_def

            user.stats.specialdefense = target_spd
            target.stats.specialdefense = user_spd

        # heart swap
        if move.id == 'heartswap':
            user_boosts = user.boosts
            target_boosts = target.boosts

            user.boosts = target_boosts
            target.boosts = user_boosts

        # kinggsheild
        if move.id == 'kingsshield' and user.id == 'aegislash':
            user.form_change('aegislashshield')

        # pain split
        if move.id == 'painsplit':
            avg_hp = (user.hp + target.hp) /2
            user.hp = avg_hp if avg_hp < user.stats.hp else user.stats.hp
            target.hp = avg_hp if avg_hp < target.stats.hp else target.stats.hp

        # power split
        if move.id == 'powersplit':
            avg_atk = (user.stats.attack + target.stats.attack)/2
            avg_spa = (user.stats.specialattack + target.stats.specialattack)/2

            user.stats._replace(attack = avg_atk)
            target.stats._replace(attack = avg_atk)

            user.stats._replace(specialattack = avg_spa)
            target.stats._replace(specialattack = avg_spa)

        # power swap
        if move.id == 'powerswap':
            user_atk = user.stats.attack
            target_atk = target.stats.attack

            user_spa = user.stats.specialattack
            target_spa = target.stats.specialattack

            user.stats._replace(attack = target_atk)
            target.stats._replace(attack = user_atk)

            user.stats._replace(specialattack = target_spa)
            target.stats._replace(specialattack = user_spa)

        # power trick
        if move.id == 'powertrick':
            user_atk = user.stats.attack
            user_spa = user.stats.specialattack

            user.stats.specialattack = user_atk
            user.stats.attack = user_spa

        # psychoshift
        if move.id == 'psychoshift':
            if target.add_status(user.status):
                user.cure_status()

        # psychup
        if move.id == 'psychup':
            user.boosts = target.boosts

        # purify
        if move.id == 'purify':
            if target.cure_status():
                user.damage(-0.5, flag='percentmaxhp')
        
        # recycle
        if move.id == 'recycle':
            if user.last_used_item is not None and user.item == '':
                user.item = user.last_used_item

        # reflect type
        if move.id == 'reflecttype':
            user.types = target.types

        # refresh
        if move.id == 'refresh':
            if user.status in ['brn', 'par', 'psn', 'tox']:
                user.cure_status()

        # rest
        if move.id == 'rest':
            if user.status != 'slp':
                user.status = 'slp'
                user.sleep_n = 2
                user.damage(-1, flag='percentmaxhp')

        # role play
        if move.id == 'roleplay':
            user.ability = target.ability

        # simple beam
        if move.id == 'simplebeam':
            target.ability = 'simple'

        # sketch
        if move.id == 'sketch':
            if target.last_used_move is not None:
                if 'sketch' in user.moves:
                    user.moves.remove('sketch')
                user.moves.append(target.last_used_move)

        # skill swap
        if move.id == 'skillswap':
            user_ability = user.ability
            target_ability = target.ability

            user.ability = target_ability
            target.ability = user_ability

        # sleep talk
        if move.id == 'sleeptalk':
            if user.status == 'slp' and len(user.moves) > 1:
                while move.id == 'sleeptalk':
                    move = dex.move_dex[user.moves[random.randint(0, len(user.moves)-1)]]

        # soak
        if move.id == 'soak':
            target.types = ['Water']

        # speed swap
        if move.id == 'speedswap':
            user_speed = user.stats.speed
            target_speed = target.stats.speed

            user.stats._replace(speed = target_speed)
            target.stats._replace(speed = user_speed)

        # stockpile
        if move.id == 'stockpile':
            user.stockpile += 1
            if user.stockpile > 3:
                user.stockpile = 3
            user.boost({'def': 1, 'spd': 1})

        # strength sap
        if move.id == 'strengthsap':
            if target.boosts['atk'] != -6:
                user.damage(-(target.get_attack()))
                target.boost({'atk': -1})

        # substitute
        if move.id == 'substitute':
            if not user.substitute and user.hp > user.stats.hp*0.25:
                user.substitute = True
                user.damage(0.25, flag='percentmaxhp')
                user.substitute_hp = math.floor(0.25 * user.stats.hp)

        # switcheroo and trick
        if move.id == 'switcheroo' or move.id == 'trick':
            user_item = user.item
            target_item = target.item

            user.item = target_item
            target.item = user_item

        # topsy-turvy
        if move.id == 'topsyturvy':
            for stat in target.boosts:
                target.boosts[stat] = -target.boosts[stat]

        # trick or treat
        if move.id == 'trickortreat':
            target.types.append('Ghost')

        # worry seed
        if move.id == 'worryseed':
            target.ability = 'insomnia'

        # breaks protect
        if move.breaks_protect:
            if 'protect' in target.volatile_statuses:
                target.volatile_statuses.remove('protect')
            if 'banefulbunker' in target.volatile_statuses:
                target.volatile_statuses.remove('banefulbunker')
            if 'spikyshield' in target.volatile_statuses:
                target.volatile_statuses.remove('spikyshield')
            if 'kingsshield' in target.volatile_statuses:
                target.volatile_statuses.remove('kingsshield')

        # growth (the move) does another stat boost in the sun
        if move.id == 'growth':
            if self.weather == 'sunlight':
                target.boost(move.primary['self']['boosts'])

    def active_pokemon(self) -> List[Pokemon]:
        '''
        Returns a list of pointers to all the active pokemon in this battle
        '''
        active = []
        for pokemon in self.p1.active_pokemon:
            active.append(pokemon)
        for pokemon in self.p2.active_pokemon:
            active.append(pokemon)
        return active


    def create_move(self, p : Pokemon, c : Decision) -> dex.Move:
        '''
        This method takes in the user pokemon and the decision corresponding
        to that pokmeon and returns a Move (namedtuple) object that contains 
        all information about the move that pokemon will use.
        '''
        if c.type != 'move':
            return

        move = dex.move_dex[p.moves[c.selection]]

        # encore overwrites move decision
        if 'encore' in p.volatile_statuses and p.last_used_move is not None:
            move = dex.move_dex[p.last_used_move]
            #return move # Can you z move the encored move? I think yes?

        player = self.p2
        if p.player_uid == 1:
            player = self.p1
        if not p.can_z(move) or not c.zmove or player.used_zmove:
            return move

        # update z move power
        # THIS NEEDS UPDATING
        item = dex.item_dex[p.item]
        if item.zMove is True:
            zmove_id = dex.zmove_chart[item.id]
        else:
            zmove_id = re.sub(r'\W+', '', item.zMove.lower())
        base_move = move
        move = dex.move_dex[zmove_id]

        if move.base_power == 1:
            move = move._replace(base_power = base_move.z_move.base_power)
            move = move._replace(category = base_move.category)

        z_move = move.z_move._replace(boosts=base_move.z_move.boosts)
        z_move = move.z_move._replace(effect=base_move.z_move.effect)
        move = move._replace(z_move=z_move)
        return move

def populate_action_queue(q : List, p : Pokemon, c : Decision, m : dex.Move) -> None:
    '''
    Creates and appends actions to the queue q for the given decisions.
    '''
    a = None

    # generate SWITCH actions
    if c.type == 'switch':
        a = Action('switch', user=p, pos=c.selection) 

    # generate MEGA EVOLUTION actions
    elif c.type == 'mega' and c.mega:
        a = Action('mega', user=p)

    # move decision actions
    elif c.type == 'move':
        a = Action('move', user=p, move=m, target=c.target)

    if a is not None:
        heapq.heappush(q, (resolve_priority(a), a))
    return

def resolve_priority(action) -> float:
    '''
    returns a number
    (action_priority_tier * 13000) + user.get_speed() + random.random()

    lower number is the higher priority

    multiply tier by 13_000 because 12_096 is maximum calculated speed
    stat of any pokemon

    add random.random() to the allow the priority queue to handle possible
    ties with a coin flip

    priority tiers
        0-pursuit on a pokemon that is switching out but not yet fainted
            -if mega, mega first then pursuit
        1-switches
            -calculated speed
        2-mega
            -calculated speed
            -update this pokemons later actions with new calculated speed
        3-15-moves
            - +5 to -7 priority tiers
                -Gale Wings, Prankster, Triage affect priority tier
            -calculated speed
                -Full Incense, Lagging Tail, Stall go last in priority tier
                -Quick Claw, Custap Berry go first in priority tier
                -Trick Room

    the priority queue can also be re-ordered by certain effects
    ex. Round, Dancer, Instruct, Pledge moves, After You, Quash
            
    '''

    # apt - action priority tier as defined above
    action_priority_tier : int = None

    if action.action_type == 'switch':
        action_priority_tier = 1
    elif action.action_type == 'mega':
        action_priority_tier = 2
    elif action.action_type == 'move':
        action_priority_tier = 3 + (5 - action.move.priority)

    # get_speed() returns higher number = faster speed
    # priority speed needs to be lower number = faster speed
    speed = 12096 - action.user.get_speed()

    # multiply priority tier by 13000 because it supercedes speed
    priority = action_priority_tier * 13000

    # random.random() is the tie breaker
    return priority + speed + random.random()
