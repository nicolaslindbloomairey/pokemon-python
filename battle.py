#from dex import ModdedDex
from side import Side
from data.data import Abilities, Formats, Items, Learnsets, Moves, Pokedex, Typechart

class Battle(ModdedDex):
    def __init__(self, formatid):
        format = ModdedDex.getFormat(formatid)
        super().__init__(format['mod'])
        #self.data.Scripts?

        self.log = []

        self.sides = [None, None]
        self.weatherData = {'id':''}
        self.terrainData = {'id':''}
        self.pseudoWeather = {}

        self.format = format['name']
        self.formatid = formatid
        #self.formatData = {'id': format.name}

        self.effect = {'id':''}
        self.effectData = {'id':''}
        self.event = {'id':''}

        self.gameType = format['gameType'] or 'singles'
        #self.reportExactHP = format.debug or False
        #self.replayExactHP = not format.team
        
        self.queue = []
        self.faintQueue = []
        self.messageLog = []

        #self.send = send

        self.turn = 0
        self.p1 = None
        self.p2 = None
        self.lastUpdate = 0
        self.weather = ''
        self.terrain = ''
        self.ended = False
        self.started = False
        self.active = False
        self.eventDepth = 0
        self.lastMove = ''
        self.activeMove = None
        self.activePokemon = None
        self.activeTarget = None
        self.midTurn = False
        self.currentRequest = ''
        self.lastMoveLine = 0
        self.reportPercentages = False
        self.supportCancel = False
        self.events = None

        self.abilityOrder = 0

        #self.prng = prng
        #self.prngSeed = self.prng.startingSeed.slice()
        self.teamGenerator = None

    def toString(self):
        return 'Battle: ' + self.format

    def runEvent(self, eventid, target, source, effect, relayVar, onEffect, fastExit):
        pass

    def join(self, slot, name, avatar, team):
        slotNum = 1 if slot=='p2' else 0
        #team = self.getTeam(team)
        #self.[slot] = Side(name, self, slotNum, team)
        setattr(self, slot, Side(name, self, slotNum, team))
        self.sides[slotNum] = getattr(self, slot)
        #self.sides[0] = getattr(self, slot)
        #self.sides.append(getattr(self, slot))

        #player = self[slot]
        #log

        self.start()
        #return player

    def start():
       pass 
