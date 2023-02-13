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
ROTATE_90 = np.deg2rad(90)


class Plant():
    def __init__(self, angle, length, width, leaves_size):
        self.array = "X"
        self.rules = {
            "X": "F-[[X]+X]+F[+FX]-X",
            "F": "FF"
        }
        self.angle = np.deg2rad(angle)
        self.length = length
        self.width = width
        self.leaves_size = leaves_size
        self.stem_color  = pygame.Color("burlywood4")
        self.leave_color = pygame.Color("springgreen4")
        self.position = (SCREEN_WIDTH / 3, SCREEN_HEIGHT)

    def grow(self):
        new_array = ""
        for letter in self.array:
            new_array += self.rules[letter] if letter in self.rules else letter
        self.array = str(new_array)

    def draw(self):
        nodes = [{
            "x": self.position[0],
            "y": self.position[1],
            "angle": self.angle,
        },]
        for letter in self.array:
            node = nodes[-1]
            match letter:
                case "F":
                    theta = node["angle"] + ROTATE_90
                    line_start = (node["x"], node["y"])
                    line_end = (node["x"] - self.length * np.cos(theta) + np.random.normal(0,0.03),
                                node["y"] - self.length * np.sin(theta) + np.random.normal(0,0.03))
                    pygame.draw.line(SCREEN, self.stem_color, line_start, line_end, self.width)
                    node["x"], node["y"] = line_end

                case "+":
                    node["angle"] += self.angle

                case "-":
                    node["angle"] -= self.angle

                case "[":
                    nodes.append(node.copy())

                case "]":
                    position = (node["x"], node["y"])
                    pygame.draw.circle(SCREEN, self.leave_color, position, self.leaves_size)
                    nodes.pop(-1)


def quit_game():
    pygame.quit()
    sys.exit()

def print_fps():
    text = FONT.render(f"FPS: {int(CLOCK.get_fps())}", False, pygame.Color("black"))
    SCREEN.blit(text, (0,0))

async def main():
    """ Handle the game loop. """
    plant = Plant(25, 3, 3, 3)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit_game()
                else:
                    plant.grow()
            if event.type == pygame.MOUSEBUTTONDOWN:
                plant.grow()
            if event.type == TIMER:
                SCREEN.fill(pygame.Color("cadetblue1"))
                plant.draw()

        print_fps()
        pygame.display.flip()
        CLOCK.tick(60)
        await asyncio.sleep(0)


if __name__=="__main__":
    pygame.init()
    pygame.display.set_caption("Snake")
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    FONT   = pygame.font.SysFont(None, 32)
    CLOCK  = pygame.time.Clock()
    TIMER  = pygame.USEREVENT
    pygame.time.set_timer(TIMER, 100)

    asyncio.run(main())
    