from sim.battle import Battle


'''
zero = 0
one = 0
for i in range(50):
    battle = Battle(False)

    battle.run()

    #print(battle.sides[battle.winner].name)
    if battle.winner == 0:
        zero += 1
    if battle.winner == 1:
        one += 1

print( str(zero) + " | " + str(one))
'''

battle = Battle()
battle.run()
print(battle.sides[battle.winner].name)
