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
            self.pokemon.append(Pokemon(self.team[i], num, self, battle))
            self.pokemon[i].position = i
        #print(self.pokemon)

        self.pokemonLeft = len(self.pokemon)

        self.activePokemon = self.pokemon[0]
        self.pokemon[0].active = True

        '''
            current request is one of
            move - move request
            switch - fainted pokemon or for u-turn and what not
            teampreview - beginning of battle pick which pokemon
            '' - no request
        '''
        self.request = ''

    #handle a switch
    def switch(self):
        #default just pick the next pokemon that isnt fainted
        if self.choice == None:
            for pokemon in self.pokemon:
                if pokemon.fainted == False:
                    self.activePokemon = pokemon
                    pokemon.active = True
        #follow the choice of the player
        else:
            if self.pokemon[self.choice.selection].fainted == False:
                self.activePokemon = self.pokemon[self.choice.selection]
                self.pokemon[self.choice.selection].active = True

            

