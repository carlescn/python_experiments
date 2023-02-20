"""
Implementation of 2D shadow casting based on line-line intersections.
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

SHAPES = (
    ((200, 200), (100, 300), (100, 150), (200, 200)),
    ((150, 450), (100, 350), (250, 300), (150, 450)),
    ((250, 150), (250,  50), (350,  50), (350, 150), (250, 150)),
    ((450, 100), (550, 200)),
    ((450, 200), (550, 100)),
    ((250, 500), (450, 500), (450, 400), (350, 400), (250, 500)),
    ((650, 500), (600, 500), (600, 455)),
    ((600, 450), (600, 430)),
    ((600, 425), (600, 405)),
    ((600, 400), (600, 380)),
    ((600, 375), (600, 355)),
    ((600, 350), (600, 330)),
    ((600, 325), (600, 305)),
    ((600, 300), (600, 280)),
    ((600, 275), (600, 250), (650, 250), (650, 100), (650,  50), (750,  50), (750, 450), (700, 500)),
    ((700, 350), (700, 450), (650, 450), (650, 300), (700, 300), (700, 100)),
)

def compute_line_line_intersection(line1, line2):
    """
    Computes the intersection of two infinite lines defined by two points.
    Returns:
        x, y: point of intersection
        t: can be used to check if point is inside section line1 (0 < t < 1)
        u: can be used to check if point is inside section line2 (0 < u < 1)
    Raises:
        ZeroDivisionError: lines are parallel
    """
    #pylint:disable=invalid-name # (single letter x, y, t, u)
    x_1, y_1 = line1[0]
    x_2, y_2 = line1[1]
    x_3, y_3 = line2[0]
    x_4, y_4 = line2[1]

    denominator = (x_1 - x_2)*(y_3 - y_4) - (y_1 - y_2)*(x_3 - x_4)
    if denominator == 0:
        raise ZeroDivisionError("Lines are parallel, no intersection")

    t = ((x_1 - x_3) * (y_3 - y_4) - (y_1 - y_3) * (x_3 - x_4)) / denominator
    u = ((x_1 - x_3) * (y_1 - y_2) - (y_1 - y_3) * (x_1 - x_2)) / denominator
    x = x_1 + t * (x_2 - x_1)
    y = y_1 + t * (y_2 - y_1)

    return x, y, t, u


class Ray():
    def __init__(self, origin, angle, degrees = False):
        self.color = pg.Color("red")
        self.theta = np.deg2rad(angle) if degrees else angle
        self.origin = None
        self.direction = None
        self.update_position(origin)

    def update_position(self, origin):
        self.origin = origin
        self.direction = (self.origin[0] - np.cos(self.theta),
                          self.origin[1] - np.sin(self.theta))

    def compute_ray_section_intersection(self, line):
        """
        Compute intersection between ray (self) and passed line section.
        Returns:
            x, y: point of intersection
            t: can be used to compare the distance of two points from the ray origin
        Raises:
            ZeroDivisionError: lines are parallel
        """
        #pylint:disable=invalid-name # (single letter x, y, t, u)
        try:
            x, y, t, u = compute_line_line_intersection((self.origin, self.direction), line)

            if not 0 < u < 1:
                raise ValueError("Intersection outside section")
            if t < 0:
                raise ValueError("Intersection in opposite direction of ray")

            return x, y, t

        except ZeroDivisionError as exception:
            raise exception

    def get_closest_intersection(self, lines):
        #pylint:disable=invalid-name # (single letter x, y)
        closest = np.Infinity
        intersection = None
        for line in lines:
            try:
                x, y, distance = self.compute_ray_section_intersection(line)
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


class ShadowCaster():
    def __init__(self, position, size, color, alpha = 128):
        self.position = position
        self.rays = []
        self.triangles = []
        self.image = self._get_image(size, color, alpha)

    def _get_image(self, size, color, alpha):
        img = pg.image.load("img/shadow_casting_radial.png").convert_alpha()
        img = pg.transform.scale(img, (size, size))
        surf = pg.Surface(img.get_size()).convert_alpha()
        surf.set_alpha(alpha)
        surf.fill(color)
        surf.blit(img, (0, 0), None, pg.BLEND_RGBA_MULT)
        return surf

    def _get_rays_intersections(self, lines):
        intersections = []
        for ray in self.rays:
            intersection = ray.get_closest_intersection(lines)
            if intersection is None:
                raise TypeError("Ray should at least intercept the edges of the screen")
            intersections.append(intersection)
        return intersections

    def set_position(self, position):
        self.position = position

    def cast_rays(self, points):
        #pylint:disable=invalid-name # (single letter x, y)
        error = 1e-10
        points = set(points)
        x, y = self.position
        angles = []
        for point in points:
            angle = np.arctan2(y - point[1], x - point[0])
            angles += [angle - error, angle + error]
        angles.sort()
        self.rays = [Ray(self.position, angle) for angle in angles]

    def update_triangles(self, lines, targets):
        self.cast_rays(targets)
        vertices = self._get_rays_intersections(lines)
        assert len(self.rays) == len(vertices)

        self.triangles = []
        vertices.append(vertices[0])
        for vert1, vert2 in zip(vertices, vertices[1:]):
            self.triangles.append((self.position, vert1, vert2))

    def draw(self, surface):
        radial_light = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

        light_center = self.position - np.divide(self.image.get_size(), 2)
        radial_light.blit(self.image, light_center)

        mask = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        for triangle in self.triangles:
            pg.draw.polygon(mask, pg.Color("white"), triangle)
        radial_light.blit(mask, (0,0), None, pg.BLEND_RGBA_MULT)

        surface.blit(radial_light, (0, 0), None, pg.BLEND_RGBA_ADD)


class Map():
    def __init__(self, shapes):
        self.polygons = shapes
        self.lines = self._get_lines(self.polygons)
        self.ray_targets = self._get_ray_targets(self.lines)

        self.background = self._get_background()
        self.lights = self._get_fixed_lights()

    def _get_background(self):
        #pylint:disable=invalid-name # (single letter x, y)
        img = pg.image.load("img/shadow_casting_floor.png").convert()
        img = pg.transform.scale(img, np.multiply(img.get_size(), 2))
        background = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for x in range(0, background.get_width(), img.get_width()):
            for y in range(0, background.get_height(), img.get_height()):
                background.blit(img, (x, y))
        return background

    def _get_lines(self, polygons):
        lines = list(SCREEN_EDGES)
        for line in polygons:
            if len(line) > 2:
                for point1, point2 in zip(line, line[1:]):
                    lines.append((point1, point2))
            else:
                lines.append(line)
        return lines

    def _get_ray_targets(self, lines):
        points = [point for line in lines for point in line]
        points += self._get_lines_intersections(lines)
        return points

    def _get_lines_intersections(self, lines):
        #pylint:disable=invalid-name # (single letter x, y, t, u)
        intersections = []
        for i, line1 in enumerate(lines):
            for line2 in lines[i:]:
                try:
                    x, y, t, u = compute_line_line_intersection(line1, line2)
                    if 0 < t < 1 and 0 < u < 1:
                        intersections.append((x, y))
                except ZeroDivisionError:
                    pass
        return set(intersections)

    def _get_fixed_lights(self):
        size_big = 800
        size_small = 300
        alpha = 64
        lights = [
            ShadowCaster((400, 300), size_big,   pg.Color("white"), alpha),
            ShadowCaster((740,  60), size_small, pg.Color("orange"), alpha),
            ShadowCaster((740, 210), size_small, pg.Color("orange"), alpha),
            ShadowCaster((740, 320), size_small, pg.Color("orange"), alpha),
            ShadowCaster((740, 430), size_small, pg.Color("orange"), alpha),
        ]

        surf = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        for light in lights:
            light.update_triangles(self.lines, self.ray_targets)
            light.draw(surf)

        return surf

    def draw_surface(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.lights, (0, 0), None, pg.BLEND_RGBA_ADD)

    def draw_lines(self, surface):
        for line in self.polygons:
            pg.draw.lines(surface, pg.Color("black"), False, line, 5)


class Game():
    def __init__(self):
        self.map = Map(SHAPES)
        self.cursor = ShadowCaster((0, 0), 600, pg.Color("gold"), 64)

    def update(self):
        # Make sure cursor is inside the screen so all rays can find at least one intersection
        cursor_x, cursor_y = pg.mouse.get_pos()
        if not 0 < cursor_x < SCREEN_WIDTH or not 0 < cursor_y < SCREEN_HEIGHT:
            return

        self.cursor.set_position(pg.mouse.get_pos())
        self.cursor.update_triangles(self.map.lines, self.map.ray_targets)

    def draw(self, surface):
        self.map.draw_surface(surface)

        self.cursor.draw(surface)

        self.map.draw_lines(surface)
        pg.draw.circle(surface, pg.Color("red"), pg.mouse.get_pos(), 8)


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
            self.game.draw(self.screen)
            self.print_fps()
            # print(self.game.cursor.position)
            pg.display.flip()
            self.clock.tick(TARGET_FPS)

    def quit(self):
        pg.quit()

    def print_fps(self):
        text = f"FPS: {int(self.clock.get_fps())}"
        rendered_text = self.font.render(text, True, pg.Color("red"))
        self.screen.blit(rendered_text, (10, 10))


if __name__=="__main__":
    App()
    