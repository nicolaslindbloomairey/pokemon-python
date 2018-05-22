from sim.pokemon import Pokemon
from tools.pick_six import generate_team
from tools.ai import Ai
from data import dex
import random

class Side(object):
    def __init__(self, battle, id, ai=True):
        '''
        battle - reference to the battle object to which this side belongs
        id - 0 or 1, index in the battle.sides list
        '''
        if ai:
            self.ai = Ai(id)
        self.id = id

        self.name = 'sam' if id else 'nic'

        self.battle = battle

        self.pokemon = []

        self.team = []

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
        self.request = 'move'

        self.used_zmove = False

    def ai_decide(self):
        self.choice = self.ai.decide(self.battle)

        # if the ai failed to make a decision
        if self.choice is None:
            self.default_decide()

        # update some flags
        if self.choice.type == 'switch':
            self.active_pokemon.is_switching = True

    def default_decide(self):

        if self.request == 'switch':
            for pokemon in self.pokemon:
                if pokemon.fainted == False:
                    self.choice = dex.Decision('switch', pokemon.position)
                    return
        elif self.request == 'pass':
            self.choice = dex.Decision('pass', 0)
            return

        rand_int = random.randint(0, 3)
        self.choice = dex.Decision('move', rand_int)


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

    # switch the active pokemon to the pokemon in index: position
    def switch(self, position):
        if self.active_pokemon.trapped:
            return

        # if the selected pokemon is fainted do a default switch
        if self.pokemon[position].fainted:
            self.default_switch()
            return

        pokemon_out = self.active_pokemon
        pokemon_in = self.pokemon[position]

        pokemon_out.is_switching = False
        self.active_pokemon = pokemon_in
        pokemon_in.active = True

        if self.battle.debug:
            print(pokemon_out.fullname
                  + ' switches out for '
                  + pokemon_in.fullname)

    # switch to the first non-fainted pokemon on your team
    def default_switch(self):
        if not pokemon_left:
            raise ValueError('There are no pokemon left but we are trying to switch!')

        for pokemon in self.pokemon:
            if pokemon.fainted == False:
                self.switch(pokemon.position)
