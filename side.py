from pokemon import Pokemon
from picksix import generateTeam
from ai import Ai

class Side:
    def __init__(self, battle, num):
        self.ai = Ai(num)

        self.battle = battle

        self.pokemon = []
        self.team = generateTeam()

        for i in range(len(self.team)):
            self.pokemon.append(Pokemon(self.team[i], num))
            self.pokemon[i].position = i
        #print(self.pokemon)

        self.pokemonLeft = len(self.pokemon)

        self.activePokemon = self.pokemon[0]

        '''
            current request is one of
            move - move request
            switch - fainted pokemon or for u-turn and what not
            teampreview - beginning of battle pick which pokemon
            '' - no request
        '''
        self.request = ''

