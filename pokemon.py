import dex as Dex
import random
import math

class Pokemon:
    def __init__(self, set, side):
        self.side = side
        self.battle = side.battle

        self.set = set

        #pokemonScripts?

        #self.baseTemplate = self.battle.getTemplate(set.species or set.name)
        #if not self.baseTemplate.exists:
        #    raise Exception("unidentified species")

        self.species = set['species']
        #if set.name == set.species or not set.name:
        #    set.name = self.baseTemplate.baseSpecies

        self.name = set['name']
        #self.speciesid = toId(self.species)
        #self.template = self.baseTemplate
        self.moves = []
        self.baseMoves = self.moves
        self.movepp = {}
        self.moveset = []
        self.baseMoveset = []

        self.trapped = False
        self.maybeTrapped = False
        self.maybeDisable = False
        self.illusion = None
        self.fainted = False
        self.faintQueued = False
        self.lastItem = ''
        self.ateBerry = False
        self.status = ''
        self.position = 0
        
        self.lastMove = ''
        self.moveThisTurn = ''

        self.lastDamage = 0
        self.lastAttackedBy = None
        self.usedItemThisTurn = False
        self.newlySwitched = False
        self.beingCalledBack = False
        self.isActive = False
        self.activeTurns = 0

        self.isStarted = False
        self.transformed = False
        self.duringMove = False
        self.speed = 0
        self.abilityOrder = 0

        #self.level = set['forcedLevel'] or set['level'] or 100
        self.level = set['level']

        self.gender = 'N'
        #self.genders = set.gender or self.template.gender or 'M' if random.random() * 2 < 1 else 'F'
        #if self.gender == 'N':
        #    self.gender = ''

        #self.happiness = set.happiness if set.happiness is int else 255
        #self.pokeball = self.set.pokemon or 'pokeball'

        self.fullname = self.side.id + ': ' + self.name
        self.details = self.species + ('' if self.level == 100 else ', L' + str(self.level)) + ('' if self.gender == '' else ', ' + self.gender) + (', shiny' if False else '')

        self.id = self.fullname

        self.statusData = {}
        self.volatiles = {}

        #self.height = self.template.height
        #self.heightm = self.template.heightm
        #self.weight = self.template.weight
        #self.weightkg = self.template.weightkg

        self.baseAbility = set['ability']
        self.ability = self.baseAbility
        self.item = set['item']
        self.abilityData = {'id': self.ability}
        self.itemData = {'id': self.item}
        #self.speciesData = {'id': self.speciesid}

        #self.types = self.baseTemplate.types
        self.addedType = ''
        self.knownType = True

        '''
        if self.set['moves'] is not None:
            for i in range(len(set['moves']):
                move = self.battle.getMove(self.set.moves[i])
                if move.id is None:
                    continue
                if move.id == 'hiddenpower' and move.type != 'Normal':
                    if set.hpType is None:
                        set.hpType = move.type
                    move = self.battle.getMove('hiddenpower')
                self.baseMoveset['move'] = move.name
                self.baseMoveset['id'] = move.id
                self.baseMoveset['pp'] = move.pp if move.noPPBoosts or move.isZ else move.pp * 8 / 5
                self.baseMoveset['maxpp'] = move.pp if move.noPPBoosts or move.isZ else move.pp * 8 / 5
                self.baseMoveset['target'] = move.target
                self.baseMoveset['disabled'] = False
                self.baseMoveset['disabledSource'] = ''
                self.baseMoveset['used'] = False

                self.moves.append(move.id)
        '''
        self.moves = set['moves']

        #self.canMegaEvo = self.battle.canMegaEvo(self)

        if 'evs' not in set:
            self.set['evs'] = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
        if 'ivs' not in set:
            self.set['ivs'] = {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}

        stats = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
        for i in stats:
            if i not in self.set['evs']:
                self.set['evs'][i] = 0
            if i not in self.set['ivs']:
                self.set['ivs'][i] = 31

        #self.hpType = self.battle.getHiddenPower(self.set.ivs).type
        self.set['boosts'] = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0}
        self.set['stats'] = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}

        self.isStale = 0
        self.isStaleCon = 0
        #self.isStaleHP = self.maxhp
        self.isStalePPTurns = 0

        self.baseIvs = self.set['ivs']
        #self.baseHpType = self.hpType
        #self.baseHpPower = self.hpPower

        self.clearVolatile(True)
        #self.maxhp = self.template.maxHP or self.baseStats.hp
        #self.hp = self.hp or self.maxhp

    
    def toString(self):
        fullname = self.fullname
        if self.illusion is not None:
            fullname = self.illusion.fullname

        positionList = 'abcdef'
        if self.isActive:
            return fullname[:2] + positionList[self.position] + fullname[2:]
        return fullname

    def getDetailsInner(self, side):
        if self.illusion is not None:
            return self.illusion.details + '|' + self.getHealthInner(side)
        return self.details + '|' + self.getHealthInner(side)

    def updateSpeed(self):
        self.speed = self.getDecisionSpeed()

    def calculateStat(self, statName, boost, modifier):
        statName = toId(statName)

        if statName == 'hp':
            return self.maxhp

        stat = self.stats[statName]

        if 'wonderroom' in self.battle.pseudoWeather:
            if statName == 'def':
                stat = self.stats['spd']
            elif statName == 'spd':
                stat = self.stats['def']

        boosts = {}
        boosts[statName] = boost
        boosts = self.battle.runEvent('ModifyBoost', self, None, None, boosts)
        boost = boosts[statName]
        boostTable = [1, 1.5, 2, 2.5, 3, 3.5, 4]
        if boost > 6:
            boost = 6
        if boost < -6:
            boost = -6
        if boost >= 0:
            stat = math.floor(stat * boostTable[boost])
        else:
            stat = math.floor(stat / boostTable[-boost])

        stat = self.battle.modify(stat, (modifier or 1))

        if self.battle.getStatCallback is not None:
            stat = self.battle.getStatCallback(stat, statName, this)

        return stat

    def getStat(self, statName, unboosted, unmodified):
        statName = toId(statName)

        if statName == 'hp':
            return self.maxhp

        stat = self.stats[statName]

        if unmodified and 'wonderroom' in self.battle.pseudoWeather:
            if statName == 'def':
                statName = 'spd'
            elif statName == 'spd':
                statName = 'def'

        if unboosted is None:
            boosts = self.battle.runEvent('ModifyBoost', self, None, None, self.boosts)
            boost = boosts[statName]
            boostTable = [1, 1.5, 2, 2.5, 3, 3.5, 4]
            if boost > 6:
                boost = 6
            if boost < -6:
                boost = -6
            if boost >= 0:
                stat = math.floor(stat * boostTable[boost])
            else:
                stat = math.floor(stat / boostTable[-boost])

        if unmodified is None:
            statTable = {'atk':'Atk', 'def':'Def', 'spa':'SpA', 'spd':'SpD', 'spe':'Spe'}
            stat = self.battle.runEvent('Modify' + statTable[statName], self, None, None, stat)

        if self.battle.getStatCallback is not None:
            stat = self.battle.getStatCallback(stat, statName, self, unboosted)

        return stat

    def getDecisionSpeed(self):
        speed = self.getStat('spe', False, False)
        if speed > 10000:
            speed = 10000
        if self.battle.getPseudoWeather('trickroom'):
            speed = 0x2710 - speed
        return speed & 0x1FFF

    def getWeight(self):
        weight = self.template.weightkg
        weight = self.battle.runEvent('ModifyWeight', self, None, None, weight)
        if weight < 0.1:
            weight = 0.1
        return weight

    def getMoveData(self, move):
        move = self.battle.getMove(move)
        for i in range(len(self.moveset)):
            moveData = self.moveset[i]
            if moveData.id == move.id:
                return moveData

        return None

    def getMoveTargets(self, move, target):
        targets = []
        if move.target == 'all':
            pass
        elif move.target == 'foeSide':
            pass
        elif move.target == 'allySide':
            pass
        elif move.target == 'allyTeam':
            if not move.target.startsWith('foe'):
                for i in range(len(self.side.active)):
                    if not self.side.active[i].fainted:
                        targets.append(self.side.active[i])
            if not move.target.startsWith('ally'):
                for i in range(len(self.side.foe.active)):
                    if not self.side.foe.active[i].fainted:
                        targets.append(self.side.foe.active[i])
        elif move.target == 'allAdjacent':
            for i in range(len(self.side.active)):
                if self.battle.isAdjacent(self, self.side.active[i]):
                    targets.append(self.side.active[i])
        elif move.target == 'allAdjacentFoes':
            for i in range(len(self.side.foe.active)):
                if self.battle.isAdjacent(self, self.side.foe.active[i]):
                    targets.append(self.side.foe.active[i])
        else:
            selectedTarget = target
            if target is None or (target.fainted and target.side != self.side):
                target = self.battle.resolveTarget(self, move)
            if target.side.active.length > 1:
                if not move.flags['charge'] or self.volatiles['twoturnmove'] or (move.id.startsWith('solarb') and self.battle.isWeather(['sunnyday', 'desolateland'])) or (self.hasItem('powerherb') and move.id != 'skydrop'):
                    target = self.battle.priorityEvent('RedirectTarget', self, self, move, target)
            if selectedTarget != target:
                self.battle.retargetLastMove(target)
            targets = [target]

            if move.pressureTarget == True:
                if move.pressureTarget == 'foeSide':
                    for i in range(len(self.side.foe.active)):
                        if self.side.foe.active[i] and not self.side.foe.active[i].fainted:
                            targets.append(self.side.foe.active[i])

        return targets

    def ignoringAbility(self):
        return (self.battle.gen >= 5 and not self.isActive) or (self.volatiles['gastroacid'] and not self.ability in {'comatose':1, 'multitype':1, 'schooling':1, 'stancechange':1})

    def ignoringItem(self):
        return (self.battle.gen >= 5 and not self.isActive) or (self.hasAbility('klutz') and not self.getItem().ignoreKlutz) or self.volatiles['embargo'] or self.battle.pseudoWeather['magicroom'];

    def deductPP(self, move, amount, source):
        move = self.battle.getMove(move)
        ppData = self.getMoveData(move)
        if ppData is None:
            return False
        ppData.used = True
        if ppData.pp is None:
            return False
        
        ppData.pp -= amount or 1
        if ppData.pp <= 0:
            ppData.pp = 0
        if ppData.virtual == True:
            foeActive = self.side.foe.active
            for i in range(len(foeActive)):
                if foeActive[i].isStale >= 2:
                    if move.selfSwitch is True:
                        self.isStalePPTurns += 1
                    return True
        self.isStalePPTurns = 0
        return True

    def moveUsed(self, move, targetLoc):
        self.lastMove = self.battle.getMove(move).id
        self.lastMoveTargetLoc = targetLoc
        self.moveThisTurn = self.lastMove

    def gotAttacked(self, move, damage, source):
        if damage is None:
            damage = 0
        move = self.battle.getMove(move)
        self.lastAttackedBy = {'pokemon': source, 'damage': damage, 'move':move.id, 'thisTurn': True}

    def getLockedMove(self):
        lockedMove = self.battle.runEvent('LockMove', self)
        if lockedMove == True:
            lockedMove = False
        return lockedMove

    def getMoves(self, lockedMove, restrictData):
        if lockedMove is not None:
            lockedMove = toId(lockedMove)
            self.trapped = True
            if lockedMove == 'recharge':
                return [{'move':'Recharge', 'id':'recharge'}]
            for i in range(len(self.moveset)):
                moveEntry = self.moveset[i]
                if moveEntry.id != lockedMove:
                    continue
                return [{'move': moveEntry.move, 'id': moveEntry.id}]
            return [{'move': self.battle.getMove(lockedMove).name, 'id':lockedMove}]
        moves = []
        hasValidMove = False
        for i in range(len(self.moveset)):
            moveEntry = self.moveset[i]

            moveName = moveEntry.move
            if moveEntry.id == 'hiddenpower':
                moveName = 'Hidden Power ' + self.hpType
                if self.battle.gen < 6:
                    moveName += ' ' + self.hpPower
            elif moveEntry.id == 'return':
                moveName = 'Return 102'
            elif moveEntry.id == 'frustration':
                moveName = 'Frustration 102'
            target = moveEntry.target
            if moveEntry.id == 'curse':
                if not self.hasType('Ghost'):
                    target = self.battle.getMove('curse').nonGhostTarget or moveEntry.target
            disabled = moveEntry.disabled
            if moveEntry.pp <= 0 or disabled and len(self.side.active) >= 2 and self.battle.targetTypeChoices(target):
                disabled = True
            elif disabled == 'hidden' and restrictData == True:
                disabled = False
            if not disabled:
                hasValidMove = True

            move.append({'move':moveName, 'id':moveEntry.id, 'pp':moveEntry.pp, 'maxpp':moveEntry.maxpp, 'target':target, 'disabled':disabled})

        if hasValidMove == True:
            return moves
        return []

    def clearVolatile(self, init):
        self.boosts = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0}

        self.transformed = False
        self.ability = self.baseAbility
        for i in self.volatiles:
            #remove volatile
            pass

        self.volatiles = {}
        self.swtichFlag = False
        self.forceSwtichFlag = False

        self.lastMove = ''
        self.moveThisTurn = ''

        self.lastDamage = 0
        self.lastAttackedBy = None
        self.newlySwitched = True
        self.beingCalledBack = False

        #self.formeChange(self.baseTemplate)


