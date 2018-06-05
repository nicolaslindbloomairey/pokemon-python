from data import dex
import re

class InValidSetError(Exception):
    def __init__(self, message):
        self.message = message

def validate_team(team):
    '''
    team is an array of six pokemon sets
    '''
    if len(team) > 6:
        raise InValidSetError("more than 6 pokemon")
    pokemon_names = set()

    for pokemon in team:
        # check if the pokemon is an actual pokemon
        species = re.sub(r'\W+', '', pokemon['species'].lower())
        pokemon_names.add(species)
        if species not in dex.pokedex:
            raise InValidSetError(species + " is not a real pokemon species")
        if len(pokemon['moves']) > 4:
            raise InValidSetError("more than 4 moves")
        for move in pokemon['moves']:
            if move not in dex.simple_learnsets[species]:
                raise InValidSetError(species + " can't learn the move " + move)
        if pokemon['ability'] not in [re.sub(r'\W+', '', ability.lower()) for ability in list(filter(None.__ne__, list(dex.pokedex[species].abilities)))]:
            raise InValidSetError(species + " cant have the ability, " + pokemon['ability'])
        for i in range(6):
            if pokemon['evs'][i] > 255 or pokemon['evs'][i] < 0:
                raise InVaidSetError("ev value is out of range: " + str(pokemon['evs'][i]))
            if pokemon['ivs'][i] > 31 or pokemon['ivs'][i] < 0:
                raise InVaidSetError("iv value is out of range: " + str(pokemon['ivs'][i]))
        if sum(pokemon['evs']) > 510:
            raise InValidSetError("sum of evs is over 510")

    if len(team) != len(pokemon_names):
        raise InValidSetError("cannot have multiple of the same pokemon")

    return True

