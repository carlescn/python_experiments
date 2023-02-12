"""
Implementation of L-systems to draw realistic looking plants
(see: https://en.wikipedia.org/wiki/L-system)
"""

import sys
import asyncio

import pygame
import numpy as np


SCREEN_WIDTH  = 1080
SCREEN_HEIGHT = 720


class Plant():
    def __init__(self):
        self.array = "X"
        self.rules = {
            "X": "F-[[X]+X]+F[+FX]-X",
            "F": "FF"
        }
        self.angle  = 25
        self.length = 5
        self.width = 3
        self.stem_color  = pygame.Color("burlywood4")
        self.leave_color = pygame.Color("springgreen4")
        self.position = (SCREEN_WIDTH / 3, SCREEN_HEIGHT)

    def grow(self):
        new_array = ""
        for letter in self.array:
            new_array += self.rules[letter] if letter in self.rules else letter
        self.array = str(new_array)

    def draw(self):
        xys    = [self.position,]
        angles = [self.angle,]
        for letter in self.array:
            match letter:
                case "F":
                    # pylint:disable=invalid-name  # single letter x, y
                    x = xys[-1][0] \
                        - self.length * np.cos(np.deg2rad(angles[-1] + 90)) \
                        + np.random.normal(0,0.03)
                    y = xys[-1][1] \
                        - self.length * np.sin(np.deg2rad(angles[-1] + 90)) \
                        + np.random.normal(0,0.08)
                    line_end = (x, y)
                    pygame.draw.line(SCREEN, self.stem_color, xys[-1], line_end, self.width)
                    xys[-1] = line_end

                case "+":
                    angles[-1] += self.angle

                case "-":
                    angles[-1] -= self.angle

                case "[":
                    xys    += [xys[-1],]
                    angles += [angles[-1],]

                case "]":
                    pygame.draw.circle(SCREEN, self.leave_color, xys[-1], 4)
                    xys.pop(-1)
                    angles.pop(-1)


async def main():
    """ Handle the game loop. """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                plant.grow()
            if event.type == pygame.MOUSEBUTTONDOWN:
                plant.grow()
            if event.type == TIMER:
                SCREEN.fill(pygame.Color("cadetblue1"))
                plant.draw()

        pygame.display.flip()
        await asyncio.sleep(0)


if __name__=="__main__":
    pygame.init()

    pygame.display.set_caption("Snake")
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    TIMER = pygame.USEREVENT
    pygame.time.set_timer(TIMER, 100)

    plant = Plant()

    asyncio.run(main())
    