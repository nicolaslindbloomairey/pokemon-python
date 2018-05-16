from battle import Battle
from collections import namedtuple
Decision = namedtuple('Decision', ['type', 'selection'])

battle = Battle()

battle.join(0, [{'species': 'mew', 'ability': 'Water Veil', 'level': 100, 'moves': ['growl', 'tackle']}])
battle.join(1, [{'species': 'squirtle', 'level': 5, 'moves': ['nuzzle', 'watergun', 'scald']}])

battle.choose(0, Decision('move', 0))
battle.choose(1, Decision('move', 2))
battle.doTurn()

print(battle)
