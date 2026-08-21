import random
import time

import pygame

import config
from mathparser import compile_function, MathParseError
import physics
from renderer import Camera, Renderer
from world import World
from ai import AI


class Game:
    def __init__(self, level, ai_enabled=True, timer_enabled=config.TIMER_ENABLED):
        self._level = level
        self.ai_enabled = ai_enabled
        self.timer_enabled = timer_enabled
        self.world = World.from_level(level, seed=random.randrange(10**9))
        self.camera = Camera(self.world.width, self.world.height)
        self.renderer = Renderer(self.world, self.camera)
        self.ai = AI(random.Random()) if ai_enabled else None
        self.ai_enabled = ai_enabled

        self.current_team = 1
        self.current_soldier = self.world.alive(1)[0] if self.world.alive(1) else None
        self.soldier_index = 0
        self.time_left = config.TURN_TIME
        self.turn_start = time.monotonic()
        self.input_text = ""
        self.cursor = 0
        self.active_shots = []
        self.state = "input"
        self.winner = None
        self._preview = None
        self._preview_key = None
        self._preview_expr = None

        # двигаем курсор: всегда стреляем "вперёд" (влево для команды 1, вправо для 2)
        self.direction = 1

    def update(self, dt):
        if self.state == "input":
            if self.timer_enabled:
                self.time_left = config.TURN_TIME - (time.monotonic() - self.turn_start)
                if self.time_left <= 0:
                    self._end_turn()
                    return
            if self.current_team == 2 and self.ai_enabled:
                # ИИ думает мгновенно, небольшой эффект задержки
                self._do_ai_shot()

    def compute_preview(self):
        """Возвращает траекторию для текущего ввода (None, если нельзя)."""
        if self.state != "input":
            return None
        if self.current_team == 2 and self.ai_enabled:
            return None
        text = self.input_text.strip()
        soldier = self.current_soldier
        if not text or soldier is None:
            return None
        key = (text, id(soldier), self._preview_key)
        if self._preview is not None and self._preview_expr == text:
            return self._preview
        try:
            f = compile_function(text)
        except MathParseError:
            return None
        dir_sign = -1 if self.current_team == 2 else 1
        shot = physics.trace_shot(f, soldier.x, soldier.y, self.world, dx=config.DX * dir_sign, shooter=soldier)
        self._preview = shot
        self._preview_expr = text
        return shot

    def _do_ai_shot(self):
        soldier = self.current_soldier
        if soldier is None:
            return
        res = self.ai.choose_shot(soldier, self.world)
        if res is None:
            self._end_turn()
            return
        expr, shot = res
        self.input_text = expr
        self.active_shots = [shot]
        if shot.hit_soldier is not None and shot.hit_soldier.team == 1:
            shot.hit_soldier.alive = False
        self._end_turn()

    def handle_event(self, event):
        if self.state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.__init__(self._level, self.ai_enabled, self.timer_enabled)
            return
        if self.state != "input":
            return
        if self.current_team == 2 and self.ai_enabled:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._fire()
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor > 0:
                    self.input_text = self.input_text[:self.cursor - 1] + self.input_text[self.cursor:]
                    self.cursor -= 1
                    self._preview_key = None
            elif event.key == pygame.K_DELETE:
                if self.cursor < len(self.input_text):
                    self.input_text = self.input_text[:self.cursor] + self.input_text[self.cursor + 1:]
                    self._preview_key = None
            elif event.key == pygame.K_LEFT:
                if self.cursor > 0:
                    self.cursor -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor < len(self.input_text):
                    self.cursor += 1
            elif event.key == pygame.K_HOME:
                self.cursor = 0
            elif event.key == pygame.K_END:
                self.cursor = len(self.input_text)
            elif event.key == pygame.K_ESCAPE:
                self.input_text = ""
                self.cursor = 0
                self._preview_key = None
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self._switch_soldier()
            else:
                ch = event.unicode
                if ch and ch.isprintable():
                    self.input_text = self.input_text[:self.cursor] + ch + self.input_text[self.cursor:]
                    self.cursor += 1
                    self._preview_key = None

    def _switch_soldier(self):
        alive = self.world.alive(self.current_team)
        if not alive:
            return
        idx = alive.index(self.current_soldier)
        self.current_soldier = alive[(idx + 1) % len(alive)]
        self._preview = None
        self._preview_key = None

    def _fire(self):
        soldier = self.current_soldier
        if soldier is None:
            return
        self._preview = None
        self._preview_key = None
        try:
            f = compile_function(self.input_text)
        except MathParseError as e:
            print(f"[ошибка] {e}")
            self.input_text = ""
            return
        # направление: в сторону противника (синие слева -> вправо, красные справа -> влево)
        dir_sign = -1 if self.current_team == 2 else 1
        shot = physics.trace_shot(f, soldier.x, soldier.y, self.world, dx=config.DX * dir_sign, shooter=soldier)
        self.active_shots = [shot]
        if shot.hit_soldier is not None:
            shot.hit_soldier.alive = False
            print(f"[попадание] солдат команды {shot.hit_soldier.team} уничтожен")
        elif shot.exploded_at is not None:
            print("[взрыв] траектория прервана")
        self._end_turn()

    def _end_turn(self):
        # проверка победы
        alive1 = len(self.world.alive(1))
        alive2 = len(self.world.alive(2))
        if alive1 == 0 or alive2 == 0:
            self.winner = 1 if alive1 > 0 else 2
            self.state = "game_over"
            return
        self.current_team = 2 if self.current_team == 1 else 1
        alive = self.world.alive(self.current_team)
        if not alive:
            self.winner = 1 if self.current_team == 2 else 2
            self.state = "game_over"
            return
        idx = getattr(self, "soldier_index", 0)
        self.soldier_index = (idx + 1) % len(alive)
        self.current_soldier = alive[self.soldier_index]
        self.input_text = ""
        self.cursor = 0
        self.active_shots = []
        self.time_left = config.TURN_TIME
        self.turn_start = time.monotonic()
        self.state = "input"

    def draw(self, surface):
        self.renderer.draw(surface, self)