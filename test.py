from player import Player
from battle import Battle
from picksix import generateTeam
import time

format = 'vgc2018'

p1 = Player('nick', 'p1')
p2 = Player('sam', 'p2')

t0 = time.time() 

for i in range(1, 10):
    battle = Battle(format)
    print('battle number',  i)

    team1 = generateTeam()
    team2 = generateTeam()

    battle.join('p1', p1.name, None, team1)
    battle.join('p2', p2.name, None, team2)

    while not battle.ended:
        battle.choose(p1.side, p1.decide(battle))
        battle.choose(p2.side, p2.decide(battle))

    print(battle.winner)


t1 = time.time()
print (t1-t0)
