'''
Nicolas Lindbloom-Airey

turn.py

This file is entirely devoted to the do_turn(Battle) method.
One call of do_turn does all the logic for a single turn.
Functions defined in this file are:
    * functions are are only called in the do_turn method.

Functions called by run_move are called only once per run_move call.
turn_start and turn_end are called once per turn.
create_move and populate_action_queue are called once per active pokemon
    in the battle.
run_action is called once on every action created.

ORDER OF FUNCTION CALL:
    turn_start
    create_move
    populate_action_queue
    run_action 
        run_move
            update_move_before_running
            accuracy_check
            calc_damage
                -> damage called in pokemon.py
            unique_moves_after_damage
            boosts_statuses
    turn_end
'''

import heapq
from sim.player import *

def turn_start(B:Battle) -> None:
    '''
    ONLY CALLED IN do_turn()

    Returns early if this is a pseudo turn
    Updates volatile statuses that only last one turn
    Resets the pokemon.pokemon_hit_this_turn for every active pokemon
    '''
    B.turn += 1
    B.turn = math.floor(B.turn)

    if B.pseudo_turn:
        B.turn -= 0.5
        return
    for pokemon in get_active_pokemon(B):
        pokemon.active_turns += 1
        pokemon.pokemon_hit_this_turn = 0
        # remove volatile statuses that only last one turn
        one_turn_statuses = {None, 'flinch', 'endure', 'protect',
                            'banefulbunker', 'spikyshield'}
        pokemon.volatile_statuses -= one_turn_statuses
    return

def turn_end(B:Battle) -> None:
    '''
    ONLY CALLED IN do_turn()

    Updates flags after all actions are done.

    PRE: B.pseudo_turn = False
    '''
    if B.pseudo_turn:
        sys.exit('ERROR: turn_end() called on pseudo turn')

    # tick weather counter down
    if B.weather in ['sunlight', 'rain', 'sandstorm', 'hail']:
        B.weather_n -= 1
        if B.weather_n == 0:
            B.weather = 'clear'

    # weather damage
    for pokemon in get_active_pokemon(B):
        if pokemon.item == 'safteygoggles':
            continue
        if B.weather == 'sandstorm': 
            if {'Steel','Rock','Ground'}.isdisjoint(pokemon.types):
                damage(pokemon, 1/16, flag='percentmaxhp')
        if B.weather == 'hail': 
            if 'Ice' not in pokemon.types:
                damage(pokemon, 1/16, flag='percentmaxhp')


    # volatile statuses
    for pokemon in get_active_pokemon(B):
        # bound
        if 'partiallytrapped' in pokemon.volatile_statuses:
            damage(pokemon, pokemon.bound_damage, flag='percentmaxhp')
            pokemon.bound_n -= 1
            if pokemon.bound_n == 0:
                pokemon.volatile_statuses -= {'partiallytrapped'}
        # aqua ring
        if pokemon.aqua_ring:
            dmg = -1/16
            if pokemon.item == 'bigroot':
                dmg *= 1.3
            damage(pokemon, dmg, 'percentmaxhp')
        # leech seed
        #if 'leechseed' in pokemon.volatile_statuses:
        #    foe = B.sides[0 if pokemon.side_id else 1].active_pokemon[0]
        #    dmg = 1/8
        #    if foe.item == 'bigroot':
        #        dmg *= 1.3
        #    damage(foe, -(damage(pokemon, dmg, 'percentmaxhp')))
        # nightmare
        if 'nightmare' in pokemon.volatile_statuses:
            if pokemon.status == 'slp':
                damage(pokemon, 1/4, 'percentmaxhp')
        # perish song
        if 'perishsong' in pokemon.volatile_statuses:
            pokemon.perishsong_n -= 1
            if pokemon.perishsong_n == 0:
                faint(pokemon)
        # encore 
        if 'encore' in pokemon.volatile_statuses:
            pokemon.encore_n -= 1
            if pokemon.encore_n == 0:
                pokemon.volatile_statuses -= {'encore'}
        # taunt
        if 'taunt' in pokemon.volatile_statuses:
            pokemon.taunt_n -= 1
            if pokemon.taunt_n == 0:
                pokemon.volatile_statuses.remove('taunt')
        # curse
        if 'curse' in pokemon.volatile_statuses:
            if 'Ghost' in pokemon.types:
                damage(pokemon, 1/4, flag='percentmaxhp')

    # do major status checks
    for pokemon in get_active_pokemon(B):
        if pokemon.status == 'brn':
            damage(pokemon, 1/16, flag='percentmax')
        elif pokemon.status == 'psn':
            damage(pokemon, 1/8, flag='percentmax')
        elif pokemon.status == 'tox':
            dmg = 1/16*pokemon.toxic_n
            damage(pokemon, dmg, flag='percentmax')
            pokemon.toxic_n += 1
        elif pokemon.status == 'frz':
            #twenty percent chance to be thawed
            if random.random() < 0.20:
                cure_status(pokemon)
            if B.weather == 'sunlight':
                cure_status(pokemon)
        elif pokemon.status == 'slp':
            pokemon.sleep_n -= 1
            if pokemon.sleep_n == 0:
                cure_status(pokemon)
    return

def run_action(B, a : Action) -> None:
    '''
    ONLY CALLED IN do_turn()
    Takes Action object and if it is a switch, calls player.switch().
    If it is a mega evolution, call pokemon.mega_evolve().
    Lastly, if the action is a move, find the target pokemon's pointer
    and call battle.run_move(Pokemon, Move, Pokemon)
    '''
    #user, move, target, zmove, base_move = action
    # action is set up three different ways

    # one way for switches
    if a.action_type == 'switch':
        if a.user.player_uid == 1:
            switch(B.p1, a.user, a.pos)
        if a.user.player_uid == 2:
            switch(B.p2, a.user, a.pos)
        return

    # another for mega evolutions
    if a.action_type == 'mega':
        a.user.mega_evolve()
        return

    # if it is a single battle and target starts with 'foe'
    if not B.doubles and a.target[0:3] == 'foe':
        p = a.user.player_uid
        if p == 1:
            run_move(B, a.user, a.move, B.p2.active_pokemon[0])
        if p == 2:
            run_move(B, a.user, a.move, B.p1.active_pokemon[0])
        return

    if a.target == 'all': 
        move = move._replace(base_power = move.base_power * 0.75)
        for pokemon in get_active_pokemon(B):
            B.run_move(user, move, pokemon)
        return

    return

def run_move(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> None:
    '''
    ONLY CALLED IN run_action()
    Does the move logic.
    '''
    # Fainted pokemon can't use their move.
    if user.fainted:
        #B.log(user.name + " fainted before they could move")
        return

    # subtract pp
    # struggle and zmoves do not have pp
    if move.id != 'struggle' and move.z_move.crystal is None:
        if move.id in user.pp:
            user.pp[move.id] -= 1
            # remove the move from the pokemons move list if it has no pp left
            #if user.pp[move.id] == 0:
            #    if move.id in user.moves:
            #        user.moves.remove(move.id)
    # update last used move
    user.last_used_move = move.id

    move = update_move_before_running(B, user, move, target)

    # ACCURACY CHECK
    if not accuracy_check(B, user, move, target):
        if B.debug:
            print(user.name + ' used ' + move.id + ' and missed')
        # move missed! do nothing
        return

    # zmove pp
    if move.z_move.crystal is not None:
        pass
        #user.side.used_zmove = True

    # Handle multi hit moves.
    # move.multi_hit is a probability distribution of number of hits in
    #  increasing order.
    # move.multi_hit[-1] is last element.
    number_hits = 1
    if move.multi_hit is not None:
        number_hits = random.choice(move.multi_hit)
        if user.ability == 'skilllink':
            number_hits = move.multi_hit[-1]

    #---------------
    # do damage
    #---------------

    for i in range(number_hits):
        # Triplekick checks accuracy for every hit
        if i != 1 and move.id == 'triplekick':
            if not B.accuracy_check(user, move, target):
                return

        # damage calculation
        dmg = calc_damage(B, user, move, target)
        # do the damage
        # how much damage was actually done
        # is limited by how much hp the target had left
        dmg = damage(target, dmg)

    if dmg > 0:
        target.last_damaging_move = move.id

    # do unique move things
    unique_moves_after_damage(B, user, move, target, dmg)
    # handle boosts and statuses
    boosts_statuses(B, user, move, target)
    if B.debug:
        print(user.name + ' used ' + move.id + '')
    return

def calc_damage(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> int:
    '''
    ONLY CALLED IN run_move()
    Calculates the amount of damage done to the target by the user
    using the move.
    ''' 
    # status moves do zero dmg, return early
    if move.category == 'Status':
        return 0
    dmg = 0

    # Was it a critical hit? -> Make local var.
    crit = False
    move_crit = move.crit_ratio if move.crit_ratio is not None else 0
    crit_chance = user.crit_chance + move_crit
    random_crit = random.random() < (dex.crit[crit_chance] if crit_chance <= 3 else 1) and B.rng
    if crit_chance >= 3 or random_crit:
        crit = True

    # Set up power, attack, defense variables
    power = move.base_power
    if move.category == 'Special':
        attack = get_specialattack(user, crit, B.weather)
        defense = get_specialdefense(target, crit, B.weather)
    elif move.category == 'Physical':
        attack = get_attack(user, crit, B.weather)
        defense = get_defense(target, crit, B.terrain)

    # Main damage formula.
    dmg = (math.floor(math.floor(math.floor(((2 * user.level) / 5) + 2) * attack * power / defense) / 50) + 2) 

    # multiply the damage by each modifier
    modifier = 1

    # CRITICAL DAMAGE
    if crit:
        modifier *= 1.5

    # RANDOMNESS
    if B.rng:
        modifier *= random.uniform(0.85, 1.0)

    # STAB (same type attack bonus)
    if move.type in user.types:
        modifier *= 1.5

    # TYPE EFFECTIVENESS
    type_modifier = 1
    for each in target.types:
        type_effect = dex.typechart_dex[each].damage_taken[move.type]
        type_modifier *= type_effect
        modifier *= type_effect

    # moves that hit multiple pokemon do less damage
    if B.doubles and move.target_type in ['foeSide', 'allyTeam', 'allAdjacent', 'allAdjacentFoes', 'allySide']:
        modifier *= 0.75

    # WEATHER
    if B.weather in ['rain', 'heavy_rain']:
        if move.type == 'Water':
            modifier *= 1.5
        elif move.type == 'Fire':
            modifier *= 0.5
    elif B.weather in ['sunlight', 'heavy_sunlight']:
        if move.type == 'Water':
            modifier *= 0.5
        elif move.type == 'Fire':
            modifier *= 1.5



    # burn
    if user.status == 'brn' and \
        move.category == 'Physical' and \
        user.ability != 'guts':
        modifier *= 0.5

    # zmove goes through protect at 1/4 damage
    if move.z_move.crystal is not None and 'protect' in target.volatile_statuses:
        modifier *= 0.25

    # aurora veil, lightscreen, reflect
    #if 'auroraveil' in target.side.side_conditions and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
    #    modifier *= 0.5
    #elif 'lightscreen' in target.side.side_conditions and move.category == 'Special' and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
    #    modifier *= 0.5
    #elif 'reflect' in target.side.side_conditions and move.category == 'Physical'and not crit and user.ability != 'infiltrator':
        #double battle this should be 0.66
    #    modifier *= 0.5

    if 'minimize' in target.volatile_statuses:
        if move.id in ['dragonrush', 'bodyslam', 'heatcrash', 'heavyslam', 'phantomforce', 'shadowforce', 'stomp']:
            modifier *= 2

    #magnitude, earthquake, surf, whirlpool do double dmg to dig and dive states
    
    # ABILITIES
    if target.ability == 'fluffy':
        if move.flags.contact and move.type != 'Fire':
            modifier *= 0.5
        elif not move.flags.contact and move.type == 'Fire':
            modifier *= 2
    elif target.ability == 'filter' or target.ability == 'prismarmor':
        if type_modifier > 1:
            modifier *= 0.75
    # friend guard
    elif target.ability in ['multiscale', 'shadowshield', 'solidrock']:
        if target.hp == target.maxhp:
            modifier *= 0.5

    if user.ability == 'sniper' and crit:
        modifier *= 1.5
    
    elif user.ability == 'tintedlens':
        if type_modifier < 1:
            modifier *= 2

    # ITEMS    
    if target.item == 'chilanberry' and move.type == 'Normal':
        modifier *= 0.5
    if user.item == 'expertbelt' and type_modifier > 1:
        modifier *= 1.2
    if user.item == 'lifeorb':
        modifier *= 1.3
    if user.item == 'metronome':
        modifier *= (1+(user.consecutive_move_uses*0.2))
    # type-resist berries
    if target.item in list(dex.type_resist_berries.keys()):
        if dex.type_resist_berries[target.item] == move.type:
            if type_modifier > 1:
                modifier *= 0.5

    #floor damage before and after applying modifier
    dmg = math.floor(dmg)
    dmg *= modifier
    dmg = math.floor(dmg)
    return dmg

def accuracy_check(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> bool:
    '''
    ONLY CALLED IN run_move
    Check if the move hits(true) or misses(false).
    Check specific move requirements to not fail
    at the end.

    A False return here ends the run_move method.
    '''

    # full paralyze
    if user.status == 'par' and random.random() < 0.25:
        return False
    # asleep pokemon miss unless they use snore or sleeptalk
    elif user.status == 'slp' and not move.sleep_usable:
        return False

    # Is the target protected?
    if 'protect' in target.volatile_statuses and move.flags.protect:
        return False
    if 'banefulbunker' in target.volatile_statuses and move.flags.protect:
        return False
    if 'spikyshield' in target.volatile_statuses and move.flags.protect:
        return False
    if 'kingsshield' in target.volatile_statuses and move.flags.protect and move.category != 'Status':
        return False

    # protect moves accuracy
    if move.id in ['protect', 'detect', 'endure', 'wide guard', 'quick guard', 'spikyshield', 'kingsshield', 'banefulbunker']:
        rand_float = random.random()
        n = user.protect_n
        user.protect_n += 3
        if not B.rng and n > 0:
            return False
        if n == 0 or rand_float < (1.0 / n):
            return True
        return False
    else:
        # if the move is not a protect move, reset the counter
        user.protect_n = 0

    # flinched
    if 'flinch' in user.volatile_statuses:
        return False

    # fake out fails after 1 turn active
    if move.id == 'fakeout' and user.active_turns > 1:
        return False

    # if user is taunted, status moves fail
    if move.category == 'Status' and 'taunt' in user.volatile_statuses:
        return False

    # these moves dont check accuracy in certain weather
    if move.id == 'thunder' and B.weather == 'rain':
        return True
    if move.id == 'hurricane' and B.weather == 'rain':
        return True
    if move.id == 'blizzard' and B.weather == 'hail':
        return True

    # some moves don't check accuracy
    if move.accuracy is True:
        return True

    # returns a boolean whether the move hit the target
    # if temp < check then the move hits
    temp = random.randint(0, 99)
    accuracy = get_accuracy(user)
    evasion = get_evasion(target)
    check = 100
    if B.rng:
        check = (move.accuracy * accuracy * evasion)
    return temp < check 

def boosts_statuses(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> None:
    '''
    ONLY CALLED in run_move()
    Handles boosts and statuses.
    '''
    # stat changing moves 
    user_volatile_status = ''
    target_volatile_status = ''
    # primary effects
    if move.primary['boosts'] is not None:
        boost(target, move.primary['boosts'])
    if move.primary['volatile_status'] is not None:
        target_volatile_status = move.primary['volatile_status']
        target.volatile_statuses.add(target_volatile_status)

    if move.primary['self'] is not None:
        if 'boosts' in move.primary['self']:
            boost(user, move.primary['self']['boosts'])
        if 'volatile_status' in move.primary['self']:
            user_volatile_status = move.primary['self']['volatile_status']
            user.volatile_statuses.add(user_volatile_status)

    if move.primary['status'] is not None:
        add_status(target, move.primary['status'])

    # secondary effects
    for effect in move.secondary:
        if not target.fainted:
            temp = random.randint(0, 99)
            check = effect['chance']
            if check != 100 and not B.rng:
                check = 0
            if temp < check:
                if 'boosts' in effect:
                    boost(target, effect['boosts'])
                if 'status' in effect:
                    add_status(target, effect['status'], user)
                if 'volatile_status' in effect:
                    target_volatile_status = effect['volatile_status']
                    target.volatile_statuses.add(target_volatile_status)

    if target_volatile_status == 'partiallytrapped':
        target.bound_n = 4 if random.random() < 0.5 else 5
        target.bound_damage = 1/16
        if user.item == 'gripclaw':
            target.bound_n = 7
        if user.item == 'bindingband':
            target.bound_damage = 1/8

    if target_volatile_status == 'taunt':
        target.taunt_n = 3

    if target_volatile_status == 'encore':
        target.encore_n = 3
    return

def update_move_before_running(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon) -> dex.Move:
    '''
    ONLY CALLED IN run_move()
    Returns the new move reference

    Some moves need to have their info updated based on the current state
    before running. the namedtuple._replace returns a new namedtuple
    instance with updated values so we dont have to worry about ruining the 
    game data
    '''
    # update the moves power

    # acrobatics
    if move.id == 'acrobatics' and user.item == '':
        power = move.base_power * 2
        move = move._replace(base_power = power)

    elif move.id == 'beatup':
        power = 0
        #for pokemon in user.side.pokemon:
        #    power += (dex.pokedex[pokemon.id].baseStats.attack / 10) + 5
        move = move._replace(base_power = power)
    
    elif move.id == 'crushgrip' or move.id == 'wringout':
        power = math.floor(120 * (target.hp / target.maxhp))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'electroball':
        power = 1
        speed = target.stats.speed / user.stats.speed
        if speed <= 0.25:
            power = 150
        if speed > 0.25:
            power = 120
        if speed > .3333:
            power = 80
        if speed > 0.5:
            power = 60
        if speed > 1:
            power = 40
        move = move._replace(base_power = power)

    elif move.id == 'eruption' or move.id == 'waterspout':
        power = math.floor(150 * (user.hp / user.maxhp))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'flail' or move.id == 'reversal':
        power = 1
        hp = user.hp / user.maxhp
        if hp < 0.0417:
            power = 200
        if hp >= 0.0417:
            power = 150
        if hp > 0.1042:
            power = 100
        if hp > 0.2083:
            power = 80
        if hp > 0.3542:
            power = 40
        if hp >= 0.6875:
            power = 20
        move = move._replace(base_power = power)

    elif move.id == 'fling':
        #default base power will be 30
        power = dex.fling.get(user.item, 30)
        move = move._replace(base_power = power)
        if user.item == 'kingsrock' or user.item == 'razorfang':
            move = move._replace(primary= {'boosts': None, 'status': None, 'volatile_status': 'flinch', 'B': None})
        elif user.item == 'flameorb':
            move = move._replace(primary= {'boosts': None, 'status': 'brn', 'volatile_status': None, 'B': None})
        elif user.item == 'toxicorb':
            move = move._replace(primary= {'boosts': None, 'status': 'tox', 'volatile_status': None, 'B': None})
        elif user.item == 'lightball':
            move = move._replace(primary= {'boosts': None, 'status': 'par', 'volatile_status': None, 'B': None})
        elif user.item == 'poisonbarb':
            move = move._replace(primary= {'boosts': None, 'status': 'psn', 'volatile_status': None, 'B': None})

    # assume max base_power for return and frustration
    elif move.id == 'frustration' or move.id == 'return':
        move = move._replace(base_power = 102)

    elif move.id == 'grassknot':
        power = 1
        weight = dex.pokedex[target.species].weightkg
        if weight >= 200:
            power = 120
        if weight < 200:
            power = 100
        if weight < 100:
            power = 80
        if weight < 50:
            power = 60
        if weight < 25:
            power = 40
        if weight < 10:
            power = 20
        move = move._replace(base_power = power)

    elif move.id == 'heatcrash' or move.id == 'heavyslam':
        power = 1
        weight = dex.pokedex[target.id].weightkg / dex.pokedex[user.id].weightkg
        if weight > 0.5:
            power = 40
        if weight < 0.5:
            power = 60
        if weight < 0.333:
            power = 80
        if weight < 0.25:
            power = 100
        if weight < 0.20:
            power = 120
        move = move._replace(base_power = power)

    elif move.id == 'gyroball':
        target_player = (B.p1 if target.player_uid == 1 else B.p2)
        user_player = (B.p1 if user.player_uid == 1 else B.p2)
        power = math.floor(25 * (get_speed(target, B.weather, B.terrain, B.trickroom, target_player.tailwind) / get_speed(user, B.weather, B.terrain, B.trickroom, user_player.tailwind)))
        if power < 1:
            power = 1
        move = move._replace(base_power = power)

    elif move.id == 'magnitude':
        power = random.choice(dex.magnitude_power)
        move = move._replace(base_power = power)

    elif move.id == 'naturalgift':
        item = dex.item_dex[user.item]
        if item.isBerry:
            move = move._replace(base_power = item.naturalGift['basePower'])
            move = move._replace(type = item.naturalGift['type'])
    
    elif move.id == 'powertrip' or move.id == 'storedpower':
        power = 20
        for stat in user.boosts:
            if user.boosts[stat] > 0:
                power += (user.boosts[stat] * 20)
        move = move._replace(base_power = power)

    elif move.id == 'present':
        power = random.choice([0, 0, 120, 80, 80, 80, 40, 40, 40, 40])
        move = move._replace(base_power = power)

    elif move.id == 'punishment':
        power = 60
        for stat in target.boosts:
            if target.boosts[stat] > 0:
                power += (target.boosts[stat] * 20)
        if power > 200:
            power = 200
        move = move._replace(base_power = power)

    elif move.id == 'spitup':
        power = 100 * user.stockpile
        move = move._replace(base_power = power)
        user.stockpile = 0

    # assist
    elif move.id == 'assist':
        # it hink this is broken
        #move = dex.move_dex[random.choice(target.moves)]
        pass
    
    # metronome
    elif move.id == 'metronome':
        while move.id in dex.no_metronome:
            move = dex.move_dex[random.choice(list(dex.move_dex.keys()))]

    # mimic
    elif move.id == 'mimic':
        if target.last_used_move is not None:
            if 'mimic' in user.moves:
                user.moves.remove('mimic')
            user.moves.append(target.last_used_move)
            move = dex.move_dex[target.last_used_move]

    # copycat
    elif move.id == 'copycat':
        if target.last_used_move is not None:
            move = dex.move_dex[target.last_used_move]

    elif move.id == 'naturepower':
        move = dex.move_dex['triattack']

    # mirror move
    elif move.id == 'mirror move':
        if target.last_used_move is not None:
            move = dex.move_dex[target.last_used_move]

    # check non unique stuff
    # baneful bunker
    if 'banefulbunker' in target.volatile_statuses:
        if move.flags.contact:
            user.add_status('psn')

    # spiky shield
    if 'spikeyshield' in target.volatile_statuses:
        damage(user, 0.125, flag='percentmaxhp')

    # RECOIL DAMAGE
    if move.recoil.damage != 0:
        if move.recoil.condition == 'always':
            if move.recoil.type == 'maxhp':
                damage(user, move.recoil.damage, flag='percentmaxhp')
    return move

def unique_moves_after_damage(B:Battle, user:Pokemon, move:dex.Move, target:Pokemon, dmg:int):
    '''
    ONLY CALLED IN run_move()
    '''
    #drain moves
    if user.item == 'bigroot':
        damage(user, -(math.floor(dmg * move.drain * 1.3)))
    else:
        damage(user, -(math.floor(dmg * move.drain)))

    #heal moves
    if move.heal > 0:
        damage(user, -(move.heal), flag='percentmaxhp')

    #heal moves that depend on weather
    if move.id in ['moonlight', 'morningsun', 'synthesis']:
        if B.weather == 'clear':
            damage(user, -(0.5), flag='percentmaxhp')
        elif B.weather == 'sunlight':
            damage(user, -(0.66), flag='percentmaxhp')
        else:
            damage(user, -(0.25), flag='percentmaxhp')
    if move.id == 'shoreup':
        if B.weather == 'sandstorm':
            damage(user, -(0.66), flag='percentmaxhp')
        else:
            damage(user, -(0.50), flag='percentmaxhp')

    #recoil moves
    if move.recoil.damage != 0:
        if move.recoil.condition == 'hit':
            if move.recoil.type == 'maxhp':
                damage(user, move.recoil.damage, flag='percentmaxhp')
            if move.recoil.type == 'damage':
                damage(user, dmg* move.recoil.damage)

    # terrain moves 
    if move.terrain is not None:
        B.terrain = move.terrain

    # weather moves
    if move.weather is not None and B.weather != move.weather:
        B.weather = move.weather
        B.weather_n = 5
        if user.item == 'heatrock' and B.weather == 'sunlight':
            B.weather_n = 8
        if user.item == 'damprock' and B.weather == 'rain':
            B.weather_n = 8
        if user.item == 'smoothrock' and B.weather == 'sandstorm':
            B.weather_n = 8
        if user.item == 'icyrock' and B.weather == 'hail':
            B.weather_n = 8

    # accupressure
    if move.id == 'acupressure':
        possible_stats = [stat for stat in user.boosts if user.boosts[stat] < 6]
        if len(possible_stats) > 0:
            rand_int = random.randint(0, len(possible_stats)-1)
            boost_stat = possible_stats[rand_int]
            user.boosts[boost_stat] += 2
            if user.boosts[boost_stat] > 6:
                user.boosts[boost_stat] = 6

    # aqua ring
    if move.id == 'aquaring':
        user.aqua_ring = True

    # ingrain
    if move.id == 'ingrain':
        user.aqua_ring = True
        user.trapped = True

    # aromatherapy
    #if move.id == 'aromatherapy' or move.id == 'healbell': 
    #    for pokemon in user.side.pokemon:
    #        pokemon.cure_status()


    # belly drum
    if move.id == 'bellydrum' and user.hp > (0.5 * user.maxhp):
        boost(user, {'atk': 6})
        damage(user, 0.5, flag='percentmax')

    # bestow
    if move.id == 'bestow':
        if user.item != '' and target.item == '':
            target.item = user.item
            user.item = ''

    # camouflage
    # every battle played using the sim is a 'link battle'
    if move.id == 'camouflage':
        user.types = ['Normal']

    # conversion
    move_types = []
    if move.id == 'conversion':
        for user_move in user.moves:
            if dex.move_dex[user_move].type not in user.types:
                move_types.append(dex.move_dex[user_move].type)
        if len(move_types) > 0:
            user.types = [move_types[random.randint(0, len(move_types)-1)]]

    # this causes an attribute error and i dont know why
    # attrubiteError starts here
    # I THINK I FIGURED IT OUT
    # conversion 2
    #print(str(move))
    if move.id == 'conversion2':
        if user.last_damaging_move is not None:
            for type in dex.typechart_dex[dex.move_dex[user.last_damaging_move].type].damage_taken:
                if type not in user.types:
                    move_types.append(type)
        if len(move_types) > 0:
            user.types = [move_types[random.randint(0, len(move_types)-1)]]

    # curse
    if move.id == 'curse' and 'Ghost' not in user.types:
        boost(user, {'atk': 1, 'def': 1, 'spe': -1})

    # defog
    if move.id == 'defog':
        boost(target, {'evasion': -1})
        #target.side.side_condition = set()

    # entrainment
    if move.id == 'entrainment':
        target.ability = user.ability

    # flower shield
    if move.id == 'flowershield':
        if 'Grass' in user.types:
            boost(user, {'def': 1})
        if 'Grass' in target.types:
            boost(target, {'def': 1})

    # focus energy
    if move.id == 'focusenergy':
        user.crit_chance += 2

    # forests curse
    if move.id == 'forestscurse':
        target.types.append('Grass')

    # gastro acid
    if move.id == 'gastroacid':
        if target.ability not in ['multitype', 'stancechance', 'schooling', 'comatose', 'shieldsdown', 'disguise', 'rkssystem', 'battlebond', 'powerconstruct']:
            target.ability = 'suppressed'

    # guard split
    if move.id == 'guardsplit':
        avg_def = (user.stats.defense + target.stats.defense)/2
        avg_spd = (user.stats.specialdefense + target.stats.specialdefense)/2

        user.stats.defense =  avg_def
        target.stats.defense = avg_def

        user.stats.specialdefense = avg_spd
        target.stats.specialdefense = avg_spd

    # guard swap
    if move.id == 'guardswap':
        user_def = user.stats.defense
        target_def = target.stats.defense

        user_spd = user.stats.specialdefense
        target_spd = target.stats.specialdefense

        user.stats.defense = target_def
        target.stats.defense = user_def

        user.stats.specialdefense = target_spd
        target.stats.specialdefense = user_spd

    # heart swap
    if move.id == 'heartswap':
        user_boosts = user.boosts
        target_boosts = target.boosts

        user.boosts = target_boosts
        target.boosts = user_boosts

    # kinggsheild
    if move.id == 'kingsshield' and user.id == 'aegislash':
        user.form_change('aegislashshield')

    # pain split
    if move.id == 'painsplit':
        avg_hp = (user.hp + target.hp) /2
        user.hp = avg_hp if avg_hp < user.stats.hp else user.stats.hp
        target.hp = avg_hp if avg_hp < target.stats.hp else target.stats.hp

    # power split
    if move.id == 'powersplit':
        avg_atk = (user.stats.attack + target.stats.attack)/2
        avg_spa = (user.stats.specialattack + target.stats.specialattack)/2

        user.stats.attack = avg_atk
        target.stats.attack = avg_atk

        user.stats.specialattack = avg_spa
        target.stats.specialattack = avg_spa

    # power swap
    if move.id == 'powerswap':
        user_atk = user.stats.attack
        target_atk = target.stats.attack

        user_spa = user.stats.specialattack
        target_spa = target.stats.specialattack

        user.stats.attack = target_atk
        target.stats.attack = user_atk

        user.stats.specialattack = target_spa
        target.stats.specialattack = user_spa

    # power trick
    if move.id == 'powertrick':
        user_atk = user.stats.attack
        user_spa = user.stats.specialattack

        user.stats.specialattack = user_atk
        user.stats.attack = user_spa

    # psychoshift
    if move.id == 'psychoshift':
        if add_status(target, user.status):
            cure_status(user)

    # psychup
    if move.id == 'psychup':
        user.boosts = target.boosts

    # purify
    if move.id == 'purify':
        if cure_status(target):
            damage(user, -0.5, flag='percentmaxhp')
    
    # recycle
    if move.id == 'recycle':
        if user.last_used_item is not None and user.item == '':
            user.item = user.last_used_item

    # reflect type
    if move.id == 'reflecttype':
        user.types = target.types

    # refresh
    if move.id == 'refresh':
        if user.status in ['brn', 'par', 'psn', 'tox']:
            cure_status(user)

    # rest
    if move.id == 'rest':
        if user.status != 'slp':
            user.status = 'slp'
            user.sleep_n = 2
            damage(user, -1, flag='percentmaxhp')

    # role play
    if move.id == 'roleplay':
        user.ability = target.ability

    # simple beam
    if move.id == 'simplebeam':
        target.ability = 'simple'

    # sketch
    if move.id == 'sketch':
        if target.last_used_move is not None:
            if 'sketch' in user.moves:
                user.moves.remove('sketch')
            user.moves.append(target.last_used_move)

    # skill swap
    if move.id == 'skillswap':
        user_ability = user.ability
        target_ability = target.ability

        user.ability = target_ability
        target.ability = user_ability

    # sleep talk
    if move.id == 'sleeptalk':
        if user.status == 'slp' and len(user.moves) > 1:
            while move.id == 'sleeptalk':
                move = dex.move_dex[user.moves[random.randint(0, len(user.moves)-1)]]

    # soak
    if move.id == 'soak':
        target.types = ['Water']

    # speed swap
    if move.id == 'speedswap':
        user_speed = user.stats.speed
        target_speed = target.stats.speed

        user.stats.speed = target_speed
        target.stats.speed = user_speed

    # stockpile
    if move.id == 'stockpile':
        user.stockpile += 1
        if user.stockpile > 3:
            user.stockpile = 3
        boost(user, {'def': 1, 'spd': 1})

    # strength sap
    if move.id == 'strengthsap':
        if target.boosts['atk'] != -6:
            damage(user, -(get_attack(target, B.weather)))
            boost(target, {'atk': -1})

    # substitute
    if move.id == 'substitute':
        if not user.substitute and user.hp > user.stats.hp*0.25:
            user.substitute = True
            damage(user, 0.25, flag='percentmaxhp')
            user.substitute_hp = math.floor(0.25 * user.stats.hp)

    # switcheroo and trick
    if move.id == 'switcheroo' or move.id == 'trick':
        user_item = user.item
        target_item = target.item

        user.item = target_item
        target.item = user_item

    # topsy-turvy
    if move.id == 'topsyturvy':
        for stat in target.boosts:
            target.boosts[stat] = -target.boosts[stat]

    # trick or treat
    if move.id == 'trickortreat':
        target.types.append('Ghost')

    # worry seed
    if move.id == 'worryseed':
        target.ability = 'insomnia'

    # breaks protect
    if move.breaks_protect:
        if 'protect' in target.volatile_statuses:
            target.volatile_statuses.remove('protect')
        if 'banefulbunker' in target.volatile_statuses:
            target.volatile_statuses.remove('banefulbunker')
        if 'spikyshield' in target.volatile_statuses:
            target.volatile_statuses.remove('spikyshield')
        if 'kingsshield' in target.volatile_statuses:
            target.volatile_statuses.remove('kingsshield')

    # growth (the move) does another stat boost in the sun
    if move.id == 'growth':
        if B.weather == 'sunlight':
            boost(target, move.primary['B']['boosts'])

def create_move(B:Battle, p:Pokemon, c:Decision) -> dex.Move:
    '''
    ONLY NEEDS BATTLE FOR the pokemon's players used_zmove attribute

    This method takes in the user pokemon and the decision corresponding
    to that pokmeon and returns a Move (namedtuple) object that contains 
    all information about the move that pokemon will use.
    '''
    if c.type != 'move':
        return

    move = dex.move_dex[p.moves[c.selection]]

    # encore overwrites move decision
    if 'encore' in p.volatile_statuses and p.last_used_move is not None:
        move = dex.move_dex[p.last_used_move]
        #return move # Can you z move the encored move? I think yes?

    player = B.p2
    if p.player_uid == 1:
        player = B.p1
    if not can_z(p, move) or not c.zmove or player.used_zmove:
        return move

    # update z move power
    # THIS NEEDS UPDATING
    item = dex.item_dex[p.item]
    if item.zMove is True:
        zmove_id = dex.zmove_chart[item.id]
    else:
        zmove_id = re.sub(r'\W+', '', item.zMove.lower())
    base_move = move
    move = dex.move_dex[zmove_id]

    if move.base_power == 1:
        move = move._replace(base_power = base_move.z_move.base_power)
        move = move._replace(category = base_move.category)

    z_move = move.z_move._replace(boosts=base_move.z_move.boosts)
    z_move = move.z_move._replace(effect=base_move.z_move.effect)
    move = move._replace(z_move=z_move)
    return move

def populate_action_queue(q:List, p:Pokemon, c:Decision, m:dex.Move,
                            T:Player, B:Battle) -> None:
    '''
    ONLY NEEDS BATTLE AND PLAYER TO CALL resolve_priority()
    Creates and appends actions to the queue q for the given decisions.
    '''
    a = None

    # generate SWITCH actions
    if c.type == 'switch':
        a = Action('switch', user=p, pos=c.selection) 

    # generate MEGA EVOLUTION actions
    elif c.type == 'mega' and c.mega:
        a = Action('mega', user=p)

    # move decision actions
    elif c.type == 'move':
        a = Action('move', user=p, move=m, target=c.target)

    if a is not None:
        heapq.heappush(q, (resolve_priority(a, B, T), a))
    return

def resolve_priority(action, B:Battle, T:Player) -> float:
    '''
    ONLY NEEDS BATTLE AND PLAYER TO CALL get_speed()
    returns a number
    (action_priority_tier * 13000) + user.get_speed() + random.random()

    lower number is the higher priority

    multiply tier by 13_000 because 12_096 is maximum calculated speed
    stat of any pokemon

    add random.random() to the allow the priority queue to handle possible
    ties with a coin flip

    priority tiers
        0-pursuit on a pokemon that is switching out but not yet fainted
            -if mega, mega first then pursuit
        1-switches
            -calculated speed
        2-mega
            -calculated speed
            -update this pokemons later actions with new calculated speed
        3-15-moves
            - +5 to -7 priority tiers
                -Gale Wings, Prankster, Triage affect priority tier
            -calculated speed
                -Full Incense, Lagging Tail, Stall go last in priority tier
                -Quick Claw, Custap Berry go first in priority tier
                -Trick Room

    the priority queue can also be re-ordered by certain effects
    ex. Round, Dancer, Instruct, Pledge moves, After You, Quash
            
    '''

    # apt - action priority tier as defined above
    action_priority_tier : int = None

    if action.action_type == 'switch':
        action_priority_tier = 1
    elif action.action_type == 'mega':
        action_priority_tier = 2
    elif action.action_type == 'move':
        action_priority_tier = 3 + (5 - action.move.priority)

    # get_speed() returns higher number = faster speed
    # priority speed needs to be lower number = faster speed
    speed = 12096 - get_speed(action.user, B.weather, B.terrain,
                                B.trickroom, T.tailwind)

    # multiply priority tier by 13000 because it supercedes speed
    priority = action_priority_tier * 13000

    # random.random() is the tie breaker
    return priority + speed + random.random()
