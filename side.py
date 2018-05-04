from pokemon import Pokemon

class Side:
    def __init__(self, name, battle, sideNum, team):
        self.battle = battle
        self.n = sideNum
        self.name = name
        #avatar is unneccesary i think

        self.pokemon = []
        self.active = [None]

        self.sideConditions = {}

        self.pokemonLeft = 0

        self.faintedLastTurn = False
        self.faintedThisTurn = False

        self.choice = {
            'cantUndo': False,
            'error': '',
            'actions': [],
            'forcedSwitchesLeft': 0,
            'forcedPassesLeft': 0,
            'switchIns': {},
            'zMove': False,
            'mega': False
        }

        '''
            current request is one of
            move - move request
            switch - fainted pokemon or for u-turn and what not
            teampreview - beginning of battle pick which pokemon
            '' - no request
        '''
        self.currentRequest = ''
        self.maxTeamSize = 6
        self.foe = None

        self.id = 'p2' if sideNum == 1 else 'p1'

        if self.battle.gameType == 'doubles':
            self.active = [None, None]
        elif self.battle.gameType == 'triples' or self.battle.gameType == 'rotation':
            self.active = [None, None, None]

        self.team = team

        for i in range(len(team)):
            self.pokemon.append(Pokemon(self.team[i], self))

        self.pokemonLeft = len(self.pokemon)

        for i in range(len(self.pokemon)):
            self.pokemon[i].position = i


