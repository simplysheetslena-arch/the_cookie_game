from pathlib import Path
import pygame

ASSET_PATH = Path(__file__).resolve().parent.parent / "assets" / "cookie.png"


class Cookie:
    def __init__(self, x, y, size=88):
        if not ASSET_PATH.is_file():
            raise FileNotFoundError(f"No trobo la galeta PNG: {ASSET_PATH}")
        image = pygame.image.load(str(ASSET_PATH)).convert_alpha()
        self.image = pygame.transform.smoothscale(image, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = size * 0.43
        self.visible = True

    @property
    def center(self):
        return pygame.Vector2(self.rect.center)

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
