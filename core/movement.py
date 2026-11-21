import pygame


def move_towards(ball, target, dt):
    """Move toward target at a consistent speed regardless of FPS."""
    direction = pygame.Vector2(target) - ball.position
    distance = direction.length()
    if distance == 0:
        return
    step = min(ball.speed * dt, distance)
    ball.position += direction.normalize() * step
