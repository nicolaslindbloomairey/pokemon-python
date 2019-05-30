import sim.sim as sim
from tools.pick_six import generate_team
import time
import json


with open('data/sample_teams.json') as f:
    sample_teams = json.load(f)

t0 = time.time()

zero = 0
one = 0
error = 0
turncount = 0
num_battles = 5000 
johtoxalola = sim.dict_to_team_set(sample_teams['johtoxalola'])
genetic = sim.dict_to_team_set(sample_teams['secondgeneticsearch'])
teams = []
for i in range(2):
    teams.append(sim.dict_to_team_set(generate_team()))
p1 = 'Nic'
p2 = 'Sam'

most_turns = 0

for i in range(num_battles):

    battle = sim.Battle('single', p1, johtoxalola, p2, teams[1], debug=False)

    sim.run(battle)

    if battle.winner == 'p1':
        zero += 1
    elif battle.winner == 'p2':
        one += 1
    else:
        error += 1

    if battle.turn > most_turns:
        most_turns = battle.turn
    turncount += battle.turn

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
print(str(error) + " battles ended reached max turn length")
print(str(most_turns) + " was the max number of turns in a battle")
