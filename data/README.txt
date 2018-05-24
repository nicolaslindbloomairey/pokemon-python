here is the set up for the moves.json

id : {
    move number
    accuracy: true if it doesnt have an accuracy check, otherwise 30 <= n <= 100
    category: Physical, Special, or Status
    desc: what the moves should do
    id: name but alphanumeric lowercase
    pp: how many power points the move has
    priority: what priority tier, -7 <= n <= 5
    flags: flags the game uses for abilities and whatnot
           not sure why these flags are grouped
    type: the pokemon type the move is, Fire, Water, Grass, etc.
    terrain: None or the terrain type that is started by this move
    weather: None or the weather type that is started by this move
    ignore_accuracy: None or True, this might be useless because of the accuracy value
    drain: decimal, how much health you heal back after attacking, eg 0.5 = half the damage you do is healed back to you
    heal: decimal, how much health you heal in relation to your maxhp
    recoil: the type of recoil and how much and when to trigger it
    target_type: normal, 
    base_power: for use in the damage calc
}
