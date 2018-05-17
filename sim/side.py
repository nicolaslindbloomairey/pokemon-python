from sim.pokemon import Pokemon
from tools.pick_six import generate_team
from tools.ai import Ai

class Side(object):
    def __init__(self, battle, id, ai=True):
        if ai == True:
            self.ai = Ai(id)
        self.id = id

        if id == 0:
            self.name = 'nic'
        if id == 1:
            self.name = 'sam'

        self.battle = battle

        self.pokemon = []

        self.team = []

        #for i in range(len(self.team)):
        #    self.pokemon.append(Pokemon(self.team[i], id, self, battle))
        #    self.pokemon[i].position = i
        #print(self.pokemon)

        self.pokemon_left = len(self.pokemon)

        self.active_pokemon = None
        self.volatile_statuses = set()

        '''
            current request is one of
            move - move request
            switch - fainted pokemon or for u-turn and what not
            teampreview - beginning of battle pick which pokemon
            '' - no request
        '''
        self.request = ''

    def populate_team(self, team):
        if team == None:
            self.team = generate_team()
        else:
            self.team = team

        for i in range(len(self.team)):
            self.pokemon.append(Pokemon(self.team[i], self.id, self, self.battle))
            self.pokemon[i].position = i

        self.pokemon_left = len(self.pokemon)
        self.active_pokemon = self.pokemon[0]
        self.pokemon[0].active = True

    #handle a switch
    def switch(self):
        #default just pick the next pokemon that isnt fainted
        if self.choice == None:
            for pokemon in self.pokemon:
                if pokemon.fainted == False:
                    self.active_pokemon = pokemon
                    pokemon.active = True
        #follow the choice of the player
        else:
            if self.pokemon[self.choice.selection].fainted == False:
                self.active_pokemon = self.pokemon[self.choice.selection]
                self.pokemon[self.choice.selection].active = True

            

