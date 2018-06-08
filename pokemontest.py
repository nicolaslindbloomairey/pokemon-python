import sys, pygame
import math
from sim.battle import Battle
from data import dex

pygame.init()

battle = Battle(doubles=False)
battle.join()
battle.join()

size = width, height = 600, 400

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# font
font = pygame.font.SysFont('Arial', 12)

pokemon_images = [None]*808
for i in range(1, 808):
    pokemon_images[i] = pygame.image.load("img/" + str(i) + ".png")

screen = pygame.display.set_mode(size)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            for i in range(11):
                if 400 < event.pos[0] < 400+150 and 20+(30*i) < event.pos[1] < 40+(30*i):
                    # move i is selected
                    battle.sides[1].default_decide()
                    if i == len(battle.sides[0].active_pokemon[0].moves):
                        battle.choose(0, dex.Decision('pass', 0))
                    elif i > len(battle.sides[0].active_pokemon[0].moves):
                        battle.choose(0, dex.Decision('switch', i-(len(battle.sides[0].active_pokemon[0].moves)+1)))
                    else:
                        battle.choose(0, dex.Decision('move', i))
                    battle.do_turn()

    screen.fill(white)

    foe_num = dex.pokedex[battle.sides[1].active_pokemon[0].id].num
    foe = pokemon_images[foe_num]
    user_num = dex.pokedex[battle.sides[0].active_pokemon[0].id].num
    user = pokemon_images[user_num]

    mouse = pygame.mouse.get_pos()
    for i in range(len(battle.sides[0].active_pokemon[0].moves)+ 7):
        if 400 < mouse[0] < 400+150 and 20+(30*i) < mouse[1] < 40+(30*i):
            pygame.draw.rect(screen, red, (400, 20+(30*i), 150, 20))
        pygame.draw.rect(screen, black, (400, 20+(30*i), 150, 20), 1)
        if i == len(battle.sides[0].active_pokemon[0].moves):
            screen.blit(font.render('pass', False, black), (410, 25+(30*i)))
        elif i > len(battle.sides[0].active_pokemon[0].moves):
            screen.blit(font.render('switch to ' + str(battle.sides[0].pokemon[i-(len(battle.sides[0].active_pokemon[0].moves)+1)].name) + (' (fnt)' if battle.sides[0].pokemon[i-(len(battle.sides[0].active_pokemon[0].moves)+1)].fainted else ''), False, black), (410, 25+(30*i)))
        else:
            screen.blit(font.render(battle.sides[0].active_pokemon[0].moves[i], False, black), (410, 25+(30*i)))

    # Draw the pokmeon
    screen.blit(foe, (200, 30))
    screen.blit(user, (30, 200))

    # HP amount text render
    screen.blit(font.render("HP: " + str(battle.sides[0].active_pokemon[0].hp) + " / " + str(battle.sides[0].active_pokemon[0].maxhp), False, black), (30, 185))
    screen.blit(font.render("HP: " + str(battle.sides[1].active_pokemon[0].hp) + " / " + str(battle.sides[1].active_pokemon[0].maxhp), False, black), (200, 15))

    # HP bar
    hppercent0 = math.floor(100 * (battle.sides[0].active_pokemon[0].hp / battle.sides[0].active_pokemon[0].maxhp))
    hppercent1 = math.floor(100 * (battle.sides[1].active_pokemon[0].hp / battle.sides[1].active_pokemon[0].maxhp))
    pygame.draw.rect(screen, red, (200, 30, 100, 10))
    pygame.draw.rect(screen, green, (200, 30, hppercent1, 10))
    pygame.draw.rect(screen, red, (30, 200, 100, 10))
    pygame.draw.rect(screen, green, (30, 200, hppercent0, 10))


    # draw the frame
    pygame.display.flip()
    pygame.time.wait(15)
