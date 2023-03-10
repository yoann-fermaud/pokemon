import sys
import pygame as pg
import time, math, random, requests, io

from urllib.request import urlopen
from src.text import Text
from src.button import Button
from src.settings import *


class Move:
    def __init__(self, url):
        # call the moves API endpoint
        req = requests.get(url)
        self.json = req.json()

        self.name = self.json["name"]
        self.power = self.json["power"]
        self.type = self.json["type"]["name"]


class Pokemon(pg.sprite.Sprite):
    def __init__(self, name, level, x, y):
        pg.sprite.Sprite.__init__(self)
        # call the pokemon API endpoint
        self.screen = pg.display.set_mode(size)
        req = requests.get(f"{base_url}/pokemon/{name.lower()}")
        self.json = req.json()

        # set the pokemon's name and level
        self.name = name
        self.level = level

        # set the sprite position on the screen
        self.x = x
        self.y = y

        # number of potions left
        self.num_potions = 3

        # get the pokemon's stats from the API
        stats = self.json['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat']
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat']
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']

        # set the pokemon's types
        self.types = []
        for i in range(len(self.json['types'])):
            type = self.json['types'][i]
            self.types.append(type['type']['name'])

        # set the sprite's width
        self.size = 150

        # set the sprite to the front facing sprite
        self.set_sprite("front_default")

    def perform_attack(self, other, move):
        # display_message(f'{self.name} used {move.name}')
        self.draw_background_bottom()
        Text(self.screen, 5, 350, f"{self.name} used {move.name}!", 20,
             690, 125, "../assets/background/background_text_box.png").draw()
        # pause for 2 seconds
        time.sleep(2)
        # calculate the damage
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power

        # same type attack bonus (STAB)
        if move.type in self.types:
            damage *= 1.5

        # critical hit (6.25% chance)
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5

        # round down the damage
        damage = math.floor(damage)
        other.take_damage(damage)

    def take_damage(self, damage):
        self.current_hp -= damage
        # hp should not go below 0
        if self.current_hp < 0:
            self.current_hp = 0

    def use_potion(self):
        # check if there are potions left
        if self.num_potions > 0:

            # add 30 hp (but don't go over the max hp)
            self.current_hp += 30
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp

            # decrease the number of potions left
            self.num_potions -= 1

    def set_sprite(self, side):

        # set the pokemon's sprite
        image = self.json['sprites'][side]
        image_stream = urlopen(image).read()
        image_file = io.BytesIO(image_stream)
        self.image = pg.image.load(image_file).convert_alpha()

        # scale the image
        scale = self.size / self.image.get_width()
        new_width = self.image.get_width() * scale
        new_height = self.image.get_height() * scale
        self.image = pg.transform.scale(self.image, (new_width, new_height))

    def set_moves(self):
        self.moves = []
        # go through all moves from the api
        for i in range(len(self.json['moves'])):

            # get the move from different game versions
            versions = self.json['moves'][i]['version_group_details']
            for j in range(len(versions)):

                version = versions[j]

                # only get moves from red-blue version
                if version['version_group']['name'] != "red-blue":
                    continue

                # only get moves that can be learned from leveling up (ie. exclude TM moves)
                learn_method = version['move_learn_method']['name']
                if learn_method != "level-up":
                    continue

                # add move if pokemon level is high enough
                level_learned = version['level_learned_at']
                if self.level >= level_learned:
                    move = Move(self.json['moves'][i]['move']['url'])

                    # only include attack moves
                    if move.power is not None:
                        self.moves.append(move)

        # select up to 4 random moves
        if len(self.moves) > 4:
            self.moves = random.sample(self.moves, 4)

    def draw(self):
        sprite = self.image.copy()
        self.screen.blit(sprite, (self.x, self.y))

    def draw_background_bottom(self):
        background = pg.image.load("../assets/background/background_battle_1.png")
        background = pg.transform.scale(background, (game_width, 150))
        self.screen.blit(background, (0, 350))

    def draw_hp(self, hide, top, left):
        # display the health bar
        bar_scale = 200 // self.max_hp
        for i in range(self.max_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, 2, 10)
            pg.draw.rect(self.screen, "red", bar)

        for i in range(self.current_hp):
            bar = (self.hp_x + bar_scale * i, self.hp_y, 2, 10)
            # bar = (40, 20, 200, 20)
            pg.draw.rect(self.screen, "green", bar)

        # display "HP" text
        if not hide:
            font = pg.font.Font(pg.font.get_default_font(), 18)
            text = font.render(f'{self.current_hp} / {self.max_hp}', True, "black")
            text_rect = text.get_rect()
            text_rect.x = top
            text_rect.y = left
            self.screen.blit(text, text_rect)

    def draw_rect(self):
        return pg.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())


class Menu:
    def __init__(self):
        # create the starter pokemons
        self.screen = pg.display.set_mode((1080, 720))
        self.level = 30

        self.bulbasaur = Pokemon("Bulbasaur", self.level, 25, 150)
        self.charmander = Pokemon("Charmander", self.level, 175, 150)
        self.squirtle = Pokemon("Squirtle", self.level, 325, 150)
        self.eevee = Pokemon("Eevee", self.level, 475, 150)
        self.pokemons = [self.bulbasaur, self.charmander, self.squirtle, self.eevee]

        # the player's and rival's selected pokemon
        self.game_status = "select pokemon"
        self.player_pokemon = None
        self.rival_pokemon = None
        self.message_01 = None
        self.message_02 = None

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            # detect mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_events = event.pos
                # for selecting a pokemon
                if self.game_status == "select pokemon":
                    # check which pokemon was clicked on
                    for i in range(len(self.pokemons)):
                        if self.pokemons[i].draw_rect().collidepoint(mouse_events):
                            # assign the player's and rival's pokemon
                            self.player_pokemon = self.pokemons[i]
                            self.rival_pokemon = self.pokemons[(i + 1) % len(self.pokemons)]

                            # lower the rival pokemon's level to make the battle easier
                            self.rival_pokemon.level = int(self.rival_pokemon.level * .75)

                            # set the coordinates of the hp bars
                            self.player_pokemon.hp_x = 542
                            self.player_pokemon.hp_y = 274
                            self.rival_pokemon.hp_x = 152
                            self.rival_pokemon.hp_y = 87
                            self.game_status = "prebattle"
                # for selecting fight or use potion
                elif self.game_status == "player turn":
                    # check if fight button was clicked
                    if self.fight_button.checkForInput(mouse_events):
                        self.game_status = "player move"

                    # check if potion button was clicked
                    if self.potion_button.checkForInput(mouse_events):

                        # force to attack if there are no more potions
                        if self.player_pokemon.num_potions == 0:
                            Text(self.screen, 5, 350, "No more potions left", 20,
                                 690, 125, "../assets/background_text_box.png").draw()
                            time.sleep(1)
                            self.game_status = "player move"
                        else:
                            self.player_pokemon.use_potion()
                            Text(self.screen, 5, 350, f"{self.player_pokemon.name} used potion", 20,
                                 690, 125, "../assets/background_text_box.png").draw()
                            time.sleep(1)
                            self.game_status = "rival turn"

                elif self.game_status == "player move":
                    # check which move button was clicked
                    for i in range(len(self.move_buttons)):
                        button = self.move_buttons[i]

                        if button.checkForInput(mouse_events):
                            move = self.player_pokemon.moves[i]
                            self.player_pokemon.perform_attack(self.rival_pokemon, move)

                            # check if the rival's pokemon fainted
                            if self.rival_pokemon.current_hp == 0:
                                self.game_status = "fainted"
                            else:
                                self.game_status = "rival turn"

        pg.display.update()

    def draw(self):
        if self.game_status == "select pokemon":
            self.screen.fill("white")
            self.bulbasaur.draw()
            self.charmander.draw()
            self.eevee.draw()
            self.squirtle.draw()
            # draw box around pokemon the mouse is pointing to
            mouse_cursor = pg.mouse.get_pos()
            for pokemon in self.pokemons:
                if pokemon.draw_rect().collidepoint(mouse_cursor):
                    pg.draw.rect(self.screen, "black", pokemon.draw_rect(), 2)
            pg.display.update()
        # get moves from the API and reposition the pokemons

    def draw_pokemon_hp(self):
        # draw the hp bars
        self.hp_right = pg.image.load("../assets/pictures/hp_right.png")
        self.hp_right = pg.transform.scale(self.hp_right, (355, 107))
        self.screen.blit(self.hp_right, (345, 220))
        self.player_pokemon.draw_hp(False, 590, 295)
        Text(self.screen, 400, 220, f"{self.player_pokemon.name}", 25, 40, 40, None).draw()

        self.hp_left = pg.image.load("../assets/pictures/hp_left.png")
        self.hp_left = pg.transform.scale(self.hp_left, (370, 90))
        self.screen.blit(self.hp_left, (0, 30))
        self.rival_pokemon.draw_hp(True, 0, 0)
        Text(self.screen, 15, 30, f"{self.rival_pokemon.name}", 25, 40, 40, None).draw()

    def draw_background_bottom(self):
        background = pg.image.load("../assets/background/background_battle_1.png")
        background = pg.transform.scale(background, (game_width, 150))
        self.screen.blit(background, (0, 350))

    def draw_prebattle(self):
        if self.game_status == "prebattle":
            # draw the selected pokemon
            self.screen.fill("white")
            self.player_pokemon.draw()
            pg.display.update()

            self.player_pokemon.set_moves()
            self.rival_pokemon.set_moves()

            # reposition the pokemons
            self.player_pokemon.x = 20
            self.player_pokemon.y = 100
            self.rival_pokemon.x = 385  # 250
            self.rival_pokemon.y = 22

            # resize the sprites
            self.player_pokemon.size = 420
            self.rival_pokemon.size = 300
            self.player_pokemon.set_sprite("back_default")
            self.rival_pokemon.set_sprite("front_default")

            self.game_status = "start battle"

    def draw_start_battle(self):
        # start battle animation
        if self.game_status == "start battle":
            # rival sends out their pokemon
            self.screen.fill("white")
            self.background = pg.image.load("../assets/background/background_battle_0.png")
            self.background = pg.transform.scale(self.background, (game_width, 350))
            self.screen.blit(self.background, (0, 0))
            self.draw_background_bottom()

            incr = 0
            while incr < 255:
                self.rival_pokemon.draw()
                Text(self.screen, 5, 350, f"Rival sent out {self.rival_pokemon.name}!", 20,
                     690, 125, "../assets/background/background_text_box.png").draw()
                incr += 1
                pg.display.update()

            # pause for 1 second
            time.sleep(1)

            # player sends out their pokemon
            incr = 0
            while incr < 255:
                self.player_pokemon.draw()

                Text(self.screen, 5, 350, f"Go {self.player_pokemon.name}!", 20,
                     690, 125, "../assets/background/background_text_box.png").draw()
                incr += 1
                pg.display.update()

            # draw the hp bars
            self.draw_pokemon_hp()

            # determine who goes first
            if self.rival_pokemon.speed > self.player_pokemon.speed:
                self.game_status = "rival turn"
            else:
                self.game_status = "player turn"

            pg.display.update()

    def draw_player_turn(self):
        # display the fight and use potion buttons
        if self.game_status == "player turn":
            mouse_player_turn = pg.mouse.get_pos()

            self.draw_pokemon_hp()
            self.draw_background_bottom()

            # create the fight and use potion buttons
            self.fight_button = Button(pg.image.load("../assets/background/background_text_box.png"), 345, 125, ((game_width / 2) - 175, 412),
                                       "FIGHT", 40, "black", "grey")
            self.potion_button = Button(pg.image.load("../assets/background/background_text_box.png"), 345, 125, ((game_width / 2) + 175, 412),
                                        f"POTION ({self.player_pokemon.num_potions})", 40, "black", "grey")

            for button in [self.fight_button, self.potion_button]:
                button.changeColor(mouse_player_turn)
                button.update(self.screen)

            pg.display.update()

    def draw_player_move(self):
        if self.game_status == "player move":
            mouse_player_move = pg.mouse.get_pos()

            self.draw_pokemon_hp()
            self.draw_background_bottom()

            # create a button for each move
            self.move_buttons = []
            for i in range(len(self.player_pokemon.moves)):
                move = self.player_pokemon.moves[i]
                button_width = 345
                button_height = 72
                left = (game_width / 2 - 175) + i % 2 * (button_width + 4)
                top = 386 + i // 2 * (button_height + 2)

                button = Button(pg.image.load("../assets/background/background_text_box.png"), button_width, button_height,
                                (left, top), move.name.capitalize(), 30, "black", "grey")

                button.changeColor(mouse_player_move)
                button.update(self.screen)
                self.move_buttons.append(button)

            pg.display.update()

    def draw_rival_turn(self):
        # rival selects a random move to attack with
        if self.game_status == "rival turn":

            self.draw_pokemon_hp()
            self.draw_background_bottom()

            time.sleep(1)

            # select a random move
            move = random.choice(self.rival_pokemon.moves)
            self.rival_pokemon.perform_attack(self.player_pokemon, move)

            # check if the player's pokemon fainted
            if self.player_pokemon.current_hp == 0:
                self.game_status = "fainted"
            else:
                self.game_status = "player turn"

            pg.display.update()

    def run(self):
        while True:
            self.events()
            self.draw()
            self.draw_prebattle()
            self.draw_start_battle()
            self.draw_player_turn()
            self.draw_player_move()
            self.draw_rival_turn()


menu = Menu()
menu.run()
