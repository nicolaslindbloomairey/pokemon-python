from tools.pick_six import generate_team
from tools.ai import Ai
from data import dex
import random
import math
import heapq
import re
import sys

from new_sim.structs import *
from new_sim.battle import Battle


def join(self, side_id=None, team=None):
    if side_id is None:
        side_id = self.players

    if side_id > 1: # side id greater than one would be more than two sides which is not possible
        sys.exit("ERROR: more than two sides in pokemon battle?!?")
        return
    self.sides[side_id].populate_team(team)
    self.players += 1
    #self.pbi_log.append('player p' + str(side_id + 1) + '\n')
    #self.pbi_log.append(self.pack_team(team))

def log(self, message):
    #if self.debug:
    #    print(str(message))
    self.debug_log.append(str(message) + '\n')

# run once both players are here
def set_up(self):
    # single battle, 0 is side0, 1 is side1
    # double battle, 0 is side0active0, 1 is side0active1, 2 is side1active0...
    if not self.doubles:
        self.active_pokemon = [self.sides[0].active_pokemon[0],
                self.sides[1].active_pokemon[0]]
    elif self.doubles:
        self.active_pokemon = [self.sides[0].active_pokemon[0],
                self.sides[0].active_pokemon[1],
                self.sides[1].active_pokemon[0],
                self.sides[1].active_pokemon[1]]

        self.setup_ran = True


#method that runs the entire battle
def run(self):
    while self.players != 2:
        self.join()

    self.set_up()
    while not self.ended:

        # let the ai pick what each side will do
        for side in self.sides:
            side.default_decide()

        self.do_turn()

        if self.turn > 500:
            self.log('ERROR TURN COUNTER IS OVER 500')
            #self.error = True
            break
    if self.debug or self.error:
        print(''.join(self.debug_log))

def populate_action_queue(self, action_queue):
    for side in self.sides:
        n = 2 if self.doubles else 1
        n = len(side.active_pokemon)
        for i in range(n):
            choice = side.choice[i]
            user = side.active_pokemon[i]
            #-------------------------
            # generate SWITCH actions
            #-------------------------
            if choice.type == 'switch':
                move = 'switch'
                target = choice.selection
                action = dex.Action(user, move, target) 
                action_tuple = (self.resolve_priority(action), action)

                heapq.heappush(action_queue, action_tuple)

            #-------------------------
            # move decision actions
            #-------------------------
            elif choice.type == 'move':

            #-------------------------
                # generate MEGA EVOLUTION actions
                #-------------------------
                if choice.mega:
                    move = 'mega'

                    action = dex.Action(user, move)
                    action_tuple = (self.resolve_priority(action), action)
                    heapq.heappush(action_queue, action_tuple)


                #-------------------------
                # check if stuggle is move
                #-------------------------
                if choice.selection == 'struggle':
                    move = dex.move_dex['struggle']
                else:

                    if 'encore' in user.volatile_statuses and user.last_used_move is not None:
                        move = dex.move_dex[user.last_used_move]
                    else:
                        move = dex.move_dex[user.moves[choice.selection]]

                #-------------------------
                # update z move power
                #-------------------------
                if choice.zmove and user.can_z(move):
                    item = dex.item_dex[user.item]
                    if item.zMove is True:
                        zmove_id = dex.zmove_chart[item.id]
                    else:
                        zmove_id = re.sub(r'\W+', '', item.zMove.lower())
                    base_move = move
                    move = dex.move_dex[zmove_id]

                    # update the zmove power 
                    if move.base_power == 1:
                        move = move._replace(base_power = base_move.z_move.base_power)
                        move = move._replace(category = base_move.category)

                    z_move = move.z_move._replace(boosts=base_move.z_move.boosts)
                    z_move = move.z_move._replace(effect=base_move.z_move.effect)
                    move = move._replace(z_move=z_move)

                #-------------------------
                # targeting
                #-------------------------

                if self.doubles:
                    target = self.resolve_target(move, choice)
                elif not self.doubles:
                    if move.target_type == 'self':
                        target = 'self'
                    else:
                        target = 'foe0'


                # actually add the moves to the queue
                #if move.target_type == 'self':
                #    target = side
                #elif move.target_type == 'normal':
                #    target = self.sides[0 if side.id else 1]
                #else:
                #    target = self.sides[0 if side.id else 1]

                #-------------------------
                # generate MOVE actions
                #-------------------------
                action = dex.Action(user, move, target)
                action_tuple = (self.resolve_priority(action), action)
                heapq.heappush(action_queue, action_tuple)

            else:
                # dont add any action to the queue
                # this is here for the 'pass' decision
                pass

def resolve_target(self, move, choice):
    '''
    checks if the choice.target is a valid target for the move type
    if not return a default target

    target options are:

    targets 1 pokemon
        -foe0
        -foe1
        -ally
        -self

    targets 2 pokemon
        -foes
        -allies

    targets 3 pokemon
        -adjacent

    targets 4 pokemon
        -all
    '''
    if move.target_type == 'adjacentFoe':
        if choice.target in ['foe0', 'foe1']:
            return choice.target
        else:
            return 'foe0' if random.random() > 0.5 else 'foe1'
    elif move.target_type == 'allAdjacentFoes':
        return 'foes'
    elif move.target_type == 'any':
        if choice.target in ['foe0', 'foe1', 'ally']:
            return choice.target
        else:
            return 'foe0' if random.random() > 0.5 else 'foe1'
    elif move.target_type == 'foeSide':
        return 'foes'
    elif move.target_type == 'adjacentAlly':
        return 'ally'
    elif move.target_type == 'allAdjacent':
        return 'adjacent'
    elif move.target_type == 'randomNormal':
        if random.random() > 0.5:
            return 'foe0'
        else:
            return 'foe1'
    elif move.target_type == 'normal':
        if choice.target in ['foe0', 'foe1']:
            return choice.target
        else:
            return 'foe0' if random.random() > 0.5 else 'foe1'
    elif move.target_type == 'adjacentAllyOrSelf':
        if choice.target in ['self', 'ally']:
            return choice.target
        else:
            return 'self'
    elif move.target_type == 'self':
        return 'self'
    elif move.target_type == 'allySide':
        return 'allies'
    elif move.target_type == 'scripted':
        # used by counter, mirrorcoat, and metalburst
        # targets the last foe to damage the user this turn
        return 'foe0'
    elif move.target_type == 'all':
        return 'all'
    elif move.target_type == 'allyTeam':
        return 'allies'

def start_of_turn(self):
    if self.pseudo_turn:
        return

    #----------------
    # start of turn stuff
    #-------------------

    # remove volatile statuses that only last one turn
    for pokemon in self.active_pokemon:
        pokemon.pokemon_hit_this_turn = 0

        # one turn statuses
        one_turn_statuses = {None, 'flinch', 'endure', 'protect', 'banefulbunker',
                'spikyshield'}
        pokemon.volatile_statuses -= one_turn_statuses

def end_of_turn(self):
    if self.pseudo_turn:
        return

    #------------------
    # END OF TURN STUFF
    #------------------

    # weather stuff
    if self.weather in ['sunlight', 'rain', 'sandstorm', 'hail']:
        self.weather_n -= 1
        if self.weather_n == 0:
            self.weather = 'clear'

    for pokemon in self.active_pokemon:
        if self.weather == 'sandstorm': 
            if 'Steel' not in pokemon.types and 'Rock' not in pokemon.types and 'Ground' not in pokemon.types:
                if pokemon.item != 'safetygoggles':
                    pokemon.damage(1/16, flag='percentmaxhp')
        if self.weather == 'hail': 
            if 'Ice' not in pokemon.types:
                if pokemon.item != 'safetygoggles':
                    pokemon.damage(1/16, flag='percentmaxhp')


    # volatile statuses
    for pokemon in self.active_pokemon:

        # bound
        if 'partiallytrapped' in pokemon.volatile_statuses:
            pokemon.damage(pokemon.bound_damage, flag='percentmaxhp')
            pokemon.bound_n -= 1
            if pokemon.bound_n == 0:
                pokemon.volatile_statuses -= {'partiallytrapped'}

        # aqua ring
        if pokemon.aqua_ring:
            if pokemon.item == 'bigroot':
                pokemon.damage(-(1/12), 'percentmaxhp')
            else:
                pokemon.damage(-(1/16), 'percentmaxhp')

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

        # perish song
        if 'encore' in pokemon.volatile_statuses:
            pokemon.encore_n -= 1
            if pokemon.encore_n == 0:
                pokemon.volatile_statuses -= {'encore'}

        if 'taunt' in pokemon.volatile_statuses:
            pokemon.taunt_n -= 1
            if pokemon.taunt_n == 0:
                pokemon.volatile_statuses.remove('taunt')

        # curse
        if 'curse' in pokemon.volatile_statuses:
            if 'Ghost' in pokemon.types:
                pokemon.damage(0.25, flag='percentmaxhp')

    # do major status checks
    for pokemon in self.active_pokemon:
        if pokemon.status == 'brn':
            pokemon.damage(0.0625, flag='percentmax')
        elif pokemon.status == 'psn':
            pokemon.damage(0.125, flag='percentmax')
        elif pokemon.status == 'tox':
            damage = 0.0625*pokemon.toxic_n
            pokemon.damage(damage, flag='percentmax')
            pokemon.toxic_n += 1
        elif pokemon.status == 'frz':
            #twenty percent chance to be thawed
            if random.random() < 0.20:
                pokemon.status == ''
            if self.weather == 'sunlight':
                pokemon.cure_status()
        elif pokemon.status == 'slp':
            pokemon.sleep_n -= 1
            if pokemon.sleep_n == 0:
                pokemon.cure_status()


def do_turn(self):
    '''
    to be called once both sides have made their decisions

    updates the game state according to the decisions
    '''

    if not self.setup_ran:
        self.set_up()

    for side in self.sides:
        #side.active_pokemon.volatile_statuses = set()

        if side.choice is None:
            # error - one or more sides is missing a decsion
            raise ValueError('one or more sides is missing a decision')

    self.turn += 1

    for pokemon in self.active_pokemon:
        pokemon.active_turns += 1

    self.start_of_turn()

    # print the state of the battle
    #print(str(self.sides[0].request))
    #print(str(self.sides[1].request))
    self.log(self)

    # create priority queue and references to both sides
    action_queue = []

    # populate action queue
    self.populate_action_queue(action_queue)

    # run each each action in the queue
    while action_queue:
        priority, next_action = heapq.heappop(action_queue) 
        self.run_action(next_action)

    self.end_of_turn()

    #request the next turns move
    self.pseudo_turn = False
    self.request = 'move'
    for i in range(2):
        self.sides[i].request = ['move', 'move'] if self.doubles else ['move']

    #check if a pokemon fainted and insert a pseudo turn
    for pokemon in self.active_pokemon:
        if pokemon.fainted:
            self.pseudo_turn = True

    if self.pseudo_turn:
        for side in self.sides:
            #n = 2 if self.doubles else 1
            n = len(side.active_pokemon)
            for i in range(n):
                if side.active_pokemon[i].fainted:
                    side.request[i] = 'switch'
                else:
                    side.request[i] = 'pass'

#       check for a winner
#       end the while true once the game ends
    for side in self.sides:
        if not side.pokemon_left:
            self.ended = True
            self.winner = 0 if side.id else 1

def resolve_priority(self, action):
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
    action_priority_tier = None

    if action.move == 'switch':
        action_priority_tier = 1

    elif action.move == 'mega':
        action_priority_tier = 2

    #elif action.move.id == 'pursuit' and action.target.active_pokemon.is_switching:
    #    action_priority_tier = 0

    else:
        action_priority_tier = 3 + (5 - action.move.priority)

    #action_priority_tier should never be None here

    # get_speed() returns higher number = faster speed
    # priority speed needs to be lower number = faster speed
    speed = 12096 - action.user.get_speed()

    # multiply priority tier by 13000 because it supercededes speed
    priority = action_priority_tier * 13000

    tie_breaker = random.random()

    return priority + speed + tie_breaker

def run_action(self, action):
    user, move, target, zmove, base_move = action
    # action is set up three different ways

    # one way for switches
    if move == 'switch':
        user.side.switch(user, target)
        return

    # another for mega evolutions
    if move == 'mega':
        user.mega_evolve()
        return

    # and lastly for moves
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

def run_move(self, user, move, target):
    '''
    user = Pokemon
    move = Move
    target = Pokemon
    '''
    if user.fainted:
        self.log(user.name + " fainted before they could move")
        return


    # subtract pp
    # struggle and zmoves do not have pp
    if move.id != 'struggle' and move.z_move.crystal is None:
        # moves ran by other stuff
        #print(str(user.pp))
        if move.id in user.pp:
            user.pp[move.id] -= 1

            # remove the move from the pokemons move list if it has no pp left
            if user.pp[move.id] == 0:
                if move.id in user.moves:
                    user.moves.remove(move.id)

    user.last_used_move = move.id

    move = self.update_move_before_running(user, move, target)

    # accuracy_check
    if not self.accuracy_check(user, move, target):
        # move missed! do nothing
        return

    #user.pokemon_hit_this_turn += 1

    # zmove pp
    if move.z_move.crystal is not None:
        user.side.used_zmove = True

    # handle multi hit moves
    number_hits = 1
    if move.multi_hit is not None:
        number_hits = random.choice(move.multi_hit)
        if user.ability == 'skilllink':
            number_hits = move.multi_hit[-1]

    #---------------
    # do damage
    #---------------

    for i in range(number_hits):

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

def damage(self, user, move, target):

    # status moves do zero dmg
    # return early
    if move.category == 'Status':
        self.log(user.fullname + " used " + move.name)
        return 0

    damage = 0


    crit = False

    move_crit = move.crit_ratio if move.crit_ratio is not None else 0
    crit_chance = user.crit_chance + move_crit
    random_crit = random.random() < (dex.crit[crit_chance] if crit_chance <= 3 else 1) and self.rng

    if crit_chance >= 3 or random_crit:
        crit = True

    power = move.base_power

    if move.category == 'Special':
        attack = user.get_specialattack(crit)
        defense = target.get_specialdefense(crit)
    elif move.category == 'Physical':
        attack = user.get_attack(crit)
        defense = target.get_defense(crit)

    damage = (math.floor(math.floor(math.floor(((2 * user.level) / 5) + 2) * attack * power / defense) / 50) + 2) 

    #------------------------------------
    # multiply the damage by each modifier
    #------------------------------------
    modifier = 1

    # 0.75 if move has multiple targets, 1 otherwise
    #if user.pokemon_hit_this_turn > 1:
    #    modifier *= 0.75
    if self.doubles and move.target_type in ['foeSide', 'allyTeam', 'allAdjacent', 'allAdjacentFoes', 'allySide']:
        modifier *= 0.75

    # weather
    if self.weather == 'rain' or self.weather == 'heavy_rain':
        if move.type == 'Water':
            modifier *= 1.5
        elif move.type == 'Fire':
            modifier *= 0.5
    elif self.weather == 'sunlight' or self.weather == 'heavy_sunlight':
        if move.type == 'Water':
            modifier *= 0.5
        elif move.type == 'Fire':
            modifier *= 1.5
    else:
        modifier *= 1.0

    if crit:
        modifier *= 1.5

    # random float
    # if rng is off always do max damage
    if self.rng:
        modifier *= random.uniform(0.85, 1.0)

    # same type attack bonus
    if move.type in user.types:
        modifier *= 1.5

    # type effectiveness
    type_modifier = 1
    for each in target.types:
        type_effect = dex.typechart_dex[each].damage_taken[move.type]
        type_modifier *= type_effect
        modifier *= type_effect

    # burn
    if user.burned and move.category == 'Physical' and user.ability != 'guts':
        modifier *= 0.5

    # zmove going through protect
    if move.z_move.crystal is not None and 'protect' in target.volatile_statuses:
        modifier *= 0.25

    # aurora veil, lightscreen, reflect
    if 'auroraveil' in target.side.side_conditions and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
        modifier *= 0.5
    elif 'lightscreen' in target.side.side_conditions and move.category == 'Special' and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
        modifier *= 0.5
    elif 'reflect' in target.side.side_conditions and move.category == 'Physical'and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
        modifier *= 0.5

    if 'minimize' in target.volatile_statuses:
        if move.id in ['dragonrush', 'bodyslam', 'heatcrash', 'heavyslam', 'phantomforce', 'shadowforce', 'stomp']:
            modifier *= 2

    #magnitude, earthquake, surf, whirlpool do double dmg to dig and dive states

    #----------------
    #ability modifiers
    #-----------------

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

    if user.ability == 'sniper':
        if crit:
            modifier *= 1.5

    elif user.ability == 'tintedlens':
        if type_modifier < 1:
            modifier *= 2

    #--------------
    # item modifiers    
    #---------------
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

    #floor damage before applying modifier
    damage = math.floor(damage)

    damage *= modifier
    #floor again
    damage = math.floor(damage)
    if crit:
        self.log(user.fullname + " used " + move.name
                + ' doing ' + str(damage) + ' dmg with a crit!')
    else:
        self.log(user.fullname + " used " + move.name
                + ' doing ' + str(damage) + ' dmg.')

        return damage

def accuracy_check(self, user, move, target):
    '''
    check if the move works

    check specific move requirements to not fail
    at the end check accuracy

    a False return here ends the run_move method
    '''

    if user.status == 'par' and random.random() < 0.25:
        # full paralyze
        self.log(user.fullname + " is fully paralyzed.")
        return False
    # asleep pokemon miss unless they use snore or sleeptalk
    elif user.status == 'slp':
        if not move.sleep_usable:

            self.log(user.fullname + " is asleep.")
            return False

    if 'protect' in target.volatile_statuses and move.flags.protect:
        self.log(target.fullname + ' is protected from ' + user.fullname + "'s " + move.name)
        return False
    if 'banefulbunker' in target.volatile_statuses and move.flags.protect:
        self.log(target.fullname + ' is protected from ' + user.fullname + "'s " + move.name)
        return False
    if 'spikyshield' in target.volatile_statuses and move.flags.protect:
        self.log(target.fullname + ' is protected from ' + user.fullname + "'s " + move.name)
        return False
    if 'kingsshield' in target.volatile_statuses and move.flags.protect and move.category != 'Status':
        self.log(target.fullname + ' is protected from ' + user.fullname + "'s " + move.name)
        return False


    # protect moves accuracy
    if move.id in ['protect', 'detect', 'endure', 'wide guard', 'quick guard', 'spikyshield', 'kingsshield', 'banefulbunker']:
        rand_float = random.random()
        n = user.protect_n
        user.protect_n += 3
        #print(str(self.rng) + " " + str(n))
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


    # fake out
    if move.id == 'fakeout' and user.active_turns > 1:
        return False

    # taunt
    if move.category == 'Status' and 'taunt' in user.volatile_statuses:
        self.log(user.name + ' failed to move because of taunt')
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
    temp = random.randint(0, 99)
    accuracy = user.get_accuracy()
    evasion = target.get_evasion()
    check = 100
    if self.rng:
        check = (move.accuracy * accuracy * evasion)
    if temp >= check:
        self.log(user.name + " used " + move.name + " but it missed!")
    return temp < check 

def choose(self, side_id, choice):
    if isinstance(choice, list):
        self.sides[side_id].choice = choice
    else:
        self.sides[side_id].choice[0] = choice 

def boosts_statuses(self, user, move, target):
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


def update_move_before_running(self, user, move, target):
    '''
    returns the new move reference

    some moves need to have their info updated based on the current state
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
        for pokemon in user.side.pokemon:
            power += (dex.pokedex[pokemon.id].baseStats.attack / 10) + 5
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
        weight = dex.pokedex[target.id].weightkg
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

    if move.recoil.damage != 0:
        if move.recoil.condition == 'always':
            if move.recoil.type == 'maxhp':
                user.damage(move.recoil.damage, flag='percentmaxhp')


    return move

def unique_moves_after_damage(self, user, move, target, damage):
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
    if move.id == 'aromatherapy' or move.id == 'healbell': 
        for pokemon in user.side.pokemon:
            pokemon.cure_status()


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
        target.side.side_condition = set()

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

        user.stats._replace(defense = avg_def)
        target.stats._replace(defense = avg_def)

        user.stats._replace(specialdefense = avg_spd)
        target.stats._replace(specialdefense = avg_spd)

    # guard swap
    if move.id == 'guardswap':
        user_def = user.stats.defense
        target_def = target.stats.defense

        user_spd = user.stats.specialdefense
        target_spd = target.stats.specialdefense

        user.stats._replace(defense = target_def)
        target.stats._replace(defense = user_def)

        user.stats._replace(specialdefense = target_spd)
        target.stats._replace(specialdefense = user_spd)

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
        user.hp = avg_hp if avg_hp < user.maxhp else user.maxhp
        target.hp = avg_hp if avg_hp < target.maxhp else target.maxhp

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

        user.stats._replace(specialattack = user_atk)
        user.stats._replace(attack = user_spa)

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
        if not user.substitute and user.hp > user.maxhp*0.25:
            user.substitute = True
            user.damage(0.25, flag='percentmaxhp')
            user.substitute_hp = math.floor(0.25 * user.maxhp)

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

def ai_decide(self):
    self.choice = self.ai.decide(self.battle)

    # if the ai failed to make a decision
    if self.choice is None:
        self.default_decide()

    # update some flags
    if self.choice.type == 'switch':
        self.active_pokemon.is_switching = True

def default_decide(self):
    #n = 2 if self.battle.doubles else 1
    n = len(self.active_pokemon)
    for i in range(n):

        if self.request[i] == 'switch':
            for pokemon in self.pokemon:
                if pokemon.fainted == False:
                    self.choice[i] = dex.Decision('switch', pokemon.position)

        elif self.request[i] == 'pass':
            self.choice[i] = dex.Decision('pass', 0)

        elif self.request[i] == 'move':
            if len(self.active_pokemon[i].moves) > 0:
                rand_int = random.randint(0, len(self.active_pokemon[i].moves)-1)
                self.choice[i] = dex.Decision('move', rand_int)
            else:
                self.choice[i] = dex.Decision('move', 'struggle')

def populate_team(self, team):
    if team == None:
        self.team = generate_team()
    else:
        self.team = team

    for i in range(len(self.team)):
        self.pokemon.append(Pokemon(self.team[i], self.id, self, self.battle))
        self.pokemon[i].position = i

    for pokemon in self.pokemon:
        self.bench.append(pokemon)

    self.pokemon_left = len(self.pokemon)

    self.throw_out(self.pokemon[0])
    if self.battle.doubles:
        self.throw_out(self.pokemon[1])


# use this method to handle on entry things like abilities
def throw_out(self, pokemon):
    if not pokemon in self.bench:
        return False
    if pokemon.fainted:
        return False
    self.bench.remove(pokemon)
    self.active_pokemon.append(pokemon)
    pokemon.active = True

# switch the active pokemon to the pokemon in index: position
def switch(self, user, position):
    if 'cantescape' in user.volatile_statuses and not user.fainted:
        return False
    if 'partiallytrapped' in user.volatile_statuses and not user.fainted and 'Ghost' not in user.types:
        return False

    if self.battle.doubles and self.pokemon_left == 1:
        self.active_pokemon.remove(user)
        self.battle.active_pokemon.remove(user)
        return

    # if the selected pokemon is fainted or is already on the field do a default switch
    if self.pokemon[position].fainted or self.pokemon[position].active:
        return self.default_switch(user)

    pokemon_out = user
    pokemon_in = self.pokemon[position]

    #switch
    # update the sides active pokemon
    pos = self.active_pokemon.index(pokemon_out)
    self.active_pokemon[pos] = pokemon_in

    # update the battles active pokemon
    pos = self.battle.active_pokemon.index(pokemon_out)
    self.battle.active_pokemon[pos] = pokemon_in

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

    self.battle.log(pokemon_out.fullname
            + ' switches out for '
            + pokemon_in.fullname)
    return True

# switch to the first non-fainted pokemon on your team
def default_switch(self, user):
    if not self.pokemon_left:
        raise ValueError('There are no pokemon left but we are trying to switch!')

    for pokemon in self.bench:
        if not pokemon.fainted and not pokemon.active:
            self.switch(user, pokemon.position)
            return True

def form_change(self, species):
    self.species = species
    self.id = self.species
    self.template = dex.pokedex[self.species]
    self.base_ability = self.template.abilities.normal0
    self.base_ability = re.sub(r'\W+', '', self.base_ability.lower())
    self.ability = self.base_ability
    self.types = self.template.types
    self.calculate_stats()
    self.hp = self.stats.hp
    self.maxhp = self.hp

def mega_evolve(self):
    canmega = False
    if self.item != '' and dex.item_dex[self.item].megaStone is not None:
        megaspecies = re.sub(r'\W+', '', dex.item_dex[self.item].megaStone.lower())
        if re.sub(r'\W+', '', dex.item_dex[self.item].megaEvolves.lower()) == self.species:
            canmega = True


    if canmega:
        # overwrite the current pokemon with the mega form
        self.species = megaspecies
        self.template = dex.pokedex[self.species]
        self.base_ability = self.template.abilities.normal0
        self.base_ability = re.sub(r'\W+', '', self.base_ability.lower())
        self.ability = self.base_ability
        self.types = self.template.types
        self.calculate_stats()
        self.hp = self.stats.hp
        self.maxhp = self.hp

def can_z(self, move):
    item = dex.item_dex[self.item]
    if self.side.used_zmove:
        return False
    if item.zMoveType is not None and move.type != item.zMoveType:
        return False
    if item.zMoveUser is not None and self.name not in item.zMoveUser:
        return False
    if item.zMoveFrom is not None and move.name != item.zMoveFrom:
        return False
    return True

def cure_status(self):
    if self.status == '':
        return False
    self.toxic_n = 1
    self.status = ''
    return True

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


def get_attack(self, crit=False):
    modifier = dex.boosts[self.boosts['atk']]
    if crit and modifier < 1:
        modifier = 1
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

def get_defense(self, crit):
    modifier = dex.boosts[self.boosts['def']]
    if crit and modifier > 1:
        modifier = 1
    if self.ability == 'marvelscale' and self.status != '':
        modifier *= 1.5
    if self.ability == 'grasspelt' and self.battle.terrain == 'grassy':
        modifier *= 1.5
    if self.species == 'ditto' and self.item == 'metalpowder':
        modifier = 2
    if self.template.evos is not None and self.item == 'eviolite':
        modifier = 1.5
    return self.stats.defense * modifier

def get_specialattack(self, crit):
    modifier = dex.boosts[self.boosts['spa']]
    if crit and modifier < 1:
        modifier = 1
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

def get_specialdefense(self, crit):
    modifier = dex.boosts[self.boosts['spd']]
    if crit and modifier > 1:
        modifier = 1
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

def damage(self, amount, flag=None):
    old_hp = self.hp
    if self.fainted:
        return 0
    if flag is None:
        self.hp -= math.floor(amount)
    elif flag == 'percentmax':
        damage = math.floor(self.maxhp*amount)
        self.hp -= damage
    elif flag == 'percentmaxhp':
        damage = math.floor(self.maxhp*amount)
        self.hp -= damage
    elif flag == 'percentcurrent':
        damage = math.floor(self.hp*amount)
        self.hp -= damage

    if 'endure' in self.volatile_statuses and self.hp < 1:
        self.hp = 1
        self.battle.log(self.name + ' endured with 1 hp')
    if self.hp > self.maxhp:
        self.hp = self.maxhp

    diff_hp = old_hp - self.hp
    if diff_hp > 0:
        self.battle.log(self.name + ' took ' + str(diff_hp) + ' dmg')
    elif diff_hp < 0:
        self.battle.log(self.name + ' healed ' + str(-(diff_hp)) + ' hp')

    if self.hp <= 0:
        self.faint()
    return diff_hp

def faint(self):
    self.volatile_statuses = set()
    self.battle.log(self.fullname + ' fainted')
    self.trapped = False
    self.hp = 0
    self.fainted = True
    self.side.pokemon_left -= 1

def json_to_genome(json):
    '''
    takes the dict/json format and returns the value encoded genome

        species: string,
        moves: [string, string, string, string],
        item: string,
        ability: string,
        nature: string
        evs: [int, int, int, int, int, int],
        ivs: [int, int, int, int, int, int],

        use the index number of each
        [species, moves, ability, nature, item, evs, ivs]
    '''
    genome = [0]*20
    genome[0] = dex.pokedex[json['species']].num
    for i in range(len(json['moves'])):
        genome[i+1] = dex.move_dex[json['moves'][i]].num
    genome[5] = dex.ability_dex[json['ability']].num
    genome[6] = dex.nature_dex[json['nature']].num
    genome[7] = dex.item_dex[json['item']].num
    for i in range(len(json['evs'])):
        genome[i+8] = json['evs'][i]
    for i in range(len(json['ivs'])):
        genome[i+14] = json['ivs'][i]

    return genome

def genome_to_json(genome):
    pokemon = {}
    pokemon['species'] = dex.index_to_id_pokemon[genome[0]]
    pokemon['moves'] = []
    for i in range(4):
        if genome[i+1] != 0:
            pokemon['moves'].append(dex.index_to_id_moves[genome[i+1]])
    pokemon['ability'] = dex.index_to_id_abilities[genome[5]]
    pokemon['nature'] = dex.index_to_id_natures[genome[6]]
    try:
        pokemon['item'] = dex.index_to_id_items[genome[7]]
    except KeyError:
        pokemon['item'] = '' 
    pokemon['evs'] = []
    pokemon['ivs'] = []
    for i in range(6):
        pokemon['evs'].append(genome[i+8])
    for i in range(6):
        pokemon['ivs'].append(genome[i+14])

    return pokemon

def encode_team(team):
    '''
    takes array of json-coded pokemon
    '''
    genome = []
    for pokemon in team:
        genome = genome + json_to_genome(pokemon)
    return genome

def decode_team(genome):
    team = []
    for i in range((len(genome)//20)):
        team.append(genome_to_json(genome[i*20:(i+1)*20]))
    return team

