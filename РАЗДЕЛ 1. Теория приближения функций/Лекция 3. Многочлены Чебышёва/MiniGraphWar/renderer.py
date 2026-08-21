import math
import pygame

import config


class Camera:
    def __init__(self, world_w, world_h):
        self.px = (config.SCREEN_W - 2 * config.MARGIN) / world_w
        self.py = (config.SCREEN_H - 2 * config.MARGIN) / world_h
        self.scale = min(self.px, self.py)
        self.ox = config.SCREEN_W // 2
        self.oy = config.SCREEN_H // 2

    def to_screen(self, wx, wy):
        return (self.ox + int(wx * self.scale), self.oy - int(wy * self.scale))


class Renderer:
    def __init__(self, world, camera):
        self.world = world
        self.cam = camera

    def draw(self, surface, game):
        surface.fill(config.BG_COLOR)
        self._draw_grid(surface)
        self._draw_obstacles(surface)
        self._draw_soldiers(surface, game.current_soldier)
        self._draw_preview(surface, game.compute_preview())
        self._draw_shots(surface, game)
        self._draw_hud(surface, game)
        pygame.display.flip()

    def _draw_grid(self, surface):
        cam = self.cam
        w, h = self.world.width, self.world.height
        font = pygame.font.SysFont("consolas", 12)
        # вертикальные линии
        x = -w / 2
        while x <= w / 2:
            sx, sy = cam.to_screen(x, -h / 2)
            ex, ey = cam.to_screen(x, h / 2)
            color = config.GRID_COLOR if abs(x) > 0.001 else config.AXIS_COLOR
            width = 1 if abs(x) > 0.001 else 2
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
            if abs(x) > 0.001:
                label = font.render(f"{x:.0f}", True, (120, 130, 150))
                surface.blit(label, (sx - 10, cam.to_screen(x, h / 2)[1] + 2))
            x += 5
        y = -h / 2
        while y <= h / 2:
            sx, sy = cam.to_screen(-w / 2, y)
            ex, ey = cam.to_screen(w / 2, y)
            color = config.GRID_COLOR if abs(y) > 0.001 else config.AXIS_COLOR
            width = 1 if abs(y) > 0.001 else 2
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
            if abs(y) > 0.001:
                label = font.render(f"{y:.0f}", True, (120, 130, 150))
                surface.blit(label, (cam.to_screen(-w / 2, y)[0] + 3, sy - 8))
            y += 5
        # метка начала координат
        ox, oy = cam.to_screen(0, 0)
        pygame.draw.circle(surface, (255, 255, 255), (ox, oy), 3)
        label = font.render("(0,0)", True, (255, 255, 255))
        surface.blit(label, (ox + 5, oy + 3))

    def _draw_obstacles(self, surface):
        for o in self.world.obstacles:
            sx, sy = self.cam.to_screen(o.x, o.y)
            r = max(4, int(o.r * self.cam.scale))
            pygame.draw.circle(surface, (160, 110, 40), (sx, sy), r)
            pygame.draw.circle(surface, (90, 60, 20), (sx, sy), r, 3)
            # штриховка крестом
            inset = max(2, r // 4)
            pygame.draw.line(surface, (110, 75, 25), (sx - inset, sy - inset), (sx + inset, sy + inset), 2)
            pygame.draw.line(surface, (110, 75, 25), (sx + inset, sy - inset), (sx - inset, sy + inset), 2)

    def _draw_preview(self, surface, shot):
        if shot is None or len(shot.points) < 2:
            return
        pts = [self.cam.to_screen(px, py) for px, py in shot.points]
        pygame.draw.lines(surface, (90, 200, 255), False, pts, 1)
        end = pts[-1]
        pygame.draw.circle(surface, (90, 200, 255), end, 3)

    def _draw_soldiers(self, surface, current=None):
        for s in self.world.soldiers:
            sx, sy = self.cam.to_screen(s.x, s.y)
            color = config.TEAM1_COLOR if s.team == 1 else config.TEAM2_COLOR
            if s.alive:
                pygame.draw.circle(surface, color, (sx, sy), 8)
                pygame.draw.circle(surface, (0, 0, 0), (sx, sy), 8, 2)
                pygame.draw.circle(surface, (255, 255, 255), (sx - 3, sy - 3), 2)
            else:
                pygame.draw.line(surface, (80, 80, 80), (sx - 7, sy - 7), (sx + 7, sy + 7), 3)
                pygame.draw.line(surface, (80, 80, 80), (sx + 7, sy - 7), (sx - 7, sy + 7), 3)
        if current is not None and current.alive:
            sx, sy = self.cam.to_screen(current.x, current.y)
            color = config.TEAM1_COLOR if current.team == 1 else config.TEAM2_COLOR
            pygame.draw.circle(surface, color, (sx, sy), 12, 3)

    def _draw_shots(self, surface, game):
        for shot in game.active_shots:
            pts = [self.cam.to_screen(px, py) for px, py in shot.points]
            if len(pts) > 1:
                pygame.draw.lines(surface, config.TRAJECTORY_COLOR, False, pts, 2)
            if shot.hit_soldier is not None:
                self._draw_boom(surface, shot.hit_soldier.x, shot.hit_soldier.y)
            elif shot.exploded_at is not None:
                self._draw_boom(surface, shot.exploded_at[0], shot.exploded_at[1])

    def _draw_boom(self, surface, wx, wy):
        sx, sy = self.cam.to_screen(wx, wy)
        for i, r in enumerate([8, 16, 26]):
            color = (255, int(200 - i * 50), 0)
            pygame.draw.circle(surface, color, (sx, sy), r, 2)

    def _draw_hud(self, surface, game):
        font = pygame.font.SysFont("consolas", 20)
        font_small = pygame.font.SysFont("consolas", 16)
        team1 = len(self.world.alive(1))
        team2 = len(self.world.alive(2))
        if game.timer_enabled:
            timer_txt = f"{game.time_left:.1f}"
        else:
            timer_txt = "без таймера"
        hud = f"Игрок: {team1}    ИИ: {team2}    Ход: {timer_txt}"
        surface.blit(font.render(hud, True, (255, 255, 255)), (10, 10))

        if game.state == "input":
            label = font.render(f"Ход команды {'Синие' if game.current_team == 1 else 'Красные'}", True,
                                config.TEAM1_COLOR if game.current_team == 1 else config.TEAM2_COLOR)
            surface.blit(label, (10, 40))
            if game.current_soldier is not None:
                cs = game.current_soldier
                pos = font_small.render(f"Твой солдат: x={cs.x:.1f}, y={cs.y:.1f} (x в функции — смещение от солдата)",
                                        True, (160, 200, 255))
                surface.blit(pos, (10, 132))
            box = pygame.Rect(10, 70, 500, 34)
            pygame.draw.rect(surface, (30, 34, 44), box)
            pygame.draw.rect(surface, (200, 200, 200), box, 2)
            txt = font.render(game.input_text, True, (255, 255, 255))
            surface.blit(txt, (box.x + 6, box.y + 6))
            cx = box.x + 6 + font.size(game.input_text[:game.cursor])[0]
            pygame.draw.line(surface, (255, 255, 255), (cx, box.y + 5), (cx, box.y + box.h - 5), 2)
            hint = font_small.render("Enter — выстрел, ←→ — курсор, ↑↓ — солдат, Esc — сброс", True, (150, 150, 150))
            surface.blit(hint, (10, 110))
        elif game.state == "game_over":
            txt = "ПОБЕДА!" if game.winner == 1 else "ПОРАЖЕНИЕ"
            surf = font.render(txt, True, (255, 255, 255))
            r = surf.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2 - 20))
            surface.blit(surf, r)
            hint = font_small.render("Enter — заново, Esc — в меню уровней", True, (200, 200, 200))
            r = hint.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2 + 20))
            surface.blit(hint, r)