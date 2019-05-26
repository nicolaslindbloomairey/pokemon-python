from sim.battle import Battle
import new_sim.sim as Sim
from tools.pick_six import generate_team
import json
import pprint


teams = []
for i in range(2):
    teams.append(Sim.dict_to_team_set(generate_team()))

battle = Sim.Battle('single', 'Nic', teams[0], 'Sam', teams[1])

battle.run()
