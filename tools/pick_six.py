import random
import json
import numpy
import re
import os
from data import dex
#from collections import namedtuple
#Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../data/vgcreformated.json"
abs_file_path = os.path.join(script_dir, rel_path)

with open(abs_file_path) as f:
    vgc = json.load(f)
with open('data/domains/all.json') as f:
    domain_all = json.load(f)


def generate_vgc_team():

    probs = numpy.array([p['usage'] for p in vgc])
    probs /= probs.sum()
    names = numpy.random.choice([o['name'] for o in vgc], 6, False, probs)

    team = []
    for data in [o for o in vgc if o['name'] in names]:
        pokemon = {
            'name': data['name'],
            'species': data['name'],
            'id': data['id'],
            'level': 50
            #'gender': ''
        }

        pokemon['moves'] = numpy.random.choice(list(data['moves'].keys()), 4, False, numpy.array(list(data['moves'].values())) / numpy.array(list(data['moves'].values())).sum())
        pokemon['item'] = numpy.random.choice(list(data['items'].keys()), replace=False, p=numpy.array(list(data['items'].values())) / numpy.array(list(data['items'].values())).sum())
        pokemon['ability'] = numpy.random.choice(list(data['abilities'].keys()), replace=False, p=numpy.array(list(data['abilities'].values())) / numpy.array(list(data['abilities'].values())).sum())
        pokemon['nature'] = numpy.random.choice(list(data['natures'].keys()), replace=False, p=numpy.array(list(data['natures'].values())) / numpy.array(list(data['natures'].values())).sum())

        divs = numpy.sort(numpy.random.randint(128, size=5)).tolist()
        divs.insert(0, 0)
        divs.append(127)
        e = []
        for i in range(len(divs)-1):
            e.append(252 if 4*(divs[i+1]-divs[i]) > 252 else 4*(divs[i+1]-divs[i]))

        pokemon['evs'] = dex.Stats(e[0], e[1], e[2], e[3], e[4], e[5])
        pokemon['ivs'] = dex.Stats(31, 31, 31, 31, 31, 31)

        team.append(pokemon)

        for i in range(len(pokemon['moves'])):
            move = re.sub(r'\W+', '', pokemon['moves'][i].lower())
            pokemon['moves'][i] = move

    return team

def generate_team(num_pokemon=6, domain='all'):
    team = []
    species = []
    items = []
    pokedex = list(domain_all)
    items = list(dex.item_dex.keys())
    natures = list(dex.nature_dex.keys())

    while len(team) < 6:
        pokemon = {}
        r = random.randint(0,len(pokedex)-1)
        pokemon['species'] = pokedex[r]
        del pokedex[r]

        pokemon['moves'] = []
        moves = list(dex.simple_learnsets[pokemon['species']])
        while len(pokemon['moves']) < 4 and len(moves) > 0:
            r = random.randint(0,len(moves)-1)
            pokemon['moves'].append(moves[r])
            del moves[r]

        
        r = random.randint(0,len(items)-1)
        pokemon['item'] = items[r]

        r = random.randint(0,len(natures)-1)
        pokemon['nature'] = natures[r]

        abilities = [re.sub(r'\W+', '', ability.lower()) for ability in list(filter(None.__ne__, list(dex.pokedex[pokemon['species']].abilities)))]
        #print(str(abilities))
        r = random.randint(0,len(abilities)-1)
        pokemon['ability'] = abilities[r]

        divs = [random.randint(0,127) for i in range(5)]
        divs.append(0)
        divs.append(127)
        divs.sort()
        evs = [4*(divs[i+1]-divs[i]) if 4*(divs[i+1]-divs[i])< 252 else 252 for i in range(len(divs)-1)]
        pokemon['evs'] = evs
        pokemon['ivs'] = [31, 31, 31, 31, 31, 31]

        team.append(pokemon)
        
    return team

def choice(L, n, p):
    pass

#print(generateTeam())

