from sim.battle import Battle
from tools.pick_six import generate_team
import time

t0 = time.time()

zero = 0
one = 0
turncount = 0
num_battles = 200
teams = [generate_team(), generate_team()]

for i in range(num_battles):
    battle = Battle(doubles=False, debug=False)
    
    battle.join(team=teams[0])
    battle.join(team=teams[1])

    battle.run()
    turncount += battle.turn
    #print(str(battle.turn))

    #print(battle.sides[battle.winner].name)
    if battle.winner == 0:
        zero += 1
    if battle.winner == 1:
        one += 1

t1 = time.time()
avg_turns = turncount/num_battles
total_time = t1-t0
avg_time = round((total_time*1000) / num_battles, 2)
avg_time_turn = round( total_time*1_000_000 / num_battles / avg_turns, 2)
print('number of battles: ' + str(num_battles))
print('average turns per battle: ' + str(avg_turns))
print('total time: ' + str(round(total_time, 2)) + ' s')
print('average time per battle: ' + str(avg_time) + ' ms')
print('average time per turn: ' + str(avg_time_turn) + ' us')
print( str(zero) + " | " + str(one) + " | " + str(num_battles-zero-one))
