import json
from collections import namedtuple

#this module is for searching the dex, aka all the game data

Abilities = json.load(open('data/abilities.json'))
Formats = json.load(open('data/formats.json'))
Items = json.load(open('data/items.json'))
Learnsets = json.load(open('data/learnsets.json'))
Moves = json.load(open('data/moves.json'))
Pokedex = json.load(open('data/pokedex.json'))
Typechart = json.load(open('data/typechart.json'))
Natures = json.load(open('data/natures.json'))
#missing statuses, scripts, rulesets(formats), formatsdata( event pokemon and their moves), aliases



#the namedtuples
Effect = namedtuple('Effect', 'name')

Ability = namedtuple('Ability', 'desc shortDesc id name rating num') #way more props, supressweather, onmodifymovepriority, onbasepowerpriority

Format = namedtuple('Format', 'name desc mod gameType forcedLevel teamLength timer ruleset banlist')
TeamLength = namedtuple('TeamLength', 'validate battle')
Timer = namedtuple('Timer', 'starting perTurn maxPerTurn maxFirstTurn timeoutAutoChoose')

Item = namedtuple('Item', 'id name spritenum isBerry onTakeItem zMove zMoveFrom zMoveUser moveModifier megaStone megaEvolves num gen desc') #some missing props
MoveModifier = namedtuple('MoveModifier', 'basePower type')

#learnset? pokemon -> move -> how it can learn it

Move = namedtuple('Move', 'num accuracy basePower category desc shortDesc id name pp priority flags boosts drain isZ critRatio secondary target type zMovePower zMoveBoosts contestType') 
#flags? move -> integer

Pokemon = namedtuple('Pokemon', 'num species baseSpecies forme formeLetter types genderRatio baseStats abilities height weight color prevo evos evoLevel eggGroups otherFormes tier requiredItem')
GenderRatio = namedtuple('GenderRatio', 'male female')
Stats = namedtuple('Stats', 'hp atk def spa spd spe')
BaseAbilities = namedtuple('BaseAbilities', 'normal0 normal1 hidden')

TypeChart = namedtuple('TypeChart', 'damageTaken HPivs')
DamageTaken = namedtuple('DamageTaken', 'prankster par brn trapped powder sandstorm hail frz psn tox Bug Dark Dragon Electric Fairy Fighting Fire Flying Ghost Grass Ground Ice Normal Poison Psychic Rock Steel Water')

Nature = namedtuple('Nature', 'id name plus minus')



'''
    methods from the js version
        getName(name)
        getImmunity(source, target)
        getEffectiveness(source, target)
        getSpecies(species)
        getTemplate(name)
        getLearnset(template)
        getMove(name)
        getMoveCopy(move)
        getEffect(name)
        getFormat(name)
        getItem(name)
        getAbility(name)
        getType(type)
        getNature(nature)
        spreadModify(stats, set)
        natureModify(stats, nature)
        getHiddenPower(ivs)
        getRuleTable(format, depth=0)
        shuffle(arr)
        levenshtein(s, t, l)
        clampIntRange(num, min, max)
        getTeamGenerator(format, seed)
        generateTeam(format, seed)
        dataSearch(target, searchIn, isInexact)
        packTeam(team)
        fastUnpackTeam(buf)
        deepClone(obj)
        loadDataFile(basePath, dataType)
        includeMods()
        includeModData()
        includeData()
        loadData()
        includeFormats()
        installFormat(id, format)
'''



