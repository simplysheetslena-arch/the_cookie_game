"""Cookie Wars — Phase 3: one winner, three conspirators.

Run: python phases/phase_03.py
Controls: R to replay, ESC to quit.
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
COOKIE_SIZE = 150
CORNER_MARGIN = 55

# All four are equally far from the center. Top-right always wins.
TOP_RIGHT_SPEED = 330
OTHER_SPEED = 215

# The three disappointed balls meet here. Keep a little space between them
# so they look like a group instead of overlapping.
MEETING_POINT = pygame.Vector2(315, 525)
MEETING_OFFSETS = [(-33, 16), (0, -15), (33, 16)]
SAD_PAUSE = 1.4
MEETING_SPEED = 270
MEETING_TOLERANCE = 1.5


def new_game():
    cookie = Cookie(WIDTH // 2, HEIGHT // 2, size=COOKIE_SIZE)
    balls = [
        Ball(CORNER_MARGIN, CORNER_MARGIN, speed=OTHER_SPEED),         # top left
        Ball(WIDTH - CORNER_MARGIN, CORNER_MARGIN, speed=TOP_RIGHT_SPEED),  # winner!
        Ball(CORNER_MARGIN, HEIGHT - CORNER_MARGIN, speed=OTHER_SPEED), # bottom left
        Ball(WIDTH - CORNER_MARGIN, HEIGHT - CORNER_MARGIN, speed=OTHER_SPEED), # bottom right
    ]
    for ball in balls:
        ball.radius = 18
    return balls, cookie, "race", 0.0, 0.0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 3")
    clock = pygame.time.Clock()
    heart_bubble = SpeechBubble("heart")
    sad_bubble = SpeechBubble("sad")
    dots_bubble = SpeechBubble("dots")
    balls, cookie, state, elapsed, state_elapsed = new_game()

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
                    balls, cookie, state, elapsed, state_elapsed = new_game()

        elapsed += dt
        state_elapsed += dt
        if state == "race" and elapsed >= START_DELAY:
            for ball in balls:
                move_towards(ball, cookie.center, dt)
            touching = [ball for ball in balls if ball_touches_cookie(ball, cookie)]
            if touching:
                winner = min(touching, key=lambda b: b.position.distance_to(cookie.center))
                winner.celebrate()
                for ball in balls:
                    if ball is not winner:
                        ball.feel_sad()
                cookie.visible = False
                state, state_elapsed = "sad_pause", 0.0

        elif state == "sad_pause" and state_elapsed >= SAD_PAUSE:
            state, state_elapsed = "meeting", 0.0

        elif state == "meeting":
            losers = [b for b in balls if b.lost]
            for ball, offset in zip(losers, MEETING_OFFSETS):
                ball.speed = MEETING_SPEED
                move_towards(ball, MEETING_POINT + pygame.Vector2(offset), dt)
            if all(ball.position.distance_to(MEETING_POINT + pygame.Vector2(offset)) <= MEETING_TOLERANCE
                   for ball, offset in zip(losers, MEETING_OFFSETS)):
                state, state_elapsed = "talking", 0.0

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        for ball in balls:
            ball.draw(screen)
        for ball in balls:
            if ball.won:
                heart_bubble.draw(screen, ball.position.x, ball.position.y)
            elif ball.lost and state == "sad_pause":
                sad_bubble.draw(screen, ball.position.x, ball.position.y)
        if state == "talking":
            # One shared bubble makes the three dots look like a conversation.
            dots_bubble.draw(screen, MEETING_POINT.x, MEETING_POINT.y - 22)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
