import json

def reformat_moves():
    with open('old_moves.json') as f:
        moves = json.load(f)

    move_attr_set = set()
    flags = set()

    for move in moves:
        for attr in moves[move]:
            move_attr_set.add(attr)
        for flag in moves[move]['flags']:
            flags.add(flag)

    for move in moves:
        for attr in move_attr_set:
            if attr not in moves[move]:
                moves[move][attr] = None

    for move in list(moves.keys()):
        if moves[move]['isNonstandard']:
            del moves[move]
        else:
            del moves[move]['isNonstandard']

    for move in moves:
        for flag in flags:
            if flag not in moves[move]['flags']:
                moves[move]['flags'][flag] = False
            else:
                moves[move]['flags'][flag] = True
        
        drain = moves[move].pop('drain')
        if drain is not None:
            moves[move]['drain'] = drain[0]/drain[1]
        else:
            moves[move]['drain'] = 0
        heal = moves[move].pop('heal')
        if heal is not None:
            moves[move]['heal'] = heal[0]/heal[1]
        else:
            moves[move]['heal'] = 0

        # recoil moves
        recoil = moves[move].pop('recoil')
        recoil_damage = 0
        if recoil is not None:
            recoil_damage = recoil[0]/recoil[1]
        type = 'damage'
        condition = 'hit'
        if move in ['finalgambit', 'healingwish', 'lunardance', 'memento', 'explosion', 'selfdestruct']:
            recoil_damage = 1
            type = 'maxhp' 
        if move in ['explosion', 'selfdestruct']:
            condition = 'always'
        if move == 'struggle':
            recoil_damage = 0.25
            type = 'maxhp'
            condition = 'always'
        if move == 'mindblown':
            recoil_damage = 0.50
            type = 'maxhp'
            condition = 'always'
        if move in ['jumpkick', 'highjumpkick']:
            recoil_damage = 0.50
            type = 'maxhp'
            condition = 'miss'

        moves[move]['recoil'] = {
            'damage': recoil_damage,
            'type': type,
            'condition': condition,
        }
        moves[move]['target_type'] = moves[move].pop('target')
        moves[move]['base_power'] = moves[move].pop('basePower')
        moves[move]['short_desc'] = moves[move].pop('shortDesc')
        moves[move]['ignore_ability'] = moves[move].pop('ignoreAbility')
        moves[move]['ignore_defensive'] = moves[move].pop('ignoreDefensive')
        moves[move]['ignore_evasion'] = moves[move].pop('ignoreEvasion')
        moves[move]['ignore_immunity'] = moves[move].pop('ignoreImmunity')
        moves[move]['breaks_protect'] = moves[move].pop('breaksProtect')
        moves[move]['defensive_category'] = moves[move].pop('defensiveCategory')
        moves[move]['force_switch'] = moves[move].pop('forceSwitch')
        moves[move]['future_move'] = moves[move].pop('isFutureMove')
        moves[move]['unreleased'] = moves[move].pop('isUnreleased')
        moves[move]['viable'] = moves[move].pop('isViable')
        moves[move]['multi_hit'] = moves[move].pop('multihit')
        moves[move]['no_faint'] = moves[move].pop('noFaint')
        moves[move]['no_pp_boosts'] = moves[move].pop('noPPBoosts')
        moves[move]['no_sketch'] = moves[move].pop('noSketch')
        moves[move]['pseudo_weather'] = moves[move].pop('pseudoWeather')
        moves[move]['thaws_target'] = moves[move].pop('thawsTarget')
        moves[move]['self_switch'] = moves[move].pop('selfSwitch')
        moves[move]['side_condition'] = moves[move].pop('sideCondition')
        moves[move]['sleep_usable'] = moves[move].pop('sleepUsable')
        moves[move]['volatile_status'] = moves[move].pop('volatile_status')
        moves[move]['true_damage'] = moves[move].pop('damage')

        moves[move]['crit_ratio'] = moves[move].pop('critRatio')
        if moves[move]['crit_ratio'] is None:
            moves[move]['crit_ratio'] = 0

        if moves[move]['target_type'] == 'self':
            moves[move]['self'] = {
                'boosts': moves[move]['boosts'],
                'status': moves[move]['status'],
                'volatile_status': moves[move]['volatile_status'],
            }
            moves[move]['boosts'] = None
            moves[move]['status'] = None
            moves[move]['volatile_status'] = None
        moves[move]['primary'] = {
            'boosts': moves[move].pop('boosts'),
            'status': moves[move].pop('status'),
            'volatile_status': moves[move].pop('volatile_status'),
            'self': moves[move].pop('self')
        }
        #temp = False
        #for key in moves[move]['primaries']:
        #    if moves[move]['primaries'][key] is not None:
        #        temp = True
        #if not temp:
        #    moves[move]['primaries'] = None

        if moves[move]['secondary'] is None:
            del moves[move]['secondary']
            moves[move]['secondary'] = []
        else:
            moves[move]['secondary'] = [ moves[move].pop('secondary') ]
        if moves[move]['tertiary'] is None:
            del moves[move]['tertiary']
        else:
            moves[move]['secondary'].append(moves[move].pop('tertiary'))

        moves[move].pop('useTargetOffensive')
        moves[move].pop('selfdestruct')
        moves[move].pop('contestType')
        moves[move].pop('hasCustomRecoil')
        moves[move].pop('stealsBoosts')
        moves[move].pop('struggleRecoil')
        moves[move].pop('pressureTarget')
        moves[move].pop('onBasePowerPriority')
        moves[move].pop('onTryHit')
        moves[move].pop('nonGhostTarget')
        moves[move].pop('ohko')
        moves[move].pop('stallingMove')
        moves[move].pop('multiaccuracy')
        moves[move].pop('noMetronome')
        moves[move].pop('effect')
        moves[move].pop('mindBlownRecoil')
        moves[move]['z_move'] = {
            'boosts': moves[move].pop('zMoveBoost'),
            'crystal': moves[move].pop('isZ'),
            'effect': moves[move].pop('zMoveEffect'),
            'base_power': moves[move].pop('zMovePower')
        }

    with open('moves.json', 'w') as outfile:
        json.dump(moves, outfile)


reformat_moves()
