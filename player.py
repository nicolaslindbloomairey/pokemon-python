import random
import math

class Player:
    def __init__(self, name, side):
        self.name = name
        self.side = side

def decide(self, state):
    if state[self.side].currentRequest == 'teampreview':
        slots = ['1', '2', '3', '4', '5', '6']
        team = ''
        for i in range(0, 4):
            team = team + slots.remove(random.choice(slots))

            return 'team ' + team

        elif state[self.side].currentRequest == 'switch':
            pass

        elif state[self.side].currentReqest == 'move':
            loc = ['', '']
            move = [None, None]
            decision = ''

            for i in range(len(state[self.side].active)):
                if state[self.side].active[i].fainted == False:

                    move[i] = random.randint(0,3)
                    if state[self.side].active[i].moveset[move[i]-1].target == 'normal':
                        loc[i] = ' ' + random.randint(0,1)
                    elif state[self.side].active[i].moveset[move[i]-1].target == 'adjacentAlly':
                        loc[i] = ' -2' if i == 0 else ' -1'
                    elif state[self.side].active[i].moveset[move[i]-1].target == 'allAdjacentFoes':
                        loc[i] = '' 
                    elif state[self.side].active[i].moveset[move[i]-1].target == 'self':
                        loc[i] = ''
                    elif state[self.side].active[i].moveset[move[i]-1].target == 'allySide':
                        loc[i] = ''
                    else:
                        return 'default'

                    decision = decision + 'move ' + state[self.side].active[i].moves[move[i]-1] + '' + loc[i]
                    if i == 0 and state[self.side].active[1].fainted == False:
                        decision = decision + ','

            return decision

        else:
            return 'default'

