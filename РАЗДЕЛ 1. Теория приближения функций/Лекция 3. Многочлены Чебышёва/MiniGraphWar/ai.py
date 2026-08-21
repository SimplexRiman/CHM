import math

import config
import physics
from mathparser import compile_function, MathParseError


class AI:
    def __init__(self, rng):
        self.rng = rng

    def choose_shot(self, soldier, world):
        enemy_team = 1 if soldier.team == 2 else 2
        enemies = world.alive(enemy_team)
        if not enemies:
            return None
        target = self.rng.choice(enemies)
        # быстрая оценка: крупный шаг, но радиус солдата 0.6 всё равно ловится
        evaldx = 0.08
        evalsteps = 1500

        def shoot(expr):
            try:
                f = compile_function(expr)
            except MathParseError:
                return None
            return physics.trace_shot(f, soldier.x, soldier.y, world,
                                      dx=evaldx * (-1 if soldier.team == 2 else 1),
                                      max_steps=evalsteps, shooter=soldier)

        # 1) прицельная прямая в цель (гарантированное попадание без препятствий)
        dx = target.x - soldier.x
        dy = target.y - soldier.y
        if abs(dx) > 0.01:
            m = dy / dx
            line_expr = f"({m:.4f})*x"
            shot = shoot(line_expr)
            if shot is not None and shot.hit_soldier is not None and shot.hit_soldier.team == enemy_team:
                return (line_expr, shot)

        # 2) прицельные параболы с разной крутизной (перелетают препятствия)
        x0, y0 = soldier.x, soldier.y
        tx, ty = target.x, target.y
        denom = tx - x0
        if abs(denom) > 0.01:
            m0 = (ty - y0) / denom
            for _ in range(25):
                k = self.rng.uniform(-0.015, 0.015)
                a = m0 - k * denom  # чтобы дуга проходила точно через цель
                expr = f"({a:.5f})*x+({k:.6f})*x**2"
                shot = shoot(expr)
                if shot is not None and shot.hit_soldier is not None and shot.hit_soldier.team == enemy_team:
                    return (expr, shot)

        templates = [
            "a*x+b",
            "a*x**2+b*x+c",
            "a*sin(b*x)+c",
            "a*cos(b*x)+c",
            "a*x**3+b",
            "a*exp(b*x)+c",
            "a*sqrt(abs(x))+b",
        ]
        best = None
        best_score = float("inf")
        for _ in range(25):
            t = self.rng.choice(templates)
            params = {}
            for name in ("a", "b", "c"):
                params[name] = self.rng.uniform(-2.0, 2.0)
            expr = t
            for name in ("a", "b", "c"):
                expr = expr.replace(name, f"({params[name]:.4f})")
            shot = shoot(expr)
            if shot is None:
                continue
            if shot.hit_soldier is not None and shot.hit_soldier.team == enemy_team:
                return (expr, shot)
            score = self._score(shot, target)
            if score < best_score:
                best_score = score
                best = (expr, shot)
        return best

    def _score(self, shot, target):
        if not shot.points:
            return float("inf")
        return min(
            math.hypot(px - target.x, py - target.y) for px, py in shot.points
        )