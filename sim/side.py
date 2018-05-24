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
        self.side_conditions = set()

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

        if len(self.active_pokemon.moves) > 0:
            rand_int = random.randint(0, len(self.active_pokemon.moves)-1)
            self.choice = dex.Decision('move', rand_int)
        else:
            self.choice = dex.Decision('move', 'struggle')


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

    # use this method to handle on entry things like abilities
    def throw_out(self, pokemon):
        pass

    # switch the active pokemon to the pokemon in index: position
    def switch(self, position):
        if 'cantescape' in self.active_pokemon.volatile_statuses:
            return False
        if 'partiallytrapped' in self.active_pokemon.volatile_statuses and 'Ghost' not in self.active_pokemon.types:
            return False

        # if the selected pokemon is fainted do a default switch
        if self.pokemon[position].fainted:
            return self.default_switch()

        pokemon_out = self.active_pokemon
        pokemon_in = self.pokemon[position]

        #switch
        self.active_pokemon = pokemon_in

        pokemon_in.active = True
        pokemon_out.is_switching = False
        pokemon_out.aqua_ring = False
        pokemon_out.volatile_statuses = set()

        self.boosts = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
        }

        self.battle.log(pokemon_out.fullname
              + ' switches out for '
              + pokemon_in.fullname)
        return True

    # switch to the first non-fainted pokemon on your team
    def default_switch(self):
        if not pokemon_left:
            raise ValueError('There are no pokemon left but we are trying to switch!')

        for pokemon in self.pokemon:
            if pokemon.fainted == False:
                self.switch(pokemon.position)
        return True
