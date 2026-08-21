import math

import config


class Shot:
    def __init__(self, points, hit_soldier=None, exploded_at=None):
        self.points = points
        self.hit_soldier = hit_soldier
        self.exploded_at = exploded_at


def trace_shot(f, x0, y0, world, dx=config.DX, max_steps=config.MAX_STEPS, shooter=None):
    """Трассирует снаряд y = f(x - x0) + c через позицию (x0, y0).

    Функция считается в координатах солдата: u = x - x0, поэтому
    снаряд проходит точно через (x0, y0) при c = y0 - f(0).
    """
    try:
        f0 = f(0.0, y0)
    except (ValueError, ZeroDivisionError, OverflowError, ArithmeticError):
        return Shot([(x0, y0)])
    if not math.isfinite(f0):
        return Shot([(x0, y0)])

    c = y0 - f0
    points = [(x0, y0)]
    x = x0
    step = dx if dx != 0 else config.DX
    for _ in range(max_steps):
        x += step
        u = x - x0
        try:
            y = f(u, y0) + c
        except (ValueError, ZeroDivisionError, OverflowError, ArithmeticError):
            return Shot(points, exploded_at=(x, y0))
        if not math.isfinite(y):
            return Shot(points, exploded_at=(x, y0))

        # вертикальный скачок => взрыв
        if points:
            last_x, last_y = points[-1]
            if abs(y - last_y) > 40:
                return Shot(points, exploded_at=(x, y))

        points.append((x, y))

        # выход за границы поля
        if abs(x) > world.width / 2 or abs(y) > world.height / 2:
            return Shot(points)

        # попадание в препятствие
        for o in world.obstacles:
            if (x - o.x) ** 2 + (y - o.y) ** 2 <= o.r * o.r:
                return Shot(points, exploded_at=(x, y))

        # попадание в солдата (кроме самого стреляющего)
        for s in world.soldiers:
            if not s.alive or s is shooter:
                continue
            if (x - s.x) ** 2 + (y - s.y) ** 2 <= 0.6 ** 2:
                return Shot(points, hit_soldier=s)

    return Shot(points)


def trace_full(f, x0, y0, world, direction=1):
    """Полная траектория в обе стороны (для предпросмотра)."""
    fwd = trace_shot(f, x0, y0, world, dx=config.DX * direction)
    return fwd