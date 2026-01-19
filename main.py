import sys
import pygame

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

PLAYER_SIZE = 32
RUN_SPEED = 220
GRAVITY = 1700
JUMP_SPEED = 620
JUMP_BUFFER = 0.16

GROUND_HEIGHT = 80
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

COLORS = {
    "bg": (16, 18, 22),
    "player": (240, 240, 240),
    "platform": (70, 80, 90),
    "spike": (210, 60, 60),
    "goal": (60, 200, 120),
}


def column(x, height, width=60):
    return pygame.Rect(x, GROUND_Y - height, width, height)


def spike(x, width=56, height=22):
    return pygame.Rect(x, GROUND_Y - height, width, height)


def goal(x, height=140, width=80):
    return pygame.Rect(x, GROUND_Y - height, width, height)


def build_levels():
    return [
        {
            "name": "Level 1",
            "width": 2300,
            "start": (60, GROUND_Y - PLAYER_SIZE),
            "ground": pygame.Rect(0, GROUND_Y, 2300, GROUND_HEIGHT),
            "columns": [
                column(560, 80),
                column(1080, 90),
                column(1600, 85),
            ],
            "spikes": [
                spike(300),
                spike(820),
                spike(1340),
                spike(1860),
            ],
            "goal": goal(2100),
        },
        {
            "name": "Level 2",
            "width": 2800,
            "start": (60, GROUND_Y - PLAYER_SIZE),
            "ground": pygame.Rect(0, GROUND_Y, 2800, GROUND_HEIGHT),
            "columns": [
                column(600, 85),
                column(1160, 95),
                column(1720, 80),
                column(2280, 90),
            ],
            "spikes": [
                spike(320),
                spike(900),
                spike(1440),
                spike(2000),
                spike(2520),
            ],
            "goal": goal(2620),
        },
        {
            "name": "Level 3",
            "width": 3300,
            "start": (60, GROUND_Y - PLAYER_SIZE),
            "ground": pygame.Rect(0, GROUND_Y, 3300, GROUND_HEIGHT),
            "columns": [
                column(640, 90),
                column(1240, 80),
                column(1840, 100),
                column(2440, 85),
                column(2920, 95),
            ],
            "spikes": [
                spike(360),
                spike(980),
                spike(1560),
                spike(2160),
                spike(2680),
            ],
            "goal": goal(3140),
        },
    ]


LEVELS = build_levels()


level_index = 0
level_width = 0
platforms = []
columns = []
spikes = []
goal_rect = pygame.Rect(0, 0, 0, 0)
player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
player_x = 0.0
player_y = 0.0
vel_y = 0.0
on_ground = False
camera_x = 0.0
jump_buffer = 0.0
jump_held = False
jump_used = False
state = "play"
win_timer = 0.0


def load_level(index):
    global level_index, level_width, platforms, columns, spikes, goal_rect
    global player_rect, player_x, player_y, vel_y, on_ground, camera_x
    global jump_buffer, jump_held, jump_used, state, win_timer

    level_index = index
    level = LEVELS[level_index]
    level_width = level["width"]
    columns = level["columns"]
    spikes = level["spikes"]
    goal_rect = level["goal"]
    platforms = [level["ground"]] + columns

    player_rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    player_rect.topleft = level["start"]
    player_x = float(player_rect.x)
    player_y = float(player_rect.y)
    vel_y = 0.0
    on_ground = False
    camera_x = 0.0
    jump_buffer = 0.0
    jump_held = False
    jump_used = False
    state = "play"
    win_timer = 0.0
    pygame.display.set_caption(f"Rhythm Cube - {level['name']}")


def main():
    global player_x, player_y, vel_y, on_ground, camera_x, jump_buffer, state
    global win_timer, jump_used, jump_held

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player_image = None
    try:
        player_image = pygame.image.load("cube.png").convert_alpha()
        player_image = pygame.transform.smoothscale(
            player_image,
            (PLAYER_SIZE, PLAYER_SIZE),
        )
    except Exception:
        player_image = None

    load_level(0)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    jump_held = True
                    jump_used = False
                    jump_buffer = JUMP_BUFFER
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    jump_held = False

        if state == "win":
            win_timer -= dt
            if win_timer <= 0:
                next_index = level_index + 1
                if next_index >= len(LEVELS):
                    state = "all_done"
                    pygame.display.set_caption("Rhythm Cube - All Levels Clear")
                else:
                    load_level(next_index)
            continue
        if state == "all_done":
            continue

        if jump_buffer > 0:
            jump_buffer = max(0.0, jump_buffer - dt)
        if jump_held and not jump_used:
            jump_buffer = JUMP_BUFFER

        vel_y += GRAVITY * dt

        player_x += RUN_SPEED * dt
        player_rect.x = int(player_x)

        prev_y = player_y
        player_y += vel_y * dt
        player_rect.y = int(player_y)
        on_ground = False

        for platform in platforms:
            overlap_x = player_rect.right > platform.left and player_rect.left < platform.right
            if overlap_x:
                if vel_y >= 0 and prev_y + PLAYER_SIZE <= platform.top and player_rect.bottom >= platform.top:
                    player_rect.bottom = platform.top
                    player_y = float(player_rect.y)
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0 and prev_y >= platform.bottom and player_rect.top <= platform.bottom:
                    player_rect.top = platform.bottom
                    player_y = float(player_rect.y)
                    vel_y = 0

        if on_ground and jump_buffer > 0 and not jump_used:
            vel_y = -JUMP_SPEED
            jump_buffer = 0.0
            jump_used = True
            on_ground = False

        for s in spikes:
            if player_rect.colliderect(s):
                load_level(level_index)
                break

        if player_rect.colliderect(goal_rect):
            state = "win"
            win_timer = 1.0
            pygame.display.set_caption("Rhythm Cube - Victory!")

        if player_rect.top > SCREEN_HEIGHT + 120 or player_rect.left > level_width + 200:
            load_level(level_index)

        camera_x = player_rect.centerx - SCREEN_WIDTH * 0.35
        if camera_x < 0:
            camera_x = 0.0
        if camera_x > level_width - SCREEN_WIDTH:
            camera_x = float(level_width - SCREEN_WIDTH)

        offset_x = int(camera_x)

        screen.fill(COLORS["bg"])
        for platform in platforms:
            screen_rect = platform.move(-offset_x, 0)
            pygame.draw.rect(screen, COLORS["platform"], screen_rect)

        for s in spikes:
            apex = (s.centerx - offset_x, s.top)
            left = (s.left - offset_x, s.bottom)
            right = (s.right - offset_x, s.bottom)
            pygame.draw.polygon(screen, COLORS["spike"], [left, apex, right])

        pygame.draw.rect(screen, COLORS["goal"], goal_rect.move(-offset_x, 0))
        if player_image:
            screen.blit(player_image, (player_rect.x - offset_x, player_rect.y))
        else:
            pygame.draw.rect(screen, COLORS["player"], player_rect.move(-offset_x, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
