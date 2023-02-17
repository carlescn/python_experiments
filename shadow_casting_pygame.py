"""
Implementation of 2D shadow casting based on line-line intersections
"""

import pygame as pg
import numpy as np


SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TARGET_FPS    = 60
TIMER_MS      = 100


class Ray():
    def __init__(self, origin, angle):
        self.color = pg.Color("yellow")
        self.length = SCREEN_WIDTH #TODO: change to intersection with edge of screen?
        self.theta = np.deg2rad(angle)
        self.origin = None
        self.end = None
        self.update_position(origin)
        self.intersection = None

    def update_position(self, origin):
        self.origin = origin
        self.end = (self.origin[0] - self.length * np.cos(self.theta),
                    self.origin[1] - self.length * np.sin(self.theta))

    def compute_intersection(self, line):
        #pylint:disable=invalid-name # (single letter x, y, t, u)
        x_1, y_1 = self.origin
        x_2, y_2 = self.end
        x_3, y_3 = line.start
        x_4, y_4 = line.end

        # If lines are parallel (no intersection), denominator is zero
        denominator = (x_1 - x_2)*(y_3 - y_4) - (y_1 - y_2)*(x_3 - x_4)
        if denominator == 0:
            return None
        t = ((x_1 - x_3)*(y_3 - y_4) - (y_1- y_3)*(x_3 - x_4)) / denominator
        u = ((x_1 - x_3)*(y_1 - y_2) - (y_1- y_3)*(x_1 - x_2)) / denominator

        if 0 < u < 1 and 0 < t:
            x = x_1 + t * (x_2 - x_1)
            y = y_1 + t * (y_2 - y_1)
            return {"x": x, "y": y, "t": t}
        else:
            return None

    def get_first_intersection(self, lines):
        #pylint:disable=invalid-name # (single letter x, y, t, u)
        t = np.Infinity
        intersection = None
        for line in lines:
            result = self.compute_intersection(line)
            if result is not None and result["t"] < t:
                t = result["t"]
                intersection = (result["x"],result["y"])
        #TODO: return intersection and remove all this:
        if intersection is None:
            self.intersection = None
            self.color = pg.Color("yellow")
        else:
            self.intersection = intersection
            self.end = intersection
            self.color = pg.Color("red")

    def draw(self, surface):
        pg.draw.aaline(surface, self.color, self.origin, self.end)
        if self.intersection is not None:
            pg.draw.circle(surface, self.color, self.intersection, 5)


class ShadowCaster():
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color
        self.rays = [Ray(self.position, 0),]

    def update_position(self, position):
        self.position = position
        for ray in self.rays:
            #TODO: autorotation is only for testing. Remove this line eventually.
            ray.theta = (ray.theta + np.pi / 180) % (2 * np.pi)
            ray.update_position(position)

    def get_intersections(self, lines):
        for ray in self.rays:
            ray.get_first_intersection(lines)

    def draw(self, surface):
        for ray in self.rays:
            ray.draw(surface)
        pg.draw.circle(surface, self.color, self.position, self.size)


class Line(): # TODO: change line for polygon
    def __init__(self, color):
        self.start = self.get_random_coord()
        self.end   = self.get_random_coord()
        self.color = color

    def draw(self, surface):
        pg.draw.aaline(surface, self.color, self.start, self.end)

    #TODO: random line positions only for testing. Remove eventually.
    def get_random_coord(self):
        return (
        np.random.randint(0, SCREEN_WIDTH),
            np.random.randint(0, SCREEN_HEIGHT)
        )


class Game():
    def __init__(self):
        self.cursor = ShadowCaster(pg.mouse.get_pos(), 8, pg.Color("white"))
        self.lines  = [Line(pg.Color("white")) for _ in range(3)]

    def draw(self, surface):
        for line in self.lines:
            line.draw(surface)
        self.cursor.draw(surface)

    def update(self):
        self.cursor.update_position(pg.mouse.get_pos())
        self.cursor.get_intersections(self.lines)


class App():
    def __init__(self):
        pg.init()
        pg.display.set_caption("Pygame template")
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.mouse.set_visible(False)
        self.font   = pg.font.SysFont(None, 24)

        self.clock  = pg.time.Clock()
        self.timer  = pg.USEREVENT
        pg.time.set_timer(self.timer, TIMER_MS)

        self.game = Game()
        self.main_loop()

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                # if event.type == pg.KEYDOWN:
                #     pass
                # if event.type == pg.MOUSEBUTTONDOWN:
                #     pass
                # if event.type == self.timer:
                #     pass

            self.game.update()
            self.screen.fill(pg.Color("black"))
            self.game.draw(self.screen)
            self.print_fps()
            pg.display.flip()
            self.clock.tick(TARGET_FPS)

    def quit(self):
        pg.quit()

    def print_fps(self):
        text = f"FPS: {int(self.clock.get_fps())}"
        rendered_text = self.font.render(text, True, pg.Color("white"))
        self.screen.blit(rendered_text, (10, 10))


if __name__=="__main__":
    App()
    