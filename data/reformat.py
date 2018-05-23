import json

with open('moves.json') as f:
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
    moves[move]['base_power'] = moves[move].pop('basePower')
    moves[move]['short_desc'] = moves[move].pop('shortDesc')
    moves[move]['contest_type'] = moves[move].pop('contestType')
    moves[move]['crit_ratio'] = moves[move].pop('critRatio')
    moves[move]['ignore_ability'] = moves[move].pop('ignoreAbility')
    moves[move]['ignore_defensive'] = moves[move].pop('ignoreDefensive')
    moves[move]['ignore_evasion'] = moves[move].pop('ignoreEvasion')
    moves[move]['ignore_immunity'] = moves[move].pop('ignoreImmunity')
    moves[move]['breaks_protect'] = moves[move].pop('breaksProtect')
    moves[move]['defensive_category'] = moves[move].pop('defensiveCategory')
    moves[move]['force_switch'] = moves[move].pop('forceSwitch')
    moves[move]['has_custom_recoil'] = moves[move].pop('hasCustomRecoil')
    moves[move]['future_move'] = moves[move].pop('isFutureMove')
    moves[move]['unreleased'] = moves[move].pop('isUnreleased')
    moves[move]['z_crystal'] = moves[move].pop('isZ')
    moves[move]['viable'] = moves[move].pop('isViable')
    moves[move]['multi_hit'] = moves[move].pop('multihit')
    moves[move]['no_faint'] = moves[move].pop('noFaint')
    moves[move]['no_pp_boosts'] = moves[move].pop('noPPBoosts')
    moves[move]['no_sketch'] = moves[move].pop('noSketch')
    moves[move].pop('multiaccuracy')
    moves[move].pop('noMetronome')
    moves[move].pop('effect')
    moves[move].pop('mindBlownRecoil')



print(moves['tackle'])

print(move_attr_set)
print(flags)
print(len(flags))

with open('reformat.json', 'w') as outfile:
    json.dump(moves, outfile)
