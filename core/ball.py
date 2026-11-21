import pygame


class Ball:
    def __init__(self, x, y, radius=18, speed=235):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.speed = speed  # Pixels per second
        self.color = (250, 250, 250)
        self.won = False
        self.lost = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def celebrate(self):
        self.won = True
        self.color = (73, 211, 126)

    def feel_sad(self):
        self.lost = True
        self.color = (97, 153, 244)
