from sim.side import Side
from data import dex
import random
import math
import heapq
import re

class Battle(object):
    def __init__(self, debug=True, rng=True):
        self.rng = rng
        self.debug = debug
        self.sides = []
        self.active_pokemon = []
        for i in range(2):
            self.sides.append(Side(self, i))
            self.active_pokemon.append(self.sides[i].active_pokemon)
        self.status = ''

        self.weather = ''
        self.terrain = ''
        self.turn = 0
        self.winner = None
        self.ended = False
        self.started = False
        #self.request = 'real'
        self.pseudo_turn = False
        self.trickroom = False

    def join(self, side_id, team=None):
        self.sides[side_id].populate_team(team)

    #method that runs the entire battle
    def run(self):
        self.join(0)
        self.join(1)
        while not self.ended:

            # let the ai pick what each side will do
            for side in self.sides:
                side.ai_decide()

            self.do_turn()

            if self.turn > 500:
                print('ERROR TURN COUNTER IS OVER 500')
                break

    def __str__(self):
        out = ['\n']
        out.append('Turn ' + str(self.turn) + '\n')
        out.append(str(self.sides[0].pokemon_left)
                       + " : "
                       + str(self.sides[1].pokemon_left)
                       + '\n')
        for i in range(2):
            out.append(self.sides[i].name
                       + "|"
                       + str(self.sides[i].active_pokemon))
            out.append('\n')
            out.append(str(self.sides[i].choice))
            out.append('\n')
        del out[-1]
        return ''.join(out)

    def populate_action_queue(self, action_queue):
        for side in self.sides:
            # add the switches to the queue
            if side.choice.type == 'switch':
                user = side.active_pokemon
                move = 'switch'
                target = side.choice.selection
                action = dex.Action(user, move, target) 
                action_tuple = (self.resolve_priority(action), action)

                heapq.heappush(action_queue, action_tuple)

            # add the moves to the queue
            elif side.choice.type == 'move':
                
                # add the mega evolutions as a seperate action
                if side.choice.mega:
                    user = side.active_pokemon
                    move = 'mega'
                    action = dex.Action(user, move)
                    action_tuple = (self.resolve_priority(action), action)

                    heapq.heappush(action_queue, action_tuple)

                user = side.active_pokemon

                # if the move is Z
                move = dex.move_dex[user.moves[side.choice.selection]]
                if side.choice.zmove and user.can_z(move):
                    item = dex.item_dex[user.item]
                    if item.zMove is True:
                        zmove_id = dex.zmove_chart[item.id]
                    else:
                        zmove_id = re.sub(r'\W+', '', item.zMove.lower())
                    base_move = move
                    move = dex.move_dex[zmove_id]

                    # update the zmove power 
                    if move.basePower == 1:
                        move = move._replace(basePower = base_move.zMovePower)

                # actually add the moves to the queue
                if move.target == 'self':
                    target = side
                elif move.target == 'normal':
                    target = self.sides[0 if side.id else 1]
                else:
                    target = self.sides[0 if side.id else 1]
                action = dex.Action(user, move, target)
                action_tuple = (self.resolve_priority(action), action)

                heapq.heappush(action_queue, action_tuple)

            else:
                # dont add any action to the queue
                # this is here for the 'pass' decision
                pass
                

    def do_turn(self):
        '''
        to be called once both sides have made their decisions
        
        updates the game state according to the decisions
        '''

        for side in self.sides:
            side.active_pokemon.volatile_statuses = set()

            if side.choice is None:
                # error - one or more sides is missing a decsion
                raise ValueError('one or more sides is missing a decision')

        self.turn += 1

        for side in self.sides:
            side.active_pokemon.active_turns += 1

        # print the state of the battle
        if self.debug:
            print(self)


        # create priority queue and references to both sides
        action_queue = []

        # populate action queue
        self.populate_action_queue(action_queue)

        # run each each action in the queue
        while action_queue:
            priority, next_action = heapq.heappop(action_queue) 
            if self.debug:
                print(str(priority))
            self.run_action(next_action)

        # do status checks
        for side in self.sides:
            pokemon = side.active_pokemon
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


        #request the next turns move
        self.request = 'move'
        for i in range(2):
            self.sides[i].request = 'move'
        #check if a pokemon fainted and insert a pseudo turn
        for i in range(2):
            if self.sides[i].active_pokemon.fainted:
                # flag this side for a switch
                self.sides[i].request = 'switch'
                self.pseudo_turn = True
                if self.sides[0 if i else 1].active_pokemon.fainted == False:
                    self.sides[0 if i else 1].request = 'pass'

#       check for a winner
#       end the while true once the game ends
        for side in self.sides:
            if not side.pokemon_left:
                self.ended = True
                self.winner = side.id

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

        elif action.move.id == 'pursuit' and action.target.active_pokemon.is_switching:
            action_priority_tier = 0

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
        # action is set up three different ways

        # one way for switches
        if action.move == 'switch':
            action.user.side.switch(action.target)

        # another for mega evolutions
        elif action.move == 'mega':
            action.user.mega_evolve()

        # and lastly for moves
        else:
            self.run_move(action.user, action.move, action.target.active_pokemon)


    def run_move(self, user, move, target):
        if user.fainted:
            if self.debug:
                print(user.name + " fainted before they could move")
            return

        # accuracy_check
        if not self.accuracy_check(user, move, target):
            # move missed! do noting
            if self.debug:
                print(user.name + " used " + move.name + " but it missed!")
            return

        if move.isZ is not None:
            user.side.used_zmove = True

        #move hit, continue

        damage = self.damage(user, move, target)

        if self.debug:
            print(user.name + " used " + move.name
                  + ' doing ' + str(damage) + ' dmg')

        target.damage(damage)
        if move.drain is not None:
            user.damage(-(math.floor(damage * move.drain[0] / move.drain[1])))

        # stat changing moves
        if move.boosts is not None:
            target.boost(move.boosts)
        if move.volatileStatus is not None:
            target.volatile_statuses.add(move.volatileStatus)

        if move.self is not None:
            if 'boosts' in move.self:
                user.boost(move.self['boosts'])
            if 'volatileStatus' in move.self:
                target.volatile_statuses.add(move.self['volatileStatus'])

        # primary effects
        if move.status is not None and target.fainted != True:
            if target.status == '':
                target.status = move.status

        # accupressure
        # raises a random stat that is not maxed already by 2
        if move.id == 'acupressure':
            possible_stats = [stat for stat in user.boosts if user.boosts[stat] < 6]

            if len(possible_stats) > 0:
                rand_int = random.randint(0, len(possible_stats)-1)
                boost_stat = possible_stats[rand_int]
                user.boosts[boost_stat] += 2
                if user.boosts[boost_stat] > 6:
                    user.boosts[boost_stat] = 6


        


        # secondary effects
        if move.secondary is not None and target.fainted != True:
            temp = random.randint(0, 99)
            check = move.secondary['chance']
            #print(str(temp) + '<' + str(check))
            if temp < check:
                if 'boosts' in move.secondary:
                    target.boost(move.secondary['boosts'])
                if 'status' in move.secondary:
                    status = move.secondary['status']
                    if target.status == '':
                        if status == 'brn' and ('Fire' in target.types or dex.ability_dex[target.ability].prevent_burn):
                            pass
                        if status == 'par' and ('Electric' in target.types or dex.ability_dex[target.ability].prevent_par):
                            pass
                        if status == 'psn' and (('Poison' in target.types or 'Steel' in target.types) and user.ability != 'corosion'):
                            pass
                        if status == 'psn' and dex.ability_dex[target.ability].prevent_psn:
                            pass
                        if status == 'slp' and dex.ability_dex[target.ability].prevent_slp:
                            pass
                        else:
                            target.status = move.secondary['status']
                if 'volatileStatus' in move.secondary:
                    target.volatile_statuses.add(move.secondary['volatileStatus'])

        # tertiary effects only exist for Ice Fang, Fire Fang, and Thunder Fang
        if move.tertiary is not None and target.fainted != True:
            temp = random.randint(0, 99)
            check = move.tertiary['chance']
            #print(str(temp) + '<' + str(check))
            if temp < check:
                if 'boosts' in move.tertiary:
                    target.boost(move.secondary['boosts'])
                if 'status' in move.tertiary:
                    status = move.tertiary['status']
                    if target.status == '':
                        if status == 'brn' and ('Fire' in target.types or dex.ability_dex[target.ability].prevent_burn):
                            pass
                        else:
                            target.status = move.tertiary['status']
                if 'volatileStatus' in move.tertiary:
                    target.volatile_statuses.add(move.tertiary['volatileStatus'])
            


    def damage(self, user, move, target):
        damage = 0

        power = move.basePower
        if move.id == 'acrobatics' and user.item == '':
            power *= 2
        
        if move.category == 'Special':
            damage = ((((((2 * user.level) / 5) + 2) * user.get_specialattack() * power / target.get_specialdefense()) / 50) + 2) 
        elif move.category == 'Physical':
            damage = ((((((2 * user.level) / 5) + 2) * user.get_attack() * power / target.get_defense()) / 50) + 2) 
        elif move.category == 'Status':
            pass

#       multiply the damge by each modifier
        modifier = 1

#       0.75 if move has multiple targets, 1 otherwise
#       weather
        if self.weather == 'rain':
            if move.type == 'Water':
                modifier *= 1.5
            elif move.type == 'Fire':
                modifier *= 0.5
        elif self.weather == 'sunlight':
            if move.type == 'Water':
                modifier *= 0.5
            elif move.type == 'Fire':
                modifier *= 1.5
        else:
            modifier *= 1.0
#       if crit *=1.5
#       random float
        if (self.rng):
            modifier *= random.uniform(0.85, 1.0)
#       STAB      
        if move.type in user.types:
            modifier *= 1.5
#       type effectiveness
        for each in target.types:
            modifier *= dex.typechart_dex[each].damage_taken[move.type]
#       burn
        if user.burned and move.category == 'Physical' and user.ability != 'guts':
            modifier *= 0.5
#       other
        if move.isZ is not None and 'protect' in target.volatile_statuses:
            modifier *= 0.25

        #floor damage before applying modifier
        damage = math.floor(damage)
#       apply modifier
        damage *= modifier
        #print(str(damage))

        return math.floor(damage)

    def accuracy_check(self, user, move, target):
        #if not self.rng:
        #    return True

        # moves hitting protect
        #print(str(target.volatile_statuses))
        #print(str(move.flags))

        if user.status == 'par' and random.random() < 0.25:
            # full paralyze
            return False
        # asleep pokemon miss unless they use snore or sleeptalk
        elif user.status == 'slp':
            if move.id != 'snore' and move.id != 'sleeptalk':
                return False

            
        if 'protect' in target.volatile_statuses and 'protect' in move.flags:
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

        if move.accuracy is True:
            return True

        # fake out
        if move.id == 'fakeout' and user.active_turns > 1:
            return False
        # returns a boolean whether the move hit the target
        temp = random.randint(0, 99)
        accuracy = user.get_accuracy()
        evasion = target.get_evasion()
        check = 100
        if self.rng:
            check = (move.accuracy * accuracy * evasion)
        return temp < check 
        
    def choose(self, side_id, choice):
        self.sides[side_id].choice = choice 
