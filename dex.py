import json
import time
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



#-------------
#POKEDEX
#-------------
pokemonAttributes = ['id', 'num', 'species', 'baseSpecies', 'forme', 'formeLetter', 'types', 
                        'genderRatio', 'baseStats', 'abilities', 'height', 'weight', 'color',
                        'prevo', 'evos', 'evoLevel', 'eggGroups', 'otherFormes', 'tier', 'requiredItem']
pokemon = {}

#Pokemon = namedtuple('Pokemon', 'id num species baseSpecies forme formeLetter types genderRatio baseStats abilities height weight color prevo evos evoLevel eggGroups otherFormes tier requiredItem')
Pokemon = namedtuple('Pokemon', pokemonAttributes)
GenderRatio = namedtuple('GenderRatio', 'male female')
Stats = namedtuple('Stats', 'hp attack defense specialattack specialdefense speed')
BaseAbilities = namedtuple('BaseAbilities', 'normal0 normal1 hidden')

for i in Pokedex:
    for a in pokemonAttributes:
        if a not in Pokedex[i]:
            Pokedex[i][a] = None
        else:
            if a == 'genderRatio':
                Pokedex[i][a] = GenderRatio(Pokedex[i][a]['M'], Pokedex[i][a]['F'])
            elif a == 'baseStats':
                Pokedex[i][a] = Stats(Pokedex[i][a]['hp'], Pokedex[i][a]['atk'], Pokedex[i][a]['def'], Pokedex[i][a]['spa'],  Pokedex[i][a]['spd'], Pokedex[i][a]['spe'])
            elif a == 'abilities':
                Pokedex[i][a] = BaseAbilities(Pokedex[i][a].get('0'), Pokedex[i][a].get('1'), Pokedex[i][a].get('H'))

    Pokedex[i]['id'] = i

    #pokemon[i] = Pokemon(Pokedex[i]['id'], Pokedex[i]['num'], Pokedex[i]['species'], Pokedex[i]['baseSpecies'], Pokedex[i]['forme'], Pokedex[i]['formeLetter'], Pokedex[i]['types'], Pokedex[i]['genderRatio'], Pokedex[i]['baseStats'], Pokedex[i]['abilities'], Pokedex[i]['height'], Pokedex[i]['weight'], Pokedex[i]['color'], Pokedex[i]['prevo'], Pokedex[i]['evos'], Pokedex[i]['evoLevel'], Pokedex[i]['eggGroups'], Pokedex[i]['otherFormes'], Pokedex[i]['tier'], Pokedex[i]['requiredItem']) 
    pokemon[i] = Pokemon._make([Pokedex[i][j] for j in pokemonAttributes])


#------------
#ABILITIES
#------------
abilityAttributes = ['id', 'desc', 'shortDesc', 'name', 'rating', 'num'] 
abilities = {}

Ability = namedtuple('Ability', abilityAttributes) #way more props, supressweather, onmodifymovepriority, onbasepowerpriority

for i in Abilities:
    for a in abilityAttributes:
        if a not in Abilities[i]:
            Abilities[i][a] = None

    #abilities[i] = Ability(Abilities[i]['id'], Abilities[i]['desc'], Abilities[i]['shortDesc'], Abilities[i]['name'], Abilities[i]['rating'], Abilities[i]['num']) 
    abilities[i] = Ability._make([Abilities[i][j] for j in abilityAttributes])


#---------
#Format
#---------
formatAttributes = ['id', 'name', 'desc', 'mod', 'gameType', 'forcedLevel', 'teamLength', 'timer', 'ruleset', 'banlist'] 
formats = {}

Format = namedtuple('Format', formatAttributes)
TeamLength = namedtuple('TeamLength', 'validate battle')
Timer = namedtuple('Timer', 'starting perTurn maxPerTurn maxFirstTurn timeoutAutoChoose')

for i in Formats:
    for a in formatAttributes:
        if a not in Formats[i]:
            Formats[i][a] = None
        else:
            if a == 'teamLength':
                Formats[i][a] = TeamLength(Formats[i][a]['validate'], Formats[i][a]['battle'])
            elif a == 'timer':
                Formats[i][a] = Timer(Formats[i][a]['starting'], Formats[i][a]['perTurn'], Formats[i][a]['maxPerTurn'], Formats[i][a]['maxFirstTurn'],  Formats[i][a]['timeoutAutoChoose'])

    Formats[i]['id'] = i

    #formats[i] = Format(Formats[i]['name'], Formats[i]['desc'], Formats[i]['mod'], Formats[i]['gameType'], Formats[i]['forcedLevel'], Formats[i]['teamLength'], Formats[i]['timer'], Formats[i]['ruleset'], Formats[i]['banlist'], Formats[i]['id'])
    formats[i] = Format._make([Formats[i][j] for j in formatAttributes])

#--------
#Items
#---------

itemAttributes = ['id', 'name', 'spritenum', 'isBerry', 'zMove', 'zMoveFrom', 'zMoveUser', 'megaStone', 'megaEvolves', 'num', 'gen', 'desc']
items = {}

Item = namedtuple('Item', itemAttributes) #some missing props

for i in Items:
    for a in itemAttributes:
        if a not in Items[i]:
            Items[i][a] = None

    #items[i] = Fformatsformatsormat(Formats[i]['name'], Formats[i]['desc'], Formats[i]['mod'], Formats[i]['gameType'], Formats[i]['forcedLevel'], Formats[i]['teamLength'], Formats[i]['timer'], Formats[i]['ruleset'], Formats[i]['banlist'], Formats[i]['id'])
    #items[i] = Item(Items[i]['id'], Items[i]['num'], Items[i]['spritenum'], Items[i]['isBerry'], Items[i]['zMove'], Items[i]['zMoveFrom'], Items[i]['zMoveUser'], Items[i]['megaStone'], Items[i]['id'], Items[i]['id'], Items[i]['id'], Items[i]['id'], Items[i]['id'], Items[i]['id'], 
    items[i] = Item._make([Items[i][j] for j in itemAttributes])


#--------
#Moves
#---------

moveAttributes = ['id', 'name', 'num', 'accuracy', 'basePower', 'category', 'desc', 'shortDesc', 'pp', 'priority', 'flags', 'boosts', 'drain', 'isZ', 'critRatio', 'secondary', 'target', 'type', 'zMovePower', 'zMoveBoosts', 'contestType']
moves = {}

Move = namedtuple('Move', moveAttributes) #some missing props

for i in Moves:
    for a in moveAttributes:
        if a not in Moves[i]:
            Moves[i][a] = None

    moves[i] = Move._make([Moves[i][j] for j in moveAttributes])

#--------
#TypeChart
#---------

typechartAttributes = ['damageTaken', 'HPivs']
damagetakenAttributes = ['prankster', 'par', 'brn', 'trapped', 'powder', 'sandstorm', 'hail', 'frz', 'psn', 'tox', 'Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

typecharts = {}

TypeChart = namedtuple('TypeChart', 'damageTaken HPivs')
DamageTaken = namedtuple('DamageTaken', 'prankster par brn trapped powder sandstorm hail frz psn tox Bug Dark Dragon Electric Fairy Fighting Fire Flying Ghost Grass Ground Ice Normal Poison Psychic Rock Steel Water')

for i in Typechart:
    for a in typechartAttributes:
        if a not in Typechart[i]:
            Typechart[i][a] = None
        else:
            if a == 'damageTaken':
                for y in damagetakenAttributes:
                    if y not in Typechart[i][a]:
                        Typechart[i][a][y] = None
                Typechart[i][a] = DamageTaken._make([Typechart[i][a][j] for j in damagetakenAttributes])

    typecharts[i] = TypeChart._make([Typechart[i][j] for j in typechartAttributes])


#--------
#Natures
#---------
natureAttributes = ['id', 'name', 'plus', 'minus']
natures = {}

Nature = namedtuple('Nature', natureAttributes)

for i in Natures:
    for a in natureAttributes:
        if a not in Natures[i]:
            Natures[i][a] = None

    natures[i] = Nature._make([Natures[i][j] for j in natureAttributes])


#learnset? pokemon -> move -> how it can learn it

#flags? move -> integer


Dex = namedtuple('Dex', 'abilities formats items moves pokemon typecharts natures')
dex = Dex(abilities, formats, items, moves, pokemon, typecharts, natures)


'''
    methods from the js version

    most of these are now one liners,
    eg. dex.pokemon['charizard'] replaces dex.getTemplate('charizard')

    the dex object hold a great many immutable tuples that define the game data

    if i decide i need any of these, they wil be implemented below

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



