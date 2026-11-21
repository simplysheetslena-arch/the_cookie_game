"""COOKIE WARS — PHASE 5: The swarm

Run from the project folder: python phases/phase_05.py
R = restart with new random positions/speeds | ESC = quit

Change NUMBER_OF_BALLS, MIN_COOKIE_DISTANCE and speeds below.
"""
import math
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

# --------- CUSTOMIZE HERE ---------
WIDTH, HEIGHT = 1280, 720
FPS = 60
BACKGROUND = (32, 36, 43)
COOKIE_SIZE = 150

NUMBER_OF_BALLS = 50          # Try 10, 40, 100, 200...
BALL_RADIUS = 18              # Smaller balls work better for large groups
MIN_COOKIE_DISTANCE = 450    # Minimum initial distance from cookie CENTER
MIN_SPEED = 75                # Pixels per second
MAX_SPEED = 240
SPAWN_MARGIN = 35
START_DELAY = 0.65

# At high densities balls may form a jam: this is intentional.
SEPARATION_PASSES = 3
# ----------------------------------


def spawn_balls(cookie):
    """Spawn balls outside a minimum cookie radius, without initial overlaps."""
    balls = []
    width_min, width_max = SPAWN_MARGIN + BALL_RADIUS, WIDTH - SPAWN_MARGIN - BALL_RADIUS
    height_min, height_max = SPAWN_MARGIN + BALL_RADIUS, HEIGHT - SPAWN_MARGIN - BALL_RADIUS
    min_separation = BALL_RADIUS * 2 + 3
    max_attempts = max(2000, NUMBER_OF_BALLS * 450)

    for _ in range(max_attempts):
        if len(balls) == NUMBER_OF_BALLS:
            break
        x = random.uniform(width_min, width_max)
        y = random.uniform(height_min, height_max)
        point = pygame.Vector2(x, y)
        if point.distance_to(cookie.center) < max(MIN_COOKIE_DISTANCE, cookie.radius + BALL_RADIUS + 10):
            continue
        if any(point.distance_squared_to(ball.position) < min_separation ** 2 for ball in balls):
            continue
        speed = random.uniform(min(MIN_SPEED, MAX_SPEED), max(MIN_SPEED, MAX_SPEED))
        balls.append(Ball(x, y, radius=BALL_RADIUS, speed=speed))

    if not balls:
        raise ValueError("No hi ha espai per posar cap boleta. Redueix MIN_COOKIE_DISTANCE.")
    if len(balls) < NUMBER_OF_BALLS:
        print(f"[Phase 5] Requested {NUMBER_OF_BALLS} balls, but only {len(balls)} fit without overlaps. "
              "Reduce BALL_RADIUS or MIN_COOKIE_DISTANCE.")
    return balls


def keep_inside(ball):
    r = ball.radius
    ball.position.x = max(r, min(WIDTH - r, ball.position.x))
    ball.position.y = max(r, min(HEIGHT - r, ball.position.y))


def move_swarm(balls, target, dt):
    """All balls seek the cookie; collisions resolve by pushing each other apart.

    There is no pathfinding or pushing through neighbors: at high density,
    congestion and gridlock are a legitimate result.
    """
    old_positions = [ball.position.copy() for ball in balls]

    # 1) Desired motion toward the cookie.
    for ball in balls:
        direction = target - ball.position
        length = direction.length()
        if length > 0.00001:
            ball.position += direction * (min(ball.speed * dt, length) / length)

    # 2) Non-penetration: separate touching balls. Pairwise resolution is
    # intentionally simple and suitable for ~10-200 balls.
    for _ in range(SEPARATION_PASSES):
        for i in range(len(balls)):
            a = balls[i]
            for j in range(i + 1, len(balls)):
                b = balls[j]
                delta = b.position - a.position
                min_dist = a.radius + b.radius
                dist_sq = delta.length_squared()
                if dist_sq >= min_dist * min_dist:
                    continue
                if dist_sq < 1e-12:
                    # Rare exact coincidence: assign a stable separation axis.
                    angle = (i * 17 + j * 31) * 2.399963229728653
                    normal = pygame.Vector2(math.cos(angle), math.sin(angle))
                    distance = 0
                else:
                    distance = math.sqrt(dist_sq)
                    normal = delta / distance
                overlap = min_dist - distance
                a.position -= normal * (overlap / 2 + 0.01)
                b.position += normal * (overlap / 2 + 0.01)
        for ball in balls:
            keep_inside(ball)

    # 3) Safety: if a numerical correction produces too much movement,
    # restrict it to prevent balls from visually teleporting.
    # (We deliberately don't cap correction here: resolving overlap is the
    # priority, and high density is allowed to jam.)
    return old_positions


def new_game():
    cookie = Cookie(WIDTH // 2, HEIGHT // 2, size=COOKIE_SIZE)
    balls = spawn_balls(cookie)
    return cookie, balls, "waiting", 0.0, None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 5: The Swarm")
    clock = pygame.time.Clock()
    heart = SpeechBubble("heart")
    sad = SpeechBubble("sad")
    font = pygame.font.Font(None, 29)
    small_font = pygame.font.Font(None, 23)
    cookie, balls, state, elapsed, winner = new_game()

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.04)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    cookie, balls, state, elapsed, winner = new_game()

        elapsed += dt
        if state == "waiting" and elapsed >= START_DELAY:
            state = "racing"
        if state == "racing":
            move_swarm(balls, cookie.center, dt)
            # The winner is the first ball touching the cookie; if multiple
            # contact in one frame, choose the one nearest the cookie.
            touching = [b for b in balls if b.position.distance_to(cookie.center) <= b.radius + cookie.radius]
            if touching:
                winner = min(touching, key=lambda b: b.position.distance_squared_to(cookie.center))
                winner.celebrate()
                for b in balls:
                    if b is not winner:
                        b.feel_sad()
                cookie.visible = False
                state = "finished"

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        for ball in balls:
            ball.draw(screen)

        if state == "finished" and winner is not None:
            # Show a single heart; not 100 speech bubbles crowding the screen.
            heart.draw(screen, winner.position.x, winner.position.y)

        count_text = font.render(f"BALLS: {len(balls)}", True, (195, 200, 207))
        screen.blit(count_text, (22, 19))
        note = "R: NEW RANDOM RACE     ESC: EXIT"
        screen.blit(small_font.render(note, True, (112, 120, 131)), (22, HEIGHT - 33))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
