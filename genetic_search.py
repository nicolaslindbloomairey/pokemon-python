from sim.pokemon import encode_team
from sim.pokemon import decode_team
from tools.pick_six import generate_team
from tools.validator import validate_team
from sim.battle import Battle

import random

import json
with open('data/sample_teams.json') as f:
    sample_teams = json.load(f)
# start population

# evaluate fitness

# selection
# crossover
# mutation
# accepting

# replace

# test for end condition
# loop back to evaluating fitness
def main():
    print("generation 1")
    generation = 1

    size = 100
    population = initial_population(size)

    for individual in population:
        individual.fitness_test()

    while generation < 20:
        generation += 1
        population = sorted(population, key=lambda individual: individual.fitness, reverse=True)
        print(list(decode_team(population[0].genome)))
        print("fittest: " + str([x['species'] for x in list(decode_team(population[0].genome))]))
        del population[-30:]
        while len(population) < size:
            population.append(Chromosome(crossover(random.choice(population).genome,random.choice(population).genome)))
        r = random.randint(0, len(population)-1)
        population[r] = Chromosome(mutation(population[r].genome))

        print("generation " + str(generation))
        for individual in population:
            individual.fitness_test()


class Chromosome(object):
    def __init__(self, genome):
        self.genome = genome
        self.fitness = 0
    
    def fitness_test(self):
        team = decode_team(self.genome)

        num_battles = 75
        won = 0

        for i in range(num_battles):
            b = Battle(debug=False)

            b.join(0, team = team)
            b.join(1, team = sample_teams['johtoxalola'])

            b.run()
            if b.winner == 0:
                won += 1

        self.fitness = round(won / num_battles, 4)
        print(str(self.fitness))

def initial_population(size):
    population = []
    for i in range(size):
        population.append(Chromosome(encode_team(generate_team())))
    return population


def crossover(a, b):
    '''
    crossover indiviuals a and b

    crossover points are 20, 40, 60, 80, 100
    which are the seperation between pokemon themselves

    could add more crossover points within a specific pokemon

    '''
    a_pokes = [a[:20], a[20:40], a[40:60], a[60:80], a[80:100], a[100:120]]
    b_pokes = [b[:20], b[20:40], b[40:60], b[60:80], b[80:100], b[100:120]]

    a = b_pokes[0] + a_pokes[1] + b_pokes[2] + a_pokes[3] + b_pokes[4] + a_pokes[5]
    b = a_pokes[0] + b_pokes[1] + a_pokes[2] + b_pokes[3] + a_pokes[4] + b_pokes[5]

    return a if random.random() > 0.5 else b

def mutation(a):

    p1 = random.randint(0, 5)
    p2 = random.randint(0, 5)

    e1 = random.randint(8, 13)
    e2 = random.randint(8, 13)

    a_temp = a[(p1*20)+e1]
    b_temp = a[(p2*20)+e2]
    a[(p1*20)+e1] = b_temp
    a[(p2*20)+e2] = a_temp

    a[6] = (a[6]+1) % 25
    #a[7] += 1

    return a

main()
