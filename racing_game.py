#!/usr/bin/env python3
"""简单赛车游戏（基于 pygame 的最小实现）

玩法：用左右方向键控制赛车在道路上移动，避免从屏幕上方掉落的障碍物。
得分基于行驶距离，难度随得分逐步增加。
"""

import sys
import random
import os

import pygame

# Debugging helpers
DEBUG_MODE = os.environ.get("RACING_DEBUG", "0") == "1" or os.environ.get("RACING_SAFE", "0") == "1"
LOG_FILE = os.path.join(os.path.dirname(__file__), "racing_debug.log")

def log(msg, level="INFO"):
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} [{level}] {msg}"
        print(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # 不让日志失败干扰游戏运行
        pass

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


def load_car_image(target_w, target_h):
    """尝试从 cars/ 目录加载一张汽车图片，尺寸缩放到目标宽高。"""
    dir_path = os.path.join(os.path.dirname(__file__), 'cars')
    if not os.path.isdir(dir_path):
        return None
    candidates = []
    for fname in sorted(os.listdir(dir_path)):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            candidates.append(os.path.join(dir_path, fname))
    for path in candidates:
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (target_w, target_h))
            return img
        except Exception:
            continue
    return None


def load_font(size):
    # 优先尝试加载常见的中文字体以避免中文显示为乱码
    font_candidates = [
        r"C:\Windows\Fonts\msyh.ttf",        # Microsoft YaHei
        r"C:\Windows\Fonts\msyhbd.ttf",      # Microsoft YaHei Bold
        r"C:\Windows\Fonts\simsun.ttc",      # SimSun (Song)
        r"C:\Windows\Fonts\simsun.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux common
        "/Library/Fonts/Arial Unicode.ttf",     # macOS fallback
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                continue
    # 最后用系统字体进行回退
    try:
        return pygame.font.SysFont("Microsoft YaHei", size)
    except Exception:
        try:
            return pygame.font.SysFont("Arial", size)
        except Exception:
            return pygame.font.Font(None, size)

def load_player_car_image(target_w, target_h):
    """加载 pitstop_car_1.* 作为玩家的赛车图片，失败则返回 None"""
    dir_path = os.path.join(os.path.dirname(__file__), 'cars')
    if not os.path.isdir(dir_path):
        return None
    # 只关注 pitstop_car_1 命名的图片
    candidates = []
    for fname in sorted(os.listdir(dir_path)):
        if fname.lower().startswith('pitstop_car_1') and fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            candidates.append(os.path.join(dir_path, fname))
    for path in candidates:
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (target_w, target_h))
            return img
        except Exception:
            continue
    return None

def load_racer_images(target_w=60, target_h=90):
    """Load rival cars images from cars/ and scale to target width while preserving aspect ratio.
    Returns a list of dicts: {'image': Surface, 'w': int, 'h': int}.
    Note: the width will be clamped to target_w and height is computed to preserve aspect ratio.
    """
    dir_path = os.path.join(os.path.dirname(__file__), 'cars')
    racers = []
    if not os.path.isdir(dir_path):
        return racers
    items = []
    for fname in sorted(os.listdir(dir_path)):
        if fname.lower().startswith('pitstop_car_') and fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            import re
            m = re.match(r"pitstop_car_(\d+)", fname[:-4], re.IGNORECASE)
            idx = int(m.group(1)) if m else 0
            items.append((idx, fname))
    items.sort()
    for idx, fname in items:
        path = os.path.join(dir_path, fname)
        try:
            img = pygame.image.load(path).convert_alpha()
            orig_w, orig_h = img.get_size()
            if orig_w <= 0 or orig_h <= 0:
                continue
            # Force exact player size for opponent cars
            new_w, new_h = int(target_w), int(target_h)
            img = pygame.transform.scale(img, (new_w, new_h))
            racers.append({'image': img, 'w': new_w, 'h': new_h})
        except Exception:
            continue
    return racers
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

    # 使用字体加载函数，优先显示中文字体
    font = load_font(36)
    
    # 车道参数
    ROAD_WIDTH = 420
    ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
    ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH

    # 玩家小车参数
    CAR_WIDTH, CAR_HEIGHT = 40, 60
    car_x = WIDTH // 2 - CAR_WIDTH // 2
    car_y = HEIGHT - CAR_HEIGHT - 50
    car_speed = 7
    
    # Load player and rival car images after defining dimensions
    SAFE_MODE = os.environ.get("RACING_SAFE", "0") == "1"
    if SAFE_MODE:
        player_car_image = None
        rival_images = []
    else:
        player_car_image = load_player_car_image(CAR_WIDTH, CAR_HEIGHT)
        rival_images = load_racer_images(CAR_WIDTH, CAR_HEIGHT)
    log(f"Loaded assets: player={bool(player_car_image)}, rivals={len(rival_images)}", "DEBUG")
    log(f"SAFE_MODE={SAFE_MODE}, player_car_image={'OK' if player_car_image else 'NONE'}, rival_images={len(rival_images)}", "DEBUG")
    # 初始化对手赛车集合
    opponents = []
    opponent_spawn_timer = 0.0
    opponent_spawn_interval = 0.9

    # 障碍物数据结构：{x, y, w, h, color}
    obstacles = []
    spawn_timer = 0.0
    spawn_interval = 0.9  # 初始生成间隔（秒）

    distance = 0.0
    level = 0
    running = True
    game_over = False

    frame_count = 0
    # Motion illusion for center dashed line
    CENTER_LINE_SPEED = 240.0  # px per second
    DASH_H = 20
    DASH_GAP = 20
    DASH_CYCLE = DASH_H + DASH_GAP
    road_line_offset = 0.0
    while True:
        dt = clock.tick(60) / 1000.0  # seconds elapsed this frame
        frame_count += 1
        # 每帧调试信息（限制输出，避免过于冗长）
        if DEBUG_MODE:
            log(f"Frame start dt={dt:.4f} frame_count={frame_count}")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # 重启游戏
                        obstacles.clear()
                        opponents.clear()
                        car_x = WIDTH // 2 - CAR_WIDTH // 2
                        car_y = HEIGHT - CAR_HEIGHT - 50
                        distance = 0.0
                        level = 0
                        spawn_timer = 0.0
                        road_line_offset = 0.0
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
                if rival_images:
                    img = random.choice(rival_images)
                    w, h = img['w'], img['h']
                    x = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - w - 10)
                    y = -h
                    opponents.append({"image": img['image'], "x": x, "y": y, "w": w, "h": h, "speed": obstacle_speed * (0.9 + random.uniform(0, 0.4))})
                    if DEBUG_MODE:
                        log(f"Spawn rival: x={x}, y={y}, w={w}, h={h}, speed={opponents[-1]['speed']:.2f}", "DEBUG")
                else:
                    w = random.randint(40, 90)
                    h = random.randint(20, 60)
                    x = random.randint(ROAD_LEFT + 10, ROAD_RIGHT - w - 10)
                    y = -h
                    obstacles.append({"x": x, "y": y, "w": w, "h": h, "color": (255, 0, 0)})
                    if DEBUG_MODE:
                        log(f"Spawn obstacle: x={x}, y={y}, w={w}, h={h}", "DEBUG")
                spawn_timer = 0.0
                # 让后续生成更紧凑一点，随着等级提升
                spawn_interval = max(0.6, 0.9 - level * 0.02)

            # 移动障碍物
            for o in obstacles:
                o["y"] += obstacle_speed
            obstacles = [o for o in obstacles if o["y"] < HEIGHT + o["h"]]
            # 移动对手赛车
            for opp in opponents:
                opp["y"] += opp["speed"]
            opponents = [opp for opp in opponents if opp["y"] < HEIGHT + opp["h"]]

            # 距离/分数更新
            distance += obstacle_speed * dt * 10

            # 碰撞检测（玩家与障碍物）
            car_rect = pygame.Rect(car_x, car_y, CAR_WIDTH, CAR_HEIGHT)
            for o in obstacles:
                obs_rect = pygame.Rect(o["x"], o["y"], o["w"], o["h"])
                if car_rect.colliderect(obs_rect):
                    game_over = True
                    if DEBUG_MODE:
                        log(f"Collision: player with obstacle at ({o['x']},{o['y']}) size ({o['w']},{o['h']})", "DEBUG")
                    break
            # 碰撞检测（玩家与对手赛车）
            for opp in opponents:
                opp_rect = pygame.Rect(opp["x"], opp["y"], opp["w"], opp["h"])
                if car_rect.colliderect(opp_rect):
                    game_over = True
                    if DEBUG_MODE:
                        log(f"Collision: player with rival at ({opp['x']},{opp['y']}) size ({opp['w']},{opp['h']})", "DEBUG")
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
        # moving center line to simulate forward motion (forward/downward)
        if not game_over:
            road_line_offset = (road_line_offset + CENTER_LINE_SPEED * dt) % DASH_CYCLE
        # Draw multiple dashes with an offset to create the illusion of motion
        for y in range(-DASH_H, HEIGHT, DASH_CYCLE):
            pos = int(y + road_line_offset)
            if 0 <= pos <= HEIGHT:
                pygame.draw.rect(screen, (255, 255, 255), (center_x - 2, pos, 4, DASH_H))
        # 绘制更美观的小车外观（如无图片则回退到绘制）
        if player_car_image is not None:
            screen.blit(player_car_image, (car_x, car_y))
        else:
            draw_car(screen, car_x, car_y, CAR_WIDTH, CAR_HEIGHT)

        # 绘制障碍物
        for o in obstacles:
            pygame.draw.rect(screen, o["color"], (o["x"], o["y"], o["w"], o["h"]))
        # 绘制对手赛车
        for opp in opponents:
            if opp.get('image') is not None:
                screen.blit(opp['image'], (opp['x'], opp['y']))
            else:
                pygame.draw.rect(screen, (200, 0, 0), (opp["x"], opp["y"], opp["w"], opp["h"]))

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
