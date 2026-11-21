

def ball_touches_cookie(ball, cookie):
    if not cookie.visible:
        return False
    distance = ball.position.distance_to(cookie.center)
    return distance <= ball.radius + cookie.radius


def balls_touch(ball_a, ball_b):
    return ball_a.position.distance_to(ball_b.position) <= ball_a.radius + ball_b.radius
