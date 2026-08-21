import sys

import pygame

import config
from game import Game
from levels import LEVELS, load_custom_levels


def draw_menu(surface, levels, selected, ai_enabled, timer_enabled):
    surface.fill(config.BG_COLOR)
    font = pygame.font.SysFont("consolas", 34)
    font_small = pygame.font.SysFont("consolas", 22)
    font_tiny = pygame.font.SysFont("consolas", 16)

    title = font.render("MiniGraphWar", True, config.TRAJECTORY_COLOR)
    surface.blit(title, title.get_rect(center=(config.SCREEN_W // 2, 50)))

    hint = font_small.render("↑ ↓ — уровень, Enter — играть, E — ИИ вкл/выкл, T — таймер вкл/выкл", True, (170, 170, 170))
    surface.blit(hint, hint.get_rect(center=(config.SCREEN_W // 2, 100)))

    y = 150
    for i, lvl in enumerate(levels):
        color = (255, 255, 255) if i == selected else (130, 130, 130)
        marker = ">" if i == selected else " "
        name = lvl["name"]
        o = len(lvl.get("obstacles", []))
        t1 = len(lvl.get("team1", []))
        t2 = len(lvl.get("team2", []))
        txt = f"{marker} {name}    [преград: {o}   синих: {t1}   красных: {t2}]"
        surf = font_small.render(txt, True, color)
        surface.blit(surf, (config.SCREEN_W // 2 - 240, y))
        y += 40

    ai_mode = "ВКЛ" if ai_enabled else "ВЫКЛ"
    timer_mode = "ВКЛ" if timer_enabled else "ВЫКЛ"
    mode = font_small.render(f"ИИ: {ai_mode}    Таймер: {timer_mode}", True, (200, 200, 200))
    surface.blit(mode, mode.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H - 90)))

    surface.blit(font_tiny.render(config.FUNCS_HELP, True, (120, 130, 150)),
                 (config.SCREEN_W // 2 - 300, config.SCREEN_H - 60))
    surface.blit(font_tiny.render(config.CONSTS_HELP, True, (120, 130, 150)),
                 (config.SCREEN_W // 2 - 300, config.SCREEN_H - 40))
    surface.blit(font_tiny.render(config.EXAMPLES_HELP, True, (120, 130, 150)),
                 (config.SCREEN_W // 2 - 300, config.SCREEN_H - 20))

    pygame.display.flip()


def run():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
    pygame.display.set_caption("MiniGraphWar")
    clock = pygame.time.Clock()

    levels = LEVELS + load_custom_levels()
    if not levels:
        print("Нет уровней!")
        return
    selected = 0
    ai_enabled = True
    timer_enabled = config.TIMER_ENABLED

    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(levels)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(levels)
                elif event.key == pygame.K_e:
                    ai_enabled = not ai_enabled
                elif event.key == pygame.K_t:
                    timer_enabled = not timer_enabled
                elif event.key == pygame.K_RETURN:
                    menu = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        draw_menu(screen, levels, selected, ai_enabled, timer_enabled)
        clock.tick(30)

    game = Game(levels[selected], ai_enabled=ai_enabled, timer_enabled=timer_enabled)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
                # возврат в меню
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if game.state == "input":
                        pass  # Esc в игре сбрасывает ввод
                    elif game.state == "game_over":
                        game = Game(levels[selected], ai_enabled=ai_enabled, timer_enabled=timer_enabled)
                    else:
                        running = False
                        menu = True
        game.update(dt)
        game.draw(screen)

    pygame.quit()


if __name__ == "__main__":
    run()