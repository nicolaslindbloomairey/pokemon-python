#from dex import ModdedDex
from side import Side
import dex as Dex
import random
import math

class Battle():
    def __init__(self):
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

    #method that runs the entire battle
    def run(self):
        while not self.ended:
            self.sides[0].choice = self.sides[0].ai.decide(self) 
            self.sides[1].choice = self.sides[1].ai.decide(self) 
            self.update()

        for i in self.activePokemon:
            print(str(i))

    def update(self):
        self.turn += 1
        #determine turn order

        for i in self.activePokemon:
            print(str(i))

        if self.activePokemon[0].stats.speed > self.activePokemon[1].stats.speed:
            self.runMove(self.activePokemon[0], self.sides[0].choice, self.activePokemon[1])
            self.runMove(self.activePokemon[1], self.sides[1].choice, self.activePokemon[0])
        elif self.activePokemon[1].stats.speed > self.activePokemon[0].stats.speed:
            self.runMove(self.activePokemon[1], self.sides[1].choice, self.activePokemon[0])
            self.runMove(self.activePokemon[0], self.sides[0].choice, self.activePokemon[1])
        else:
            if random.random() > 50:
                self.runMove(self.activePokemon[0], self.sides[0].choice, self.activePokemon[1])
                self.runMove(self.activePokemon[1], self.sides[1].choice, self.activePokemon[0])
            else:
                self.runMove(self.activePokemon[1], self.sides[1].choice, self.activePokemon[0])
                self.runMove(self.activePokemon[0], self.sides[0].choice, self.activePokemon[1])

#       do switches
#       mega evolution
#       priority moves
#       items, abilities
#       trick room
#       order of speed stat

#       run all the decisions

#       check for a winner
#       end the while true once the game ends
        for i in range(2):
            if self.sides[i].activePokemon.fainted:
                self.ended = True
                self.winner = 0 if i else 1

#       force the game to end after the first turn
#        self.ended = True

    def runMove(self, user, decision, target):
        #  selection = random.randint(0, 3) if decision is not None else decision.selection
        if decision == None:
            selection = random.randint(0, 3)
        else:
            selection = decision.selection

        print(user.name + " used " + Dex.moves[user.moves[selection]].name)
#       accuracycheck
        if self.accuracyCheck(user, decision, target):
#           move hit! do damage
            target.hp -= self.damage(user, Dex.moves[user.moves[selection]], target)
        else:
#           move missed! do noting
            pass

        if target.hp <= 0:
            target.hp = 0
            target.fainted = True

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
        return random.randint(0, 99) < (move.accuracy * user.accuracy * target.evasion)
        

    def determineTurnOrder(self):
        queue = []

#    def join(self, team):
#        if len(self.sides) < 2:
#            self.sides.append(Side(team))
#
#        if len(self.sides) = 2:
#            self.start()

