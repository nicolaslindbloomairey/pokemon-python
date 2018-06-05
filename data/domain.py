import json
with open('pokedex.json') as f:
    pokedex = json.load(f)

domain_all = []

num = 1
for pokemon in pokedex:
    if pokedex[pokemon]['num'] == num:
        domain_all.append(pokemon)
        num += 1

print(str(domain_all))
print(str(len(domain_all)))
with open('domains/all.json', 'w') as outfile:
    json.dump(domain_all, outfile)
