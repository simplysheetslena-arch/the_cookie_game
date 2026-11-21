import sys
from pathlib import Path

import pygame

# Allow running this file directly as well as with python -m.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ball import Ball
from core.cookie import Cookie
from core.movement import move_towards
from core.collisions import ball_touches_cookie
from core.speech_bubble import SpeechBubble

WIDTH, HEIGHT = 1280, 720
FPS = 60
BACKGROUND = (32, 36, 43)
START_DELAY = 0.7  # Seconds before the ball starts moving
CORNER_MARGIN = 55  # Distance from the top and right edges


def new_game():
    ball = Ball(x=WIDTH - CORNER_MARGIN, y=CORNER_MARGIN, radius=18, speed=235)
    cookie = Cookie(x=WIDTH // 2, y=HEIGHT // 2, size=150)
    bubble = SpeechBubble("heart")
    return ball, cookie, bubble, 0.0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 1")
    clock = pygame.time.Clock()
    ball, cookie, bubble, elapsed = new_game()

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    ball, cookie, bubble, elapsed = new_game()

        elapsed += dt
        if elapsed >= START_DELAY and not ball.won:
            move_towards(ball, cookie.center, dt)
            if ball_touches_cookie(ball, cookie):
                cookie.visible = False
                ball.celebrate()

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        ball.draw(screen)
        if ball.won:
            bubble.draw(screen, ball.position.x, ball.position.y)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
