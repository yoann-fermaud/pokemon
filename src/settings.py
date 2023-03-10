import pygame as pg


pg.init()

# create the game window
game_width = 700
game_height = 500
size = (game_width, game_height)
pg.display.set_caption("Pokemon Battle")

# base url of the API
base_url = 'https://pokeapi.co/api/v2'
