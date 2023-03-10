import pygame as pg


class Text:
    def __init__(self, screen, top, left, text, font_size, width, height, background):
        pg.init()
        self.screen = screen
        self.top, self.left = top, left
        self.text = text
        self.width, self.height = width, height
        self.background = background

        self.font = pg.font.Font(pg.font.get_default_font(), font_size)
        self.text = self.font.render(self.text, True, "black")
        self.textRect = pg.Rect(self.top, self.left, self.width, self.height)

        # self.background = pg.image.load("../assets/background_text_box.png")
        if self.background is not None:
            self.background = pg.image.load(background)
            self.background = pg.transform.scale(self.background, (width, height))

    def draw(self):
        if self.background is not None:
            self.screen.blit(self.background, self.textRect)
        self.screen.blit(self.text, (self.textRect[0] + 25, self.textRect[1] + 20))

        pg.display.update()


