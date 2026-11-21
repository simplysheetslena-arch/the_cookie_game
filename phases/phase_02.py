"""Cookie Wars — Phase 2: two balls race for one cookie.

Run from any working directory:
    python phases/phase_02.py
"""
import sys
from pathlib import Path

import pygame

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
START_DELAY = 0.7
COOKIE_SIZE = 150  # Change this to resize the cookie
CORNER_MARGIN = 55  # Keep both balls fully visible near the corners

# Both balls begin equally far from the cookie, at opposite corners.
# Change these speeds to choose which ball wins.
TOP_RIGHT_BALL_SPEED = 245
BOTTOM_LEFT_BALL_SPEED = 205


def new_game():
    cookie = Cookie(x=WIDTH // 2, y=HEIGHT // 2, size=COOKIE_SIZE)
    top_right_ball = Ball(x=WIDTH - CORNER_MARGIN, y=CORNER_MARGIN, radius=18, speed=TOP_RIGHT_BALL_SPEED)
    bottom_left_ball = Ball(x=CORNER_MARGIN, y=HEIGHT - CORNER_MARGIN, radius=18, speed=BOTTOM_LEFT_BALL_SPEED)
    balls = [top_right_ball, bottom_left_ball]
    return balls, cookie, 0.0, False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 2")
    clock = pygame.time.Clock()
    heart_bubble = SpeechBubble("heart")
    sad_bubble = SpeechBubble("sad")
    balls, cookie, elapsed, finished = new_game()

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
                    balls, cookie, elapsed, finished = new_game()

        elapsed += dt
        if elapsed >= START_DELAY and not finished:
            # Advance everyone. Compare distance to cookie after moving.
            for ball in balls:
                move_towards(ball, cookie.center, dt)

            touching = [ball for ball in balls if ball_touches_cookie(ball, cookie)]
            if touching:
                # If both touch in the same frame, award the winner to the
                # ball that penetrated the collision radius by the most.
                winner = min(touching, key=lambda b: b.position.distance_to(cookie.center))
                winner.celebrate()
                for ball in balls:
                    if ball is not winner:
                        ball.feel_sad()
                cookie.visible = False
                finished = True

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        for ball in balls:
            ball.draw(screen)
        if finished:
            for ball in balls:
                bubble = heart_bubble if ball.won else sad_bubble
                bubble.draw(screen, ball.position.x, ball.position.y)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
