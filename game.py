import sys
import pygame as pg
from src.pokemon import Menu
from src.button import Button
from src.settings import *


class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("POKEMON")
        self.screen = pg.display.set_mode((game_width, game_height))

        self.menu = Menu()

        self.play = Button(pg.image.load("assets/button_pictures/button_rect.png"), 300, 100,
                           ((game_width / 2), 100), "PLAY", 40, "white", "grey")
        self.pokedex = Button(pg.image.load("assets/button_pictures/button_rect.png"), 345, 115,
                              ((game_width / 2), 250), "POKEDEX", 40, "white", "grey")
        self.quit = Button(pg.image.load("assets/button_pictures/button_rect.png"), 300, 90,
                           ((game_width / 2), 400), "QUIT", 40, "white", "grey")

    def events(self):
        self.mouse_event = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if self.play.checkForInput(self.mouse_event):
                    self.menu.run()

                elif self.quit.checkForInput(self.mouse_event):
                    pg.quit()
                    sys.exit()

    def draw(self):
        self.background = pg.image.load("assets/background/background_main_menu_1.png")
        self.background = pg.transform.scale(self.background, (game_width, game_height))
        self.screen.blit(self.background, (0, 0))

    def update(self):
        for button in [self.play, self.pokedex, self.quit]:
            button.changeColor(self.mouse_event)
            button.update(self.screen)

        pg.display.update()

    def run(self):
        while True:
            self.events()
            self.draw()
            self.update()


if __name__ == '__main__':
    game = Game()
    game.run()
