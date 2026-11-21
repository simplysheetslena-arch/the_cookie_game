"""Cookie Wars — Phase 4: the ambush.

Run: python phases/phase_04.py
R = restart, ESC = quit.
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
COOKIE_SIZE = 150
CORNER_MARGIN = 55
BALL_RADIUS = 18
START_DELAY = 0.7

# The previous winner starts WHITE and moves towards the cookie.
VICTIM_SPEED = 52
# The bottom-left ball sneaks up beside the top-left ball first.
SNEAK_SPEED = 220
SNEAK_POINT = (150, 135)  # Keeps it well away from the cookie.
SNEAK_PAUSE = 0.45
ATTACK_SPEEDS = (560, 590, 580)  # top-left, bottom-left, bottom-right
# Target offsets around the victim ensure no overlap, and everyone gets there.
AMBUSH_OFFSETS = ((-42, -10), (-8, 43), (38, 22))
ARRIVAL_TOLERANCE = 9
AFTER_ATTACK_PAUSE = 0.8
COOKIE_RACE_SPEEDS = (275, 320, 290)
DEAD_COLOR = (229, 79, 89)


def new_game():
    cookie = Cookie(WIDTH // 2, HEIGHT // 2, size=COOKIE_SIZE)
    victim = Ball(WIDTH - CORNER_MARGIN, CORNER_MARGIN,
                  radius=BALL_RADIUS, speed=VICTIM_SPEED)
    attackers = [
        Ball(CORNER_MARGIN, CORNER_MARGIN, radius=BALL_RADIUS, speed=ATTACK_SPEEDS[0]),
        Ball(CORNER_MARGIN, HEIGHT - CORNER_MARGIN, radius=BALL_RADIUS, speed=SNEAK_SPEED),
        Ball(WIDTH - CORNER_MARGIN, HEIGHT - CORNER_MARGIN,
             radius=BALL_RADIUS, speed=ATTACK_SPEEDS[2]),
    ]
    return victim, attackers, cookie, "waiting", 0.0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 4: The Ambush")
    clock = pygame.time.Clock()
    heart = SpeechBubble("heart")
    sad = SpeechBubble("sad")
    shh = SpeechBubble("shh")
    victim, attackers, cookie, state, state_time = new_game()

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
                    victim, attackers, cookie, state, state_time = new_game()

        state_time += dt
        if state == "waiting":
            if state_time >= START_DELAY:
                state, state_time = "sneaking", 0.0

        elif state == "sneaking":
            # The unsuspecting white ball is already heading to the cookie.
            move_towards(victim, cookie.center, dt)
            # Bottom-left moves alongside the LEFT edge, NOT through the cookie.
            move_towards(attackers[1], SNEAK_POINT, dt)
            if attackers[1].position.distance_to(SNEAK_POINT) < 0.1:
                state, state_time = "ready", 0.0

        elif state == "ready":
            move_towards(victim, cookie.center, dt)
            if state_time >= SNEAK_PAUSE:
                for attacker, speed in zip(attackers, ATTACK_SPEEDS):
                    attacker.speed = speed
                state, state_time = "ambush", 0.0

        elif state == "ambush":
            move_towards(victim, cookie.center, dt)
            # Each attacker has its own position around the moving victim.
            # Early arrivals WAIT. The victim only dies when all three arrive.
            for attacker, offset in zip(attackers, AMBUSH_OFFSETS):
                target = victim.position + pygame.Vector2(offset)
                move_towards(attacker, target, dt)

            all_arrived = all(
                attacker.position.distance_to(victim.position + pygame.Vector2(offset))
                <= ARRIVAL_TOLERANCE
                for attacker, offset in zip(attackers, AMBUSH_OFFSETS)
            )
            if all_arrived:
                victim.color = DEAD_COLOR
                victim.speed = 0
                state, state_time = "after_attack", 0.0

        elif state == "after_attack":
            if state_time >= AFTER_ATTACK_PAUSE:
                for attacker, speed in zip(attackers, COOKIE_RACE_SPEEDS):
                    attacker.speed = speed
                state, state_time = "cookie_race", 0.0

        elif state == "cookie_race":
            for attacker in attackers:
                move_towards(attacker, cookie.center, dt)
                # Process collisions immediately, instead of moving everybody
                # first (avoids inconsistent tie decisions).
                if ball_touches_cookie(attacker, cookie):
                    attacker.celebrate()
                    for other in attackers:
                        if other is not attacker:
                            other.feel_sad()
                    cookie.visible = False
                    state, state_time = "finished", 0.0
                    break

        screen.fill(BACKGROUND)
        cookie.draw(screen)
        victim.draw(screen)
        for attacker in attackers:
            attacker.draw(screen)

        if state in ("sneaking", "ready"):
            shh.draw(screen, attackers[1].position.x, attackers[1].position.y)
        if state == "finished":
            for attacker in attackers:
                if attacker.won:
                    heart.draw(screen, attacker.position.x, attacker.position.y)
                elif attacker.lost:
                    sad.draw(screen, attacker.position.x, attacker.position.y)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
