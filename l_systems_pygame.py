"""
Implementation of L-systems to draw realistic looking plants
(see: https://en.wikipedia.org/wiki/L-system)
"""

import pygame as pg
import numpy as np


SCREEN_WIDTH  = 1080
SCREEN_HEIGHT = 720
ROTATE_90 = np.deg2rad(90) # Compute it only one time


class App():
    def __init__(self):
        pg.init()
        pg.display.set_caption("Snake")
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font   = pg.font.SysFont(None, 32)
        self.clock  = pg.time.Clock()
        self.timer  = pg.USEREVENT
        pg.time.set_timer(self.timer, 100)

        self.main()

    def main(self):
        plants = self.get_plants()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.quit()
                    else:
                        self.grow_plants(plants)
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.grow_plants(plants)
                if event.type == self.timer:
                    self.screen.fill(pg.Color("cadetblue1"))
                    self.draw_plants(plants)

            self.print_fps()
            pg.display.flip()
            self.clock.tick(60)

    def quit(self):
        pg.quit()

    def get_plants(self):
        # First plant
        axiom = "X"
        rules = {
            "X": "F-[[X]+X]+F[+FX]-X",
            "F": "FF"
        }
        position = (self.screen.get_width() / 3, self.screen.get_height())
        stem_color = pg.Color("burlywood4")
        leaves_color = pg.Color("springgreen4")
        plants = [Plant(axiom, rules, position, 25, 4, 3, stem_color, 4, leaves_color),]
        # Define more plants here and append to plants
        return plants

    def grow_plants(self, plants):
        for plant in plants:
            plant.grow()

    def draw_plants(self, plants):
        for plant in plants:
            plant.draw(self.screen)

    def print_fps(self):
        text = self.font.render(f"FPS: {int(self.clock.get_fps())}", False, pg.Color("black"))
        self.screen.blit(text, (0,0))


class Plant():
    def __init__(
        self, axiom: str, rules: dict,
        position: tuple, angle_deg: float, length: float,
        stem_width: int, stem_color: pg.Color,
        leaves_size: int, leaves_color: pg.Color
    ):
        self.sentence = axiom
        self.rules    = rules
        self.position = position
        self.angle    = np.deg2rad(angle_deg)
        self.length   = length
        self.stem_width   = stem_width
        self.stem_color   = stem_color
        self.leaves_size  = leaves_size
        self.leaves_color = leaves_color

    def grow(self):
        new_sentence = ""
        for letter in self.sentence:
            new_sentence += self.rules[letter] if letter in self.rules else letter
        self.sentence = str(new_sentence)

    def draw(self, surface):
        nodes = [{
            "x": self.position[0],
            "y": self.position[1],
            "angle": self.angle,
        },]
        for letter in self.sentence:
            node = nodes[-1]
            match letter:
                case "F":
                    # rotate 90 degrees so it grows vertically
                    theta = node["angle"] + ROTATE_90
                    line_start = (node["x"], node["y"])
                    line_end = (node["x"] - self.length * np.cos(theta) + np.random.normal(0,0.03),
                                node["y"] - self.length * np.sin(theta) + np.random.normal(0,0.03))
                    pg.draw.line(surface, self.stem_color, line_start, line_end, self.stem_width)
                    node["x"], node["y"] = line_end

                case "+":
                    node["angle"] += self.angle

                case "-":
                    node["angle"] -= self.angle

                case "[":
                    nodes.append(node.copy())

                case "]":
                    position = (node["x"], node["y"])
                    pg.draw.circle(surface, self.leaves_color, position, self.leaves_size)
                    nodes.pop(-1)


if __name__=="__main__":
    App()
    