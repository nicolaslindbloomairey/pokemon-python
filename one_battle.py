import sim.sim as sim
from tools.pick_six import generate_team

teams = []
for i in range(2):
    teams.append(sim.dict_to_team_set(generate_team()))

battle = sim.Battle('single', 'Nic', teams[0], 'Sam', teams[1], debug=True)
print(battle.p1.pokemon)

sim.run(battle)
