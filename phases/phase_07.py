"""COOKIE WARS - PHASE 7: THE HUNGER GAMES.

Run: python phases/phase_07.py (from any working directory)
R: new random game  |  SPACE: pause/resume  |  ESC: exit

Put your own background at assets/hunger_games.jpg. If missing, the game
runs with a dark fallback background; all previous phases remain untouched.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.cookie import Cookie
from core.speech_bubble import SpeechBubble

# ------------------- CUSTOMIZE HERE -------------------
ARENA_WIDTH = 1672                # Arena width; the scoreboard is displayed to its right
ARENA_HEIGHT = 941
SIDEBAR_WIDTH = 320

WIDTH = ARENA_WIDTH + SIDEBAR_WIDTH
HEIGHT = ARENA_HEIGHT

FPS = 60
BALL_RADIUS = 15
START_CIRCLE_RADIUS = 135
MIN_SPEED = 55                    # Randomized speed for each participant
MAX_SPEED = 105
START_DELAY = 1.2
ROUND_PAUSE = 1.0                 # Pause between rounds
FIGHT_DISTANCE_EXTRA = 1.5
FIGHT_COOLDOWN = 0.2              # Prevents simultaneous chain eliminations
FIGHT_DURATION = 0.9               # Seconds spent motionless with angry expressions
COOKIE_SIZE = 145
# Minimum distance from the center for OUTER points in each round.
# The central point (one per round) is the only exception.
ROUND_MIN_CENTER_DISTANCES = (530, 300, 130)

ROUND_MAX_RADII = (
    (760, 425),
    (540, 320),
    (300, 210)
)

MIN_DISTANCE_BETWEEN_POINTS = 75
BACKGROUND_FILE = ROOT / "assets" / "hunger_games.png"
FALLBACK_BACKGROUND = (32, 36, 43)
# 12 pairs of colors: no pure green, blue, or red.
DISTRICT_COLORS = [
    (255, 191, 94), (186, 137, 247), (240, 166, 198),
    (243, 216, 114), (193, 153, 119), (235, 149, 112),
    (220, 188, 239), (239, 196, 159), (178, 163, 222),
    (240, 187, 123), (201, 176, 142), (244, 207, 182),
]
DEAD_COLOR = (225, 76, 83)
WIN_COLOR = (73, 211, 126)
PANEL_BG = (21, 25, 32)
WHITE = (244, 246, 248)
MUTED = (173, 183, 193)
CENTER = pygame.Vector2(ARENA_WIDTH / 2, HEIGHT / 2)
# ---------------------------------------------------------


class Tribute:
    def __init__(self, number: int, position: pygame.Vector2, speed: float):
        self.number = number
        self.district = (number - 1) // 2 + 1
        self.original_color = DISTRICT_COLORS[self.district - 1]
        self.color = self.original_color
        self.position = pygame.Vector2(position)
        self.target = pygame.Vector2(position)
        self.speed = speed
        self.alive = True
        self.arrived = False
        self.last_fight_time = -100.0
        self.fighting = False

    def move(self, dt: float):
        if not self.alive or self.arrived or self.fighting:
            return
        delta = self.target - self.position
        distance = delta.length()
        step = self.speed * dt
        if distance <= step or distance <= 0.75:
            self.position = self.target.copy()
            self.arrived = True
        elif distance > 0:
            self.position += delta * (step / distance)

    def draw(self, surface: pygame.Surface, number_font: pygame.font.Font):
        x, y = round(self.position.x), round(self.position.y)
        pygame.draw.circle(surface, (16, 19, 24), (x, y), BALL_RADIUS + 2)
        pygame.draw.circle(surface, self.color, (x, y), BALL_RADIUS)
        label_color = (26, 27, 32) if self.alive else WHITE
        label = number_font.render(str(self.number), True, label_color)
        surface.blit(label, label.get_rect(center=(x, y)))


def create_destinations(count: int, stage: int):
    """Create one central point and new random outer points for each round.

    Outer points stay inside the arena, beyond the minimum center distance,
    and are spaced far enough apart to avoid near-identical destinations.
    """
    points = [CENTER.copy()]
    minimum_radius = ROUND_MIN_CENTER_DISTANCES[stage]
    max_x, max_y = ROUND_MAX_RADII[stage]

    for _ in range(count - 1):
        for attempt in range(10000):
            # Sample uniformly inside the ellipse (not just along its edge).
            angle = random.uniform(0, math.tau)
            radial_fraction = math.sqrt(random.random())
            candidate = CENTER + pygame.Vector2(
                max_x * radial_fraction * math.cos(angle),
                max_y * radial_fraction * math.sin(angle),
            )
            if candidate.distance_to(CENTER) < minimum_radius:
                continue
            if not (BALL_RADIUS + 10 <= candidate.x <= ARENA_WIDTH - BALL_RADIUS - 10):
                continue
            if not (BALL_RADIUS + 10 <= candidate.y <= HEIGHT - BALL_RADIUS - 10):
                continue
            if any(candidate.distance_to(other) < MIN_DISTANCE_BETWEEN_POINTS for other in points):
                continue
            points.append(candidate)
            break
        else:
            raise RuntimeError(
                f"No es poden generar {count} punts amb aquesta configuracio. "
                "Redueix MIN_DISTANCE_BETWEEN_POINTS o amplia ROUND_MAX_RADII."
            )
    return points


def make_round_points():
    """Generate fresh destinations whenever a game starts, including restarts with R."""
    return [create_destinations(count, stage) for stage, count in enumerate((16, 11, 5))]


ROUND_NAMES = ["ROUND 1  /  OUTER ARENA", "ROUND 2  /  CLOSING IN", "ROUND 3  /  FINAL ZONE"]


def new_game():
    tributes = []
    for i in range(24):
        angle = -math.pi / 2 + 2 * math.pi * i / 24
        start = CENTER + pygame.Vector2(
            START_CIRCLE_RADIUS * math.cos(angle),
            START_CIRCLE_RADIUS * math.sin(angle),
        )
        tributes.append(Tribute(i + 1, start, random.uniform(MIN_SPEED, MAX_SPEED)))
    cookie = Cookie(round(CENTER.x), round(CENTER.y), size=COOKIE_SIZE)
    cookie.visible = False
    round_points = make_round_points()
    return tributes, cookie, "intro", 0, 0.0, 0, None, 0.0, round_points


def assign_destinations(tributes, stage, round_points):
    destinations = round_points[stage]
    for tribute in tributes:
        if tribute.alive:
            tribute.target = random.choice(destinations).copy()
            tribute.arrived = False


def fight_contacts(tributes, elapsed, active_fights):
    """Start fights; eliminate neither participant until the animation ends."""
    living = [t for t in tributes if t.alive and not t.fighting]
    threshold2 = (2 * BALL_RADIUS + FIGHT_DISTANCE_EXTRA) ** 2
    pairs = []
    for i, first in enumerate(living):
        for other in living[i + 1:]:
            if (first.position - other.position).length_squared() <= threshold2:
                pairs.append((first, other))
    random.shuffle(pairs)
    used = set()
    for first, second in pairs:
        if first in used or second in used or first.fighting or second.fighting:
            continue
        if (elapsed - first.last_fight_time < FIGHT_COOLDOWN or
                elapsed - second.last_fight_time < FIGHT_COOLDOWN):
            continue
        # Both participants stop moving during the fight and display speech bubbles.
        first.fighting = second.fighting = True
        first.last_fight_time = second.last_fight_time = elapsed
        active_fights.append((first, second, elapsed + FIGHT_DURATION))
        used.update((first, second))


def resolve_fights(active_fights, elapsed):
    casualties = 0
    for fight in active_fights[:]:
        first, second, ending = fight
        if elapsed < ending:
            continue
        loser = random.choice((first, second))
        loser.alive = False
        loser.color = DEAD_COLOR
        loser.arrived = True
        first.fighting = second.fighting = False
        active_fights.remove(fight)
        casualties += 1
    return casualties


def stage_complete(tributes):
    living = [t for t in tributes if t.alive]
    return bool(living) and all(t.arrived and not t.fighting for t in living)


def random_cookie_position(living, cookie_radius):
    """Choose a random cookie position that does not overlap any living participant."""
    margin = int(cookie_radius + BALL_RADIUS + 24)
    for _ in range(5000):
        point = pygame.Vector2(random.uniform(margin, ARENA_WIDTH - margin),
                               random.uniform(margin, HEIGHT - margin))
        if all(point.distance_to(t.position) > cookie_radius + BALL_RADIUS + 35
               for t in living):
            return point
    # This is very unlikely with 24 participants; use a grid search as a fallback.
    candidates = [pygame.Vector2(x, y)
                  for x in range(margin, ARENA_WIDTH - margin, 24)
                  for y in range(margin, HEIGHT - margin, 24)]
    return max(candidates, key=lambda p: min(p.distance_to(t.position) for t in living))


def load_background():
    if BACKGROUND_FILE.is_file():
        try:
            img = pygame.image.load(str(BACKGROUND_FILE)).convert()
            # Preserve the entire image without cropping or distortion.
            scale = min(ARENA_WIDTH / img.get_width(), HEIGHT / img.get_height())
            w = max(1, round(img.get_width() * scale))
            h = max(1, round(img.get_height() * scale))
            fitted = pygame.transform.smoothscale(img, (w, h))
            background = pygame.Surface((ARENA_WIDTH, HEIGHT))
            background.fill(FALLBACK_BACKGROUND)
            background.blit(fitted, ((ARENA_WIDTH - w) // 2, (HEIGHT - h) // 2))
            return background
        except pygame.error as exc:
            print(f"No puc carregar hunger_games.jpg: {exc}. Fons provisional activat.")
    else:
        print("INFO: posa assets/hunger_games.jpg per personalitzar el fons.")
    bg = pygame.Surface((ARENA_WIDTH, HEIGHT))
    bg.fill(FALLBACK_BACKGROUND)
    return bg


def draw_token(screen, t, x, y, font, *, dead=False):
    color = t.original_color
    pygame.draw.circle(screen, color, (x, y), 12)
    label = font.render(str(t.number), True, (25, 25, 29))
    screen.blit(label, label.get_rect(center=(x, y)))
    if dead:
        pygame.draw.line(screen, (230, 83, 91), (x - 11, y - 11), (x + 11, y + 11), 2)


def draw_panel(screen, tributes, stage_label, fight_count, fonts, winner):
    title_font, body_font, number_font, small_font = fonts
    pygame.draw.rect(screen, PANEL_BG, (ARENA_WIDTH, 0, WIDTH - ARENA_WIDTH, HEIGHT))
    pygame.draw.line(screen, (69, 76, 84), (ARENA_WIDTH, 0), (ARENA_WIDTH, HEIGHT), 2)
    px = ARENA_WIDTH + 25
    screen.blit(title_font.render("THE HUNGER GAMES", True, WHITE), (px, 24))
    screen.blit(small_font.render(stage_label, True, MUTED), (px, 63))
    living = [t for t in tributes if t.alive]
    dead = [t for t in tributes if not t.alive]
    screen.blit(body_font.render(f"ALIVE   {len(living):02d} / 24", True, (120, 217, 169)), (px, 110))
    screen.blit(body_font.render(f"ELIMINATED   {len(dead):02d}", True, (244, 132, 138)), (px, 150))
    screen.blit(small_font.render(f"FIGHTS: {fight_count}", True, MUTED), (px, 187))
    pygame.draw.line(screen, (67, 73, 79), (px, 225), (WIDTH - 22, 225), 1)

    screen.blit(body_font.render("SURVIVORS", True, WHITE), (px, 242))
    for index, t in enumerate(living):
        # 4 columns, up to 6 rows (all 24 visible)
        col, row = index % 4, index // 4
        draw_token(screen, t, px + 20 + col * 68, 291 + row * 38, number_font)

    pygame.draw.line(screen, (67, 73, 79), (px, 532), (WIDTH - 22, 532), 1)
    screen.blit(body_font.render("FALLEN TRIBUTES", True, WHITE), (px, 548))
    for index, t in enumerate(dead):
        col, row = index % 4, index // 4
        draw_token(screen, t, px + 20 + col * 68, 598 + row * 38, number_font, dead=True)

    if winner is not None:
        winner_text = body_font.render(f"WINNER: TRIBUTE {winner.number}", True, (120, 217, 169))
        screen.blit(winner_text, (px, 838))
    else:
        screen.blit(small_font.render("R: RESTART    SPACE: PAUSE    ESC: EXIT", True, MUTED), (px, 853))


def main():
    pygame.init()
    # The simulation uses its original logical coordinates, but the window
    # is scaled to fit the monitor without cutting off the map or scoreboard.
    monitor = pygame.display.Info()
    scale = min((monitor.current_w - 80) / WIDTH,
                (monitor.current_h - 100) / HEIGHT, 1.0)
    display_size = (max(640, int(WIDTH * scale)), max(300, int(HEIGHT * scale)))
    screen = pygame.display.set_mode(display_size)
    canvas = pygame.Surface((WIDTH, HEIGHT))
    pygame.display.set_caption("Cookie Wars - Phase 7: The Hunger Games")
    clock = pygame.time.Clock()
    number_font = pygame.font.Font(None, 23)
    title_font = pygame.font.Font(None, 32)
    body_font = pygame.font.Font(None, 27)
    small_font = pygame.font.Font(None, 21)
    fonts = (title_font, body_font, number_font, small_font)
    background = load_background()
    shade = pygame.Surface((ARENA_WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((8, 11, 15, 62))  # Keep numbered tributes readable against photos
    heart = SpeechBubble("heart")
    angry = SpeechBubble("angry")
    tributes, cookie, state, stage, wait_elapsed, fights, winner, elapsed, round_points = new_game()
    active_fights = []
    paused = False
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
                    tributes, cookie, state, stage, wait_elapsed, fights, winner, elapsed, round_points = new_game()
                    active_fights = []
                    paused = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            elapsed += dt
            if state in ("intro", "between"):
                wait_elapsed += dt
                if wait_elapsed >= (START_DELAY if state == "intro" else ROUND_PAUSE):
                    wait_elapsed = 0.0
                    if stage < 3:
                        assign_destinations(tributes, stage, round_points)
                        state = "moving"
                    else:
                        living = [t for t in tributes if t.alive]
                        cookie_pos = random_cookie_position(living, cookie.radius)
                        cookie.rect.center = (round(cookie_pos.x), round(cookie_pos.y))
                        cookie.visible = True
                        for t in living:
                            t.target = cookie.center.copy()
                            t.arrived = False
                        state = "cookie_race"

            elif state in ("moving", "cookie_race"):
                for t in tributes:
                    t.move(dt)
                fights += resolve_fights(active_fights, elapsed)
                fight_contacts(tributes, elapsed, active_fights)
                if state == "cookie_race":
                    cookie_touching = [
                        t for t in tributes if t.alive and
                        not t.fighting and t.position.distance_squared_to(cookie.center) <= (BALL_RADIUS + cookie.radius) ** 2
                    ]
                    if cookie_touching and not active_fights:
                        winner = min(cookie_touching, key=lambda t: t.position.distance_squared_to(cookie.center))
                        winner.color = WIN_COLOR
                        cookie.visible = False
                        state = "finished"
                elif not active_fights and stage_complete(tributes):
                    stage += 1
                    state = "between"
                    wait_elapsed = 0.0

        canvas.blit(background, (0, 0))
        canvas.blit(shade, (0, 0))
        cookie.draw(canvas)
        # Dead tributes behind the living ones.
        for t in tributes:
            if not t.alive:
                t.draw(canvas, number_font)
        for t in tributes:
            if t.alive:
                t.draw(canvas, number_font)
        if winner is not None:
            heart.draw(canvas, winner.position.x, winner.position.y)

        if state == "intro":
            stage_label = "24 TRIBUTES - GET READY"
        elif state == "finished":
            stage_label = "THE WINNER TAKES THE COOKIE"
        elif stage >= 3:
            stage_label = "FINAL: THE COOKIE"
        else:
            stage_label = ROUND_NAMES[stage]
        draw_panel(canvas, tributes, stage_label, fights, fonts, winner)
        if paused:
            pause_text = title_font.render("PAUSED", True, WHITE)
            canvas.blit(pause_text, pause_text.get_rect(center=(ARENA_WIDTH / 2, 43)))
        # Speech bubbles appear above both participants during the fight pause.
        for first, second, ending in active_fights:
            for t in (first, second):
                angry.draw(canvas, t.position.x, t.position.y)
        pygame.transform.smoothscale(canvas, display_size, screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
