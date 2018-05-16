#from dex import ModdedDex
from sim.side import Side
import data.dex as dex
import random
import math

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
        self.turn = 0
        self.winner = None
        self.ended = False
        self.started = False
        self.request = 'move'

    def join(self, side_id, team=None):
        self.sides[side_id].populate_team(team)

    #method that runs the entire battle
    def run(self):
        self.join(0)
        self.join(1)
        while not self.ended:
            self.sides[0].choice = self.sides[0].ai.decide(self) 
            self.sides[1].choice = self.sides[1].ai.decide(self) 
            self.do_turn()
            if self.turn > 500:
                print('ERROR TURN COUNTER IS OVER 500')
                break

    def __str__(self):
        out = ['\n']
        out.append('Turn ' + str(self.turn) + '\n')
        out.append(str(self.sides[0].pokemon_left) + " : " + str(self.sides[1].pokemon_left) + '\n')
        for i in range(2):
            out.append(self.sides[i].name + "|" + str(self.sides[i].active_pokemon))
            out.append('\n')
        del out[-1]
        return ''.join(out)

    def do_turn(self):
        self.turn += 1
        #determine turn order
        if self.debug:
            print(self)
            '''
            print('')
            print('Turn ' + str(self.turn))
            print(str(self.sides[0].pokemon_left) + " : " + str(self.sides[1].pokemon_left))

            for i in range(2):
                print(self.sides[i].name + "|" + str(self.sides[i].active_pokemon))
            '''


        #Switches because of a fainted pokemon
        for i in range(2):
            if self.sides[i].request == 'switch':
                self.sides[i].switch()



        #Moves

        if self.request == 'move':

            if self.sides[0].choice != None and self.sides[1].choice != None:
                if self.sides[0].choice.type == 'switch' and self.sides[1].choice.type == 'switch':
                    #faster pokemon switches out first
                    #this needs fixing
                    self.sides[0].switch()
                    self.sides[1].switch()
                elif self.sides[0].choice.type != 'switch' and self.sides[1].choice.type == 'switch':
                    self.sides[1].switch()
                elif self.sides[0].choice.type == 'switch' and self.sides[1].choice.type != 'switch':
                    self.sides[0].switch()
                else:
                    pass

            #turn order by speed stat
            if self.sides[0].active_pokemon.stats.speed > self.sides[1].active_pokemon.stats.speed:
                self.run_move(self.sides[0].active_pokemon, self.sides[0].choice, self.sides[1].active_pokemon)
                self.run_move(self.sides[1].active_pokemon, self.sides[1].choice, self.sides[0].active_pokemon)
            elif self.sides[1].active_pokemon.stats.speed > self.sides[0].active_pokemon.stats.speed:
                self.run_move(self.sides[1].active_pokemon, self.sides[1].choice, self.sides[0].active_pokemon)
                self.run_move(self.sides[0].active_pokemon, self.sides[0].choice, self.sides[1].active_pokemon)
            else:
                if random.random() > 50:
                    self.run_move(self.sides[0].active_pokemon, self.sides[0].choice, self.sides[1].active_pokemon)
                    self.run_move(self.sides[1].active_pokemon, self.sides[1].choice, self.sides[0].active_pokemon)
                else:
                    self.run_move(self.sides[1].active_pokemon, self.sides[1].choice, self.sides[0].active_pokemon)
                    self.run_move(self.sides[0].active_pokemon, self.sides[0].choice, self.sides[1].active_pokemon)

#       do switches
#       mega evolution
#       priority moves
#       items, abilities
#       trick room
#       order of speed stat

#       run all the decisions

        #request the next turns move
        self.request = 'move'
        for i in range(2):
            self.sides[i].request = 'move'
        #check if a pokemon fainted and insert a pseudo turn
        for i in range(2):
            if self.sides[i].active_pokemon.fainted:
                self.sides[i].request = 'switch'
                self.request = 'switch'
                if self.sides[0 if i else 1].active_pokemon.fainted == False:
                    self.sides[0 if i else 1].request = 'pass'

#       check for a winner
#       end the while true once the game ends
        for i in range(2):
            if self.sides[i].pokemon_left == 0:
                self.ended = True
                self.winner = 0 if i else 1

    def run_move(self, user, decision, target):
        if user.fainted:
            return

        #  selection = random.randint(0, 3) if decision is not None else decision.selection
        if decision == None:
            selection = random.randint(0, 3)
        else:
            selection = decision.selection

        move = dex.move_dex[user.moves[selection]]
#       accuracy_check
        #print(self.accuracy_check(user,move,target))
        if self.accuracy_check(user, move, target):
            damage = self.damage(user, move, target)
            if self.debug:
                print(user.name + " used " + move.name + ' doing ' + str(damage) + ' dmg')
#           move hit! do damage
            #print(self.damage(user, move, target))
            target.hp -= damage
        else:
#           move missed! do noting
            if self.debug:
                print(user.name + " used " + move.name + " but it missed!")
            pass

        if target.hp <= 0:
            target.faint()


#       secondary effects
        if move.secondary != False and target.fainted != True:
            temp = random.randint(0, 99)
            check = move.secondary['chance']
            #print(str(temp) + '<' + str(check))
            if temp < check:
                if 'boosts' in move.secondary:
                    for stat in move.secondary['boosts']:
                        target.boosts[stat] += move.secondary['boosts'][stat]
                if 'status' in move.secondary:
                    status = move.secondary['status']
                    if target.status == '':
                        if status == 'brn' and ('Fire' in target.types or dex.abilities[target.ability].prevent_burn):
                            pass
                        else:
                            target.status = move.secondary['status']
                if 'volatileStatus' in move.secondary:
                    target.volatile_status.add(move.secondary['volatileStatus'])
            


    def damage(self, user, move, target):
        damage = 0
        if move.category == 'Special':
            damage = ((((((2 * user.level) / 5) + 2) * user.stats.specialattack * move.basePower / target.stats.specialdefense) / 50) + 2) 
        elif move.category == 'Physical':
            #print(str(user.level) + ' ' + str(user.stats.attack) + ' ' + str(move.basePower) + ' ' + str(user.stats.defense
            damage = ((((((2 * user.level) / 5) + 2) * user.stats.attack * move.basePower / target.stats.defense) / 50) + 2) 
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

#       apply modifier
        damage *= modifier
        #print(str(damage))

        return math.floor(damage)

    def accuracy_check(self, user, move, target):
#       returns a boolean whether the move hit the target
        temp = random.randint(0, 99)
        check = (move.accuracy * dex.accuracy[user.accuracy] * dex.evasion[target.evasion])
        #print(temp, check)
        return temp < check 
        
    def choose(self, side_id, choice):
        self.sides[side_id].choice = choice 
