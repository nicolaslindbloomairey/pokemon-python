'''
Nicolas Lindbloom-Airey

sim.py

This file has the methods that would be called by the user of the simulator.
First one must create a new battle and then one can either call run() which
will run the battle from start to finish without input from players, or
you can call choose for each player and do_turn do execute a single turn.

The caller of the simulator has access to the Battle dataclass which has
all the information about the battle. Its fields should never be edited and
Its methods should never be called. The caller has access so they can view
the state of the battle. No info is hidden.
'''
import heapq
from sim.player import *


def new_battle(format_str:str, name1:str, team1:List[PokemonSet],
                name2:str, team2:List[PokemonSet], debug:bool) -> Battle:
    return Battle(format_str, name1, team1, name2, team2, debug)

def choose(B:Battle, player_uid:int, choice:str) -> None:
    '''
    Sets the player with given player_uid in given Battle choice
    to the given choice.
    '''
    choice = choice.split(' ')
    c = Decision(choice[0], int(choice[1]))
    if player_uid == 1:
            B.p1.choice = c
    if player_uid == 2:
            B.p2.choice = c
    return

def run(B:Battle) -> None:
    '''
    Runs the Battle from start to finish as if each player ran out of time.
    '''
    MAX_TURNS = 500
    while not B.ended:
        default_decide(B.p1)
        default_decide(B.p2)
        do_turn(B)
        if B.turn > MAX_TURNS:
            #sys.exit("Battle reached max number of allowed turns")
            break
    return

def do_turn(B:Battle) -> None:
    '''
    To be called once both sides have made their decisions.
    Updates the game state according to the decisions. This method
    is the meat of the simulator, some of the logic is separated
    to other methods but the idea is as follows:

        * update fields that need updating before any 'actions' happen
        * build and then execute all 'actions' for the turn
        * update fields that need updating after all 'actions'
            eg. burn damage, weather...
        * check if someone won the game on this turn
        * update the request for new decisions from player/ai

    Note: Pseudo turns exist for when either player needs to throw out
    another pokemon due to fainting

    PRE: B.p1.choice is valid
    PRE: B.p2.choice is valid
    '''
    if B.p1.choice is None or B.p2.choice is None:
        sys.exit('BATTLE ERROR: one or more sides has invalid decision')

    from sim.turn import turn_start, turn_end, run_action, run_move,\
                            calc_damage, accuracy_check, boosts_statuses,\
                            update_move_before_running,\
                            unique_moves_after_damage, create_move, \
                            populate_action_queue, resolve_priority

    turn_start(B)

    if B.debug:
        print('---Turn ' + str(B.turn) + '---')
        print(B.p1.choice)
        print(B.p2.choice)

    # create and populate action queue
    # elements of queue are in form (priority : int, action : Action)
    q : List[Tuple[float, Action]] = []
    for player in [B.p1,B.p2]:
        for i in range(len(player.active_pokemon)):
            poke = player.active_pokemon[i]
            choice = player.choice
            move = create_move(B, poke, choice)
            populate_action_queue(q, poke, choice, move, player, B)

    # run each each action in the queue
    if B.debug:
        print(q)
        print()
    while q:
        priority, next_action = heapq.heappop(q) 
        run_action(B, next_action)
    
    if not B.pseudo_turn:
        turn_end(B)

    #check for a winner
    if not pokemon_left(B.p1):
        B.ended = True
        B.winner = 'p2'
        if B.debug:
            print('p2 won')
    if not pokemon_left(B.p2):
        B.ended = True
        B.winner = 'p1'
        if B.debug:
            print('p1 won')

    #request the next turns move
    B.pseudo_turn = False
    B.request = 'move'
    B.p1.request = 'move'
    B.p2.request = 'move'
    #B.p1.request = ['move', 'move'] if B.doubles else ['move']
    #B.p2.request = ['move', 'move'] if B.doubles else ['move']

    #check if a pokemon fainted and insert a pseudo turn
    for pokemon in get_active_pokemon(B):
        if pokemon.fainted:
            B.pseudo_turn = True
            
    if B.pseudo_turn:
        # check player 1's pokemon
        for i in range(len(B.p1.active_pokemon)):
            if B.p1.active_pokemon[i].fainted:
                B.p1.request = 'switch'
            else:
                B.p1.request = 'pass'

        # check player 2's pokemon
        for i in range(len(B.p2.active_pokemon)):
            if B.p2.active_pokemon[i].fainted:
                B.p2.request = 'switch'
            else:
                B.p2.request = 'pass'
    
    if B.debug:
        print('---End of Turn ' + str(B.turn) + '---')
    return
