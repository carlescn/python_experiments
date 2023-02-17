"""
This is a template for a simple App class that initializes Pygame
and has a basic game loop.
"""

import pygame as pg
# import numpy as np

SCREEN_TITLE  = "Pygame template"
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TARGET_FPS    = 60
TIMER_MS      = 100


class App():
    def __init__(self):
        pg.init()
        pg.display.set_caption(SCREEN_TITLE)
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # self.font   = pg.font.SysFont(None, 24)
        self.clock  = pg.time.Clock()
        self.timer  = pg.USEREVENT
        pg.time.set_timer(self.timer, TIMER_MS)

        self.main_loop()

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYDOWN:
                    # Do things with keyboard input
                    pass
                if event.type == pg.MOUSEBUTTONDOWN:
                    # Do things with mouse button input
                    pass
                if event.type == self.timer:
                    # Do things based on timer
                    pass

            pg.display.flip()
            self.clock.tick(TARGET_FPS)

    def quit(self):
        pg.quit()


if __name__=="__main__":
    App()
    