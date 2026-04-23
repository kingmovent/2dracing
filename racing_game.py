#!/usr/bin/env python3
"""简单赛车游戏（基于 pygame 的最小实现）

玩法：用左右方向键控制赛车在道路上移动，避免从屏幕上方掉落的障碍物。
得分基于行驶距离，难度随得分逐步增加。
"""

import sys
import random
import os

import pygame

def draw_car(surface, x, y, w, h):
    # 车身
    body_color = (30, 144, 255)  # dodger blue
    pygame.draw.rect(surface, body_color, (int(x), int(y + h * 0.25), int(w), int(h * 0.75)), border_radius=8)
    # 车顶/玻璃
    roof = [
        (int(x + w * 0.15), int(y + h * 0.25)),
        (int(x + w * 0.35), int(y - h * 0.05)),
        (int(x + w * 0.65), int(y - h * 0.05)),
        (int(x + w * 0.85), int(y + h * 0.25)),
    ]
    pygame.draw.polygon(surface, body_color, roof)
    # 车窗（浅蓝）
    pygame.draw.polygon(surface, (200, 230, 255), [
        (int(x + w * 0.18), int(y + h * 0.25)),
        (int(x + w * 0.32), int(y - h * 0.05)),
        (int(x + w * 0.68), int(y - h * 0.05)),
        (int(x + w * 0.82), int(y + h * 0.25)),
    ])
    # 轮毂（黑色）
    wheel_r = max(3, int(h * 0.18))
    pygame.draw.circle(surface, (20, 20, 20), (int(x + w * 0.25), int(y + h * 0.92)), wheel_r)
    pygame.draw.circle(surface, (20, 20, 20), (int(x + w * 0.75), int(y + h * 0.92)), wheel_r)


def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    # 尝试创建窗口，如在无显示环境下回退到 dummy 驱动以方便调试
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    except pygame.error:
        os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        pygame.display.quit()
        pygame.display.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("简单赛车游戏")
    clock = pygame.time.Clock()

    # 使用更稳健的字体初始化，避免在某些环境中 SysFont(None, ...) 触发异常
    try:
    font = pygame.font.SysFont("Arial", 36)
    except Exception:
        font = pygame.font.Font(None, 36)

    # 车道参数
    ROAD_WIDTH = 420
    ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
    ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH

    # 玩家小车参数
    CAR_WIDTH, CAR_HEIGHT = 40, 60
    car_x = WIDTH // 2 - CAR_WIDTH // 2
    car_y = HEIGHT - CAR_HEIGHT - 50
    car_speed = 7

    # 障碍物数据结构：{x, y, w, h, color}
    obstacles = []
    spawn_timer = 0.0
    spawn_interval = 0.9  # 初始生成间隔（秒）

    distance = 0.0
    level = 0
    running = True
    game_over = False

    while True:
        dt = clock.tick(60) / 1000.0  # seconds elapsed this frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # 重启游戏
                        obstacles.clear()
                        car_x = WIDTH // 2 - CAR_WIDTH // 2
                        car_y = HEIGHT - CAR_HEIGHT - 50
                        distance = 0.0
                        level = 0
                        spawn_timer = 0.0
                        game_over = False
                        spawn_interval = 0.9
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if not game_over:
            # 控制小车移动，确保在车道内
            if keys[pygame.K_LEFT] and car_x > ROAD_LEFT + 10:
                car_x -= car_speed
            if keys[pygame.K_RIGHT] and car_x < ROAD_RIGHT - CAR_WIDTH - 10:
                car_x += car_speed

            # 生成障碍物
            spawn_timer += dt
            level = int(distance // 100)
            obstacle_speed = 5 + min(20, level * 0.5)
            if spawn_timer >= spawn_interval:
                w = random.randint(40, 90)
                h = random.randint(20, 60)
                x = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - w - 10)
                y = -h
                obstacles.append({"x": x, "y": y, "w": w, "h": h, "color": (255, 0, 0)})
                spawn_timer = 0.0
                # 让后续生成更紧凑一点，随着等级提升
                spawn_interval = max(0.6, 0.9 - level * 0.02)

            # 移动障碍物
            for o in obstacles:
                o["y"] += obstacle_speed
            obstacles = [o for o in obstacles if o["y"] < HEIGHT + o["h"]]

            # 距离/分数更新
            distance += obstacle_speed * dt * 10

            # 碰撞检测
            car_rect = pygame.Rect(car_x, car_y, CAR_WIDTH, CAR_HEIGHT)
            for o in obstacles:
                obs_rect = pygame.Rect(o["x"], o["y"], o["w"], o["h"])
                if car_rect.colliderect(obs_rect):
                    game_over = True
                    break

        # 绘制场景
        screen.fill((0, 0, 0))

        # 车道（左/右边界与中线）
        pygame.draw.rect(screen, (50, 50, 50), (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (ROAD_LEFT, 0, 6, HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (ROAD_RIGHT - 6, 0, 6, HEIGHT))
        # 中线虚线
        center_x = WIDTH // 2
        dash_h = 20
        dash_gap = 20
        for y in range(0, HEIGHT, dash_h + dash_gap):
            pygame.draw.rect(screen, (255, 255, 255), (center_x - 2, y, 4, dash_h))

        # 绘制更美观的小车外观
        draw_car(screen, car_x, car_y, CAR_WIDTH, CAR_HEIGHT)

        # 绘制障碍物
        for o in obstacles:
            pygame.draw.rect(screen, o["color"], (o["x"], o["y"], o["w"], o["h"]))

        # HUD
        dist_text = font.render(f"距离: {int(distance)}", True, (255, 255, 255))
        screen.blit(dist_text, (10, 10))
        lvl_text = font.render(f"等级: {level}", True, (255, 255, 255))
        screen.blit(lvl_text, (10, 44))

        if game_over:
            over_text = font.render("游戏结束！按 R 重启，Q 退出", True, (255, 0, 0))
            rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(over_text, rect)

        pygame.display.flip()


if __name__ == "__main__":
    main()
