"""
Implementation of 2D shadow casting based on line-line intersections
"""

import pygame as pg
import numpy as np


SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
TARGET_FPS    = 60
TIMER_MS      = 100

SCREEN_TL = (0, 0)
SCREEN_TR = (SCREEN_WIDTH, 0)
SCREEN_BL = (0, SCREEN_HEIGHT)
SCREEN_BR = (SCREEN_WIDTH, SCREEN_HEIGHT)

SCREEN_CORNERS = (SCREEN_TL, SCREEN_TR, SCREEN_BL, SCREEN_BR)
SCREEN_EDGES = (
    (SCREEN_TL, SCREEN_TR),
    (SCREEN_TR, SCREEN_BR),
    (SCREEN_BR, SCREEN_BL),
    (SCREEN_BL, SCREEN_TL),
)


class Ray():
    def __init__(self, origin, angle, degrees = False):
        self.color = pg.Color("yellow")
        self.length = SCREEN_WIDTH #TODO: change to intersection with edge of screen?
        self.theta = np.deg2rad(angle) if degrees else angle
        self.origin = None
        self.end = None
        self.update_position(origin)

    def update_position(self, origin):
        self.origin = origin
        self.end = (self.origin[0] - self.length * np.cos(self.theta),
                    self.origin[1] - self.length * np.sin(self.theta))

    def compute_ray_section_intersection(self, line_start, line_end):
        """Compute intersection between ray (self) and passed line section."""
        #pylint:disable=invalid-name # (single letter x, y, t, u)
        x_1, y_1 = self.origin
        x_2, y_2 = self.end
        x_3, y_3 = line_start
        x_4, y_4 = line_end

        # If lines are parallel (no intersection), denominator is zero
        denominator = (x_1 - x_2)*(y_3 - y_4) - (y_1 - y_2)*(x_3 - x_4)
        if denominator == 0:
            raise ZeroDivisionError("No intersection")

        t = ((x_1 - x_3) * (y_3 - y_4) - (y_1 - y_3) * (x_3 - x_4)) / denominator
        u = ((x_1 - x_3) * (y_1 - y_2) - (y_1 - y_3) * (x_1 - x_2)) / denominator

        resolution = 1e-10
        if line_start in SCREEN_CORNERS or line_end in SCREEN_CORNERS:
            resolution = -1 * resolution
        if not 0 + resolution < u < 1 - resolution:
            raise ValueError("Intersection outside section")
        if t < 0:
            raise ValueError("Intersection in opposite direction of ray")

        x = x_1 + t * (x_2 - x_1)
        y = y_1 + t * (y_2 - y_1)

        return x, y, t

    def get_closest_intersection(self, lines):
        #pylint:disable=invalid-name # (single letter x, y)
        closest = np.Infinity
        intersection = None
        for line_start, line_end in lines:
            try:
                x, y, distance = self.compute_ray_section_intersection(line_start, line_end)
                if distance < closest:
                    closest = distance
                    intersection = (x, y)
            except ValueError:
                # Intersection outside ray / section
                pass
            except ZeroDivisionError:
                # No intersection
                pass
        return intersection

    def draw(self, surface):
        pg.draw.aaline(surface, self.color, self.origin, self.end)


class ShadowCaster():
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color
        self.rays = []

    def update_position(self, position):
        self.position = position

    def cast_rays(self, points):
        points = set(points)
        x, y = self.position
        angles = [np.arctan2(y - point[1], x - point[0]) for point in points]
        angles.sort()
        self.rays = [Ray(self.position, angle) for angle in angles]

    def get_intersections(self, lines):
        for ray in self.rays:
            intersection = ray.get_closest_intersection(lines)
            # TODO: color change is only for testing. Remove all this.
            if intersection is not None:
                ray.end = intersection
                ray.color = pg.Color("red")
            else:
                ray.color = pg.Color("yellow")

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

        lines = [(line.start, line.end) for line in self.lines]
        lines += SCREEN_EDGES
        points = [point for line in lines for point in line]
        self.cursor.cast_rays(points)
        self.cursor.get_intersections(lines)



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
    