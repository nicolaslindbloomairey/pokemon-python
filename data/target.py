import json
with open('moves.json') as f:
    moves = json.load(f)
targets = set()

for move in moves:
    targets.add(moves[move]['target_type'])

print(str(targets))
