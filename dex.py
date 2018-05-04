import json
from collections import namedtuple

#this module is for searching the dex, aka all the game data

#missing statuses, scripts, rulesets(formats), formatsdata( event pokemon and thespeed moves), aliases

with open('data/abilities.json') as f:
    Abilities = json.load(f)
with open('data/formats.json') as f:
    Formats = json.load(f)
with open('data/items.json') as f:
    Items = json.load(f)
with open('data/learnsets.json') as f:
    Learnsets = json.load(f)
with open('data/moves.json') as f:
    Moves = json.load(f)
with open('data/pokedex.json') as f:
    Pokedex = json.load(f)
with open('data/typechart.json') as f:
    Typechart = json.load(f)
with open('data/natures.json') as f:
    Natures = json.load(f)

Dex = namedtuple('Dex', 'abilities formats items learnsets moves pokedex typechart natures')

blankPokemon = {
    'num': None,
    'species': None,
    'baseSpecies': None,

}


pokemon = {}

for i in Pokedex:
    stats = Stats(**i['baseStats'])
    baseabilities = BaseAbilities(**i['abilities'])
    genderRatio = GenderRatio(**i['genderRatio'])
    pokemon[i] = Pokemon(




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
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')
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



