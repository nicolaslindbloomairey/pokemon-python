#from dex import ModdedDex
from side import Side
import dex as Dex
import random
import math

class Battle():
    def __init__(self, debug=True):
        self.debug = debug
        self.sides = []
        self.activePokemon = []
        for i in range(2):
            self.sides.append(Side(self, i))
            self.activePokemon.append(self.sides[i].activePokemon)
        self.status = ''

        self.weather = ''
        self.turn = 0
        self.winner = None
        self.ended = False
        self.started = False
        self.request = 'move'

    #method that runs the entire battle
    def run(self):
        while not self.ended:
            self.sides[0].choice = self.sides[0].ai.decide(self) 
            self.sides[1].choice = self.sides[1].ai.decide(self) 
            self.doTurn()
            #if self.turn > 5:
            #    break

    def doTurn(self):
        self.turn += 1
        #determine turn order
        if self.debug:
            print('')
            print('Turn ' + str(self.turn))
            print(str(self.sides[0].pokemonLeft) + " : " + str(self.sides[1].pokemonLeft))

            for i in range(2):
                print(self.sides[i].name + "| " + str(self.sides[i].activePokemon))


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

            #turn order by speed stat
            if self.sides[0].activePokemon.stats.speed > self.sides[1].activePokemon.stats.speed:
                self.runMove(self.sides[0].activePokemon, self.sides[0].choice, self.sides[1].activePokemon)
                self.runMove(self.sides[1].activePokemon, self.sides[1].choice, self.sides[0].activePokemon)
            elif self.sides[1].activePokemon.stats.speed > self.sides[0].activePokemon.stats.speed:
                self.runMove(self.sides[1].activePokemon, self.sides[1].choice, self.sides[0].activePokemon)
                self.runMove(self.sides[0].activePokemon, self.sides[0].choice, self.sides[1].activePokemon)
            else:
                if random.random() > 50:
                    self.runMove(self.sides[0].activePokemon, self.sides[0].choice, self.sides[1].activePokemon)
                    self.runMove(self.sides[1].activePokemon, self.sides[1].choice, self.sides[0].activePokemon)
                else:
                    self.runMove(self.sides[1].activePokemon, self.sides[1].choice, self.sides[0].activePokemon)
                    self.runMove(self.sides[0].activePokemon, self.sides[0].choice, self.sides[1].activePokemon)

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
            if self.sides[i].activePokemon.fainted:
                self.sides[i].request = 'switch'
                self.request = 'switch'
                if self.sides[0 if i else 1].activePokemon.fainted == False:
                    self.sides[0 if i else 1].request = 'pass'

#       check for a winner
#       end the while true once the game ends
        for i in range(2):
            if self.sides[i].pokemonLeft == 0:
                self.ended = True
                self.winner = 0 if i else 1

    def runMove(self, user, decision, target):
        if user.fainted:
            return

        #  selection = random.randint(0, 3) if decision is not None else decision.selection
        if decision == None:
            selection = random.randint(0, 3)
        else:
            selection = decision.selection

        move = Dex.moves[user.moves[selection]]
#       accuracycheck
        #print(self.accuracyCheck(user,move,target))
        if self.accuracyCheck(user, move, target):
            if self.debug:
                print(user.name + " used " + move.name)
#           move hit! do damage
            #print(self.damage(user, move, target))
            target.hp -= self.damage(user, move, target)
        else:
#           move missed! do noting
            if self.debug:
                print(user.name + " used " + move.name + " but it missed!")
            pass

        if target.hp <= 0:
            target.faint()

        if not target.fainted:
#           secondary effects on target
            pass

#       secondary effects


    def damage(self, user, move, target):
        damage = 0
        if move.category == 'Special':
            damage  = (((( ((2 * user.level) / 5) + 2) * user.stats.specialattack * move.basePower / user.stats.specialdefense) / 50) + 2) 
        elif move.category == 'Physical':
            damage = ((((2 * user.level / 5 + 2) * user.stats.attack * move.basePower / user.stats.defense) / 50) + 2) 
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
        modifier *= random.uniform(0.85, 1.0)
#       STAB      
        if move.type in user.types:
            modifier *= 1.5
#       type effectiveness
        for each in target.types:
#            modifier *= getattr(getattr(Dex.typecharts, each).damageTaken, move.type)
            modifier *= Dex.typecharts[each].damageTaken[move.type]
#       burn
        if user.burned and move.category == 'Physical' and user.ability != 'guts':
            modifier *= 0.5
#       other

#       apply modifier
        damage *= modifier

        return math.floor(damage)

    def accuracyCheck(self, user, move, target):
#       returns a boolean whether the move hit the target
        temp = random.randint(0, 99)
        check = (move.accuracy * Dex.accuracy[user.accuracy] * Dex.evasion[target.evasion])
        #print(temp, check)
        return temp < check 
        

    def determineTurnOrder(self):
        queue = []

#    def join(self, team):
#        if len(self.sides) < 2:
#            self.sides.append(Side(team))
#
#        if len(self.sides) = 2:
#            self.start()

