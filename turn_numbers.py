from sim.battle import Battle
zero = 0
one = 0
turncount = 0
num_battles = 100
for i in range(num_battles):
    battle = Battle(False)

    battle.run()
    turncount += battle.turn
    #print(str(battle.turn))

    #print(battle.sides[battle.winner].name)
    if battle.winner == 0:
        zero += 1
    if battle.winner == 1:
        one += 1

print('average turns per battle: ' + str(turncount/num_battles))
print( str(zero) + " | " + str(one) + " | " + str(num_battles-zero-one))
