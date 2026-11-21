import pygame


class SpeechBubble:
    def __init__(self, symbol="heart"):
        self.symbol = symbol

    def draw(self, screen, x, y):
        x, y = round(x), round(y)
        rect = pygame.Rect(x - 29, y - 74, 58, 46)
        white = (248, 248, 248)
        pygame.draw.rect(screen, white, rect, border_radius=13)
        pygame.draw.polygon(screen, white, [
            (x - 5, rect.bottom - 1), (x + 4, rect.bottom + 12),
            (x + 13, rect.bottom - 1),
        ])
        if self.symbol == "heart":
            red = (240, 75, 92)
            cx, cy = x, rect.centery + 1
            pygame.draw.circle(screen, red, (cx - 7, cy - 4), 8)
            pygame.draw.circle(screen, red, (cx + 7, cy - 4), 8)
            pygame.draw.polygon(screen, red, [
                (cx - 15, cy - 2), (cx + 15, cy - 2), (cx, cy + 17)
            ])
        elif self.symbol == "sad":
            dark = (45, 54, 69)
            pygame.draw.circle(screen, dark, (x - 9, rect.centery - 5), 3)
            pygame.draw.circle(screen, dark, (x + 9, rect.centery - 5), 3)
            # Downturned mouth: a smooth frown without depending on fonts/emojis.
            pygame.draw.arc(screen, dark,
                            pygame.Rect(x - 12, rect.centery + 2, 24, 18),
                            0.15, 3.0, 3)

        elif self.symbol == "dots":
            dark = (45, 54, 69)
            cy = rect.centery + 1
            for dx in (-12, 0, 12):
                pygame.draw.circle(screen, dark, (x + dx, cy), 4)

        elif self.symbol == "shh":
            # Text instead of an emoji: works on every system.
            font = pygame.font.Font(None, 29)
            text = font.render("shh...", True, (45, 54, 69))
            screen.blit(text, text.get_rect(center=(x, rect.centery)))

        elif self.symbol == "angry":
            # Angry face drawn with shapes, without relying on emojis.
            dark = (45, 54, 69)
            cy = rect.centery
            pygame.draw.line(screen, dark, (x - 16, cy - 11), (x - 4, cy - 5), 3)
            pygame.draw.line(screen, dark, (x + 4, cy - 5), (x + 16, cy - 11), 3)
            pygame.draw.circle(screen, dark, (x - 9, cy - 1), 3)
            pygame.draw.circle(screen, dark, (x + 9, cy - 1), 3)
            pygame.draw.arc(screen, dark, pygame.Rect(x - 10, cy + 7, 20, 12), 0.15, 3.0, 3)
