"""COOKIE WARS — PHASE 6: Survival of the fastest (and luckiest).

Run from Cookie_Wars: python phases/phase_06.py
R: restart with fresh random speeds/positions/fights. ESC: quit.

This phase reuses the movement and non-overlap logic from phase 5.
Only living balls fight and move. Eliminated balls stay red and still.
"""
import random
import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.ball import Ball
from core.cookie import Cookie
from core.speech_bubble import SpeechBubble
from phases.phase_05 import move_swarm

# -------- CUSTOMIZE HERE --------
WIDTH, HEIGHT = 1280, 720
FPS = 60
BACKGROUND = (32, 36, 43)
COOKIE_SIZE = 150

NUMBER_OF_BALLS = 100          # Try 10, 40, 100...
BALL_RADIUS = 18
MIN_COOKIE_DISTANCE = 450    # Minimum starting distance from the center
MIN_SPEED = 75                # Pixels per second
MAX_SPEED = 240
SPAWN_MARGIN = 35
START_DELAY = 0.65

FIGHT_EXTRA_DISTANCE = 2      # Extra proximity margin between two balls
DEAD_COLOR = (231, 83, 89)
# -----------------------------------


def spawn_balls(cookie):
    """Generate independently random positions/speeds, without initial overlaps."""
    balls = []
    x_min, x_max = SPAWN_MARGIN + BALL_RADIUS, WIDTH - SPAWN_MARGIN - BALL_RADIUS
    y_min, y_max = SPAWN_MARGIN + BALL_RADIUS, HEIGHT - SPAWN_MARGIN - BALL_RADIUS
    # Enough initial gap to avoid fights before the race has begun.
    min_gap = 2 * BALL_RADIUS + max(5, FIGHT_EXTRA_DISTANCE + 3)
    min_center_distance = max(MIN_COOKIE_DISTANCE, cookie.radius + BALL_RADIUS + 10)

    for _ in range(max(2000, NUMBER_OF_BALLS * 450)):
        if len(balls) == NUMBER_OF_BALLS:
            break
        pos = pygame.Vector2(random.uniform(x_min, x_max), random.uniform(y_min, y_max))
        if pos.distance_squared_to(cookie.center) < min_center_distance ** 2:
            continue
        if any(pos.distance_squared_to(other.position) < min_gap ** 2 for other in balls):
            continue
        speed = random.uniform(min(MIN_SPEED, MAX_SPEED), max(MIN_SPEED, MAX_SPEED))
        ball = Ball(pos.x, pos.y, radius=BALL_RADIUS, speed=speed)
        ball.alive = True
        balls.append(ball)

    if not balls:
        raise ValueError("No hi ha espai per fer apareixer boletes: baixa MIN_COOKIE_DISTANCE.")
    if len(balls) < NUMBER_OF_BALLS:
        print(f"[Phase 6] Requested {NUMBER_OF_BALLS}, but only {len(balls)} fit. "
              "Reduce BALL_RADIUS or MIN_COOKIE_DISTANCE.")
    return balls


def resolve_fights(balls):
    """Each living ball can participate in at most one fight per frame."""
    living = [ball for ball in balls if ball.alive]
    fights = []
    for i, first in enumerate(living):
        for second in living[i + 1:]:
            trigger = first.radius + second.radius + FIGHT_EXTRA_DISTANCE
            if first.position.distance_squared_to(second.position) <= trigger ** 2:
                fights.append((first, second))

    random.shuffle(fights)  # Fair order when a crowded group collides all at once
    busy = set()
    casualties = 0
    for first, second in fights:
        if first in busy or second in busy or not first.alive or not second.alive:
            continue
        loser = random.choice((first, second))
        loser.alive = False
        loser.color = DEAD_COLOR
        loser.speed = 0
        busy.add(first)
        busy.add(second)
        casualties += 1
    return casualties


def new_game():
    cookie = Cookie(WIDTH // 2, HEIGHT // 2, size=COOKIE_SIZE)
    return cookie, spawn_balls(cookie), "waiting", 0.0, None, 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 6: Random Battles")
    clock = pygame.time.Clock()
    heart = SpeechBubble("heart")
    font = pygame.font.Font(None, 29)
    small_font = pygame.font.Font(None, 23)
    cookie, balls, state, elapsed, winner, total_fights = new_game()

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    cookie, balls, state, elapsed, winner, total_fights = new_game()

        elapsed += dt
        if state == "waiting" and elapsed >= START_DELAY:
            state = "racing"

        if state == "racing":
            living = [ball for ball in balls if ball.alive]
            # Reuse phase 5's collision avoidance, but only among living balls.
            move_swarm(living, cookie.center, dt)
            total_fights += resolve_fights(balls)

            # Dead balls never win, even if they are near the cookie.
            touching = [ball for ball in balls if ball.alive and
                        ball.position.distance_squared_to(cookie.center) <=
                        (ball.radius + cookie.radius) ** 2]
            if touching:
                winner = min(touching, key=lambda ball: ball.position.distance_squared_to(cookie.center))
                winner.celebrate()
                cookie.visible = False
                state = "finished"
            elif not any(ball.alive for ball in balls):
                state = "finished"

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        for ball in balls:
            ball.draw(screen)
        if winner is not None:
            heart.draw(screen, winner.position.x, winner.position.y)

        alive_count = sum(ball.alive for ball in balls)
        screen.blit(font.render(
            f"ALIVE: {alive_count}/{len(balls)}    ELIMINATED: {len(balls)-alive_count}    FIGHTS: {total_fights}",
            True, (195, 200, 207)), (22, 19))
        screen.blit(small_font.render("R: NEW RANDOM BATTLE     ESC: EXIT", True, (112, 120, 131)),
                    (22, HEIGHT - 33))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
