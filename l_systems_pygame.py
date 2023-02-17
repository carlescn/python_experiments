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
        pg.display.set_caption("L-Systems experiment")
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font   = pg.font.SysFont(None, 24)
        self.clock  = pg.time.Clock()
        self.timer  = pg.USEREVENT
        pg.time.set_timer(self.timer, 100)

        self.main()

    def main(self):
        plants = self.get_plants()
        iteration = 0

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        self.quit()
                    else:
                        self.grow_plants(plants)
                        iteration += 1
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.grow_plants(plants)
                if event.type == self.timer:
                    self.screen.fill(pg.Color("cadetblue1"))
                    self.draw_plants(plants)
                    self.print_info(iteration, plants)

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
        plants = [Plant(axiom, rules, position, 25, 2, 3, stem_color, 4, leaves_color),]
        # Define more plants here and append to plants
        return plants

    def grow_plants(self, plants):
        for plant in plants:
            plant.grow()

    def draw_plants(self, plants):
        for plant in plants:
            plant.draw(self.screen)

    def get_numbers(self, plants):
        sentences = lines = leaves = 0
        for plant in plants:
            sentences += len(plant.sentence)
            if plant.lines is None:
                continue
            for line in plant.lines:
                lines  += len(line)
                leaves += 1
        return (sentences, lines, leaves)

    def print_info(self, iteration, plants):
        sentence_length, number_lines, number_leaves = self.get_numbers(plants)
        texts = []
        texts.append(f"FPS: {int(self.clock.get_fps())}")
        texts.append(f"Iteration: {iteration}")
        texts.append(f"Num. lines: {number_lines:,}")
        texts.append(f"Num. leaves: {number_leaves:,}")
        texts.append(f"Len. sentences: {sentence_length:,}")
        for i, text in enumerate(texts):
            rendered_text = self.font.render(text, True, pg.Color("black"))
            self.screen.blit(rendered_text, (10, 10 + 20 * i))


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
        self.lines = None

    def grow(self):
        new_sentence = ""
        for letter in self.sentence:
            new_sentence += self.rules[letter] if letter in self.rules else letter
        self.sentence = str(new_sentence)
        self.update_lines()

    def update_lines(self):
        angle = self.angle
        line  = [self.position,]
        self.lines = []
        nodes = []
        for i, letter in enumerate(self.sentence):
            match letter:
                case "F":
                    # rotate 90 degrees so it grows vertically
                    theta = angle + ROTATE_90
                    line_end = (line[-1][0] - self.length * np.cos(theta),
                                line[-1][1] - self.length * np.sin(theta))
                    if i > 0 and self.sentence[i-1] == "F":
                        line[-1] = line_end
                    else:
                        line.append(line_end)
                case "+":
                    angle += self.angle
                case "-":
                    angle -= self.angle
                case "[":
                    nodes.append((line[-1], angle))
                case "]":
                    if len(line) > 1:
                        self.lines.append(line)
                    line, angle = nodes.pop(-1)
                    line = [line,]

    def draw(self, surface):
        if self.lines is not None:
            for line in self.lines:
                pg.draw.lines(surface, self.stem_color, False, line, self.stem_width)
            for line in self.lines[::2]:  # comment to draw all leaves, overlapped with the stems
                leave_pos = line[-1] + np.random.normal(0, 0.5, 2)
                pg.draw.circle(surface, self.leaves_color, leave_pos, self.leaves_size)


if __name__=="__main__":
    App()
    