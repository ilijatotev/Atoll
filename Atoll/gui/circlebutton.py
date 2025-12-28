import pygame
import math
from common import *

class CircleButton:
    def __init__(self, center, radius, color=BACKGROUND_COLOR):
        self.center = center
        self.radius = radius
        self.color = color
        self.hover_color = HOVER_COLOR
        self.hovered = False

    def update(self, mouse_pos):
        x, y = mouse_pos
        cx, cy = self.center
        self.hovered = math.hypot(x - cx, y - cy) <= self.radius

    def draw(self, screen):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.circle(screen, current_color, self.center, self.radius)
        pygame.draw.circle(screen, (0,0,0), self.center, self.radius, 2)

    def is_clicked(self, pos):
        x, y = pos
        cx, cy = self.center
        return math.hypot(x - cx, y - cy) <= self.radius
