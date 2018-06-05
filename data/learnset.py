import json
import math
def ncr(n, r):
    if r > n:
        r = n
    f = math.factorial
    return f(n) // f(r) // f(n-r)

with open('learnsets.json') as f:
    learnsets = json.load(f)
with open('pokedex.json') as f:
    pokedex = json.load(f)

simple_learnsets = {}

count = 1
for pokemon in learnsets:
    simple_learnsets[pokemon] = list(set(list(learnsets[pokemon]['learnset'].keys())))
    num_moves = len(simple_learnsets[pokemon])
    combinations = ncr(num_moves, 4)
    count *= combinations
    print(pokemon + " " + str(num_moves))

team_combo = ncr(807, 6)
print(str(count*team_combo))
#with open('simple_learnsets.json', 'w') as outfile:
#    json.dump(simple_learnsets, outfile)
