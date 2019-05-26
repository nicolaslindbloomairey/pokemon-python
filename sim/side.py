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

        # all the pokemon on the side
        self.pokemon = []
        # the non active pokemon
        self.bench = []

        self.team = []

        self.pokemon_left = len(self.pokemon)

        # in singles this should always be of length 1
        self.active_pokemon = []
        self.volatile_statuses = set()
        self.side_conditions = set()

        '''
            current request is one of
            move - move request
            switch - fainted pokemon or for u-turn and what not
            teampreview - beginning of battle pick which pokemon
            '' - no request
        '''
        self.request = ['move', 'move'] if self.battle.doubles else ['move']
        self.choice = [None, None] if self.battle.doubles else [None]

        self.used_zmove = False

    def __str__(self):
        out = []
        out.append('id: ' + str(self.id) + '\n') 
        out.append('name: ' + str(self.name) + '\n') 
        out.append('bench: ' + str(self.bench) + '\n') 
        #out.append('team: ' + str(self.team) + '\n') 
        out.append('pokemon_left: ' + str(self.pokemon_left) + '\n') 
        out.append('active pokemon: ' + str(self.active_pokemon) + '\n') 
        out.append('volatile_statuses: ' + str(self.volatile_statuses) + '\n') 
        out.append('side_conditions: ' + str(self.side_conditions) + '\n') 
        out.append('request: ' + str(self.request) + '\n') 
        out.append('choice: ' + str(self.choice) + '\n') 
        out.append('used_zmove: ' + str(self.used_zmove) + '\n') 
        out.append('\nPOKEMON \n') 
        for i in self.pokemon:
            out.append(str(i) + '\n') 
        return ''.join(out)

    def ai_decide(self):
        self.choice = self.ai.decide(self.battle)

        # if the ai failed to make a decision
        if self.choice is None:
            self.default_decide()

        # update some flags
        if self.choice.type == 'switch':
            self.active_pokemon.is_switching = True

    def default_decide(self):
        #n = 2 if self.battle.doubles else 1
        n = len(self.active_pokemon)
        for i in range(n):

            if self.request[i] == 'switch':
                for pokemon in self.pokemon:
                    if pokemon.fainted == False:
                        self.choice[i] = dex.Decision('switch', pokemon.position)

            elif self.request[i] == 'pass':
                self.choice[i] = dex.Decision('pass', 0)

            elif self.request[i] == 'move':
                if len(self.active_pokemon[i].moves) > 0:
                    rand_int = random.randint(0, len(self.active_pokemon[i].moves)-1)
                    self.choice[i] = dex.Decision('move', rand_int)
                else:
                    self.choice[i] = dex.Decision('move', 'struggle')

    def populate_team(self, team):
        if team == None:
            self.team = generate_team()
        else:
            self.team = team

        for i in range(len(self.team)):
            self.pokemon.append(Pokemon(self.team[i], self.id, self, self.battle))
            self.pokemon[i].position = i

        for pokemon in self.pokemon:
            self.bench.append(pokemon)

        self.pokemon_left = len(self.pokemon)

        self.throw_out(self.pokemon[0])
        if self.battle.doubles:
            self.throw_out(self.pokemon[1])


    # use this method to handle on entry things like abilities
    def throw_out(self, pokemon):
        if not pokemon in self.bench:
            return False
        if pokemon.fainted:
            return False
        self.bench.remove(pokemon)
        self.active_pokemon.append(pokemon)
        pokemon.active = True

    # switch the active pokemon to the pokemon in index: position
    def switch(self, user, position):
        if 'cantescape' in user.volatile_statuses and not user.fainted:
            return False
        if 'partiallytrapped' in user.volatile_statuses and not user.fainted and 'Ghost' not in user.types:
            return False

        if self.battle.doubles and self.pokemon_left == 1:
            self.active_pokemon.remove(user)
            self.battle.active_pokemon.remove(user)
            return

        # if the selected pokemon is fainted or is already on the field do a default switch
        if self.pokemon[position].fainted or self.pokemon[position].active:
            return self.default_switch(user)

        pokemon_out = user
        pokemon_in = self.pokemon[position]

        #switch
        # update the sides active pokemon
        pos = self.active_pokemon.index(pokemon_out)
        self.active_pokemon[pos] = pokemon_in

        # update the battles active pokemon
        pos = self.battle.active_pokemon.index(pokemon_out)
        self.battle.active_pokemon[pos] = pokemon_in

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
    def default_switch(self, user):
        if not self.pokemon_left:
            raise ValueError('There are no pokemon left but we are trying to switch!')

        for pokemon in self.bench:
            if not pokemon.fainted and not pokemon.active:
                self.switch(user, pokemon.position)
                return True

