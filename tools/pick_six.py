import random
import json
import numpy
import re
from collections import namedtuple
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')

with open('data/vgcrefomated.json') as f:
    vgc = json.load(f)


def generate_team():

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

        pokemon['evs'] = Stats(e[0], e[1], e[2], e[3], e[4], e[5])
        pokemon['ivs'] = Stats(31, 31, 31, 31, 31, 31)

        team.append(pokemon)

        for i in range(len(pokemon['moves'])):
            move = re.sub(r'\W+', '', pokemon['moves'][i].lower())
            pokemon['moves'][i] = move

    return team

#print(generateTeam())

