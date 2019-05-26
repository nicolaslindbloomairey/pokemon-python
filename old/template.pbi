format single
rng some type of random seed
player p1 [name]
team for player p1
player p2 [name]
packedteam
p1 CHOICE
p2 CHOICE

as many choices as you want until the game is over

CHOICE in singles = default,
                    pass, 
                    move slot, 
                    move slot mega, 
                    move slot zmove, 
                    switch slot

slot is 1-indexed
slot for move is 1-4 inclusive
slot for switch depends on how many pokemon you have



packedteam format:
name|species|item|ability|moves|nature|evs|gender|ivs|shiny|level|happiness]

moves, evs and ivs are comma separated
hp
atk
def
spa
spd
spe
