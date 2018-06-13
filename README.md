# pokemon-python
a pokemon battle simulator written in python

This code is a battle engine for pokemon. It simply runs the logic tied to a pokemon battle. The main feature of this battle engine is that it can complete a single battle in ~18 ms on my chromebook which is 40x faster than the battle engine in pokemon showdown. This is necessary if you want to run lots of battles very quickly for comparing pokemon AI.

The implementation of many moves, abilities, and items need to be finished.

## Usage

There are three main files that handle the simulation. Battle, Side, and Pokemon.

### Battle
Battle(doubles=False, debug=True, rng=True)\
the constructor creates a battle object, each object is a single battle simulation

### battle.join
battle.join(side_id=None, team=None)\
this method adds a player to the battle with the given team. This method expects the team in json format, see [team formats](https://github.com/nicolaslindbloomairey/pokemon-python/wiki/Team-structure-formats#json)\
the side id is 0 or 1 or will just default to the next availiable id. if battle.join is called a third time, it will do nothing.

### battle.choose
battle.choose(side_id, choice)\
the choice must be a data.dex.Decision namedtuple like so, data.dex.Decision('move', 0) or data.dex.Decision('switch', 0)\
I should really clean the arguments to this method\
check battle.sides[side_id].request to see what type of decision is being requested by the game

### battle.do_turn
battle.do_turn()\
Once both side have made a battle.choose() you can call battle.do_turn()\
It will update the game state according to the decisions made

### battle.run
battle.run()\
finished the rest of the battle with default decisions from both sides


The goal for this simulator is to have two AIs play against each other, so it will be built with that in mind.
