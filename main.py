import arcade

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

LEVEL_WIDTH = 2300

PLAYER_SIZE = 32
RUN_SPEED = 220
GRAVITY = -1700
JUMP_SPEED = 620

GROUND_HEIGHT = 80

COLORS = {
    "bg": (16, 18, 22),
    "player": (240, 240, 240),
    "platform": (70, 80, 90),
    "spike": (210, 60, 60),
    "goal": (60, 200, 120),
}


def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


class RhythmCube(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Rhythm Cube")
        self.set_update_rate(1 / FPS)
        arcade.set_background_color(COLORS["bg"])
        try:
            self.player_texture = arcade.load_texture("cube.png")
        except Exception:
            self.player_texture = None
        self.reset()

    def reset(self):
        self.player_x = 60.0
        self.player_y = float(GROUND_HEIGHT)
        self.vel_y = 0.0
        self.on_ground = True
        self.win = False
        self.level_width = LEVEL_WIDTH
        self.camera_x = 0.0
        self.spikes = [300, 820, 1340, 1860]
        self.spike_width = 56
        self.spike_height = 22
        self.columns = [
            (560, 80),
            (1080, 90),
            (1600, 85),
        ]
        self.column_width = 60
        self.goal = (2100, GROUND_HEIGHT, 80, 140)
        self.set_caption("Rhythm Cube")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.SPACE, arcade.key.UP) and self.on_ground and not self.win:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

    def on_update(self, delta_time):
        if self.win:
            return

        dt = delta_time
        self.vel_y += GRAVITY * dt
        self.player_x += RUN_SPEED * dt
        prev_y = self.player_y
        self.player_y += self.vel_y * dt
        self.on_ground = False

        if self.vel_y <= 0:
            for cx, ch in self.columns:
                col_top = GROUND_HEIGHT + ch
                if (
                    self.player_x + PLAYER_SIZE > cx
                    and self.player_x < cx + self.column_width
                    and prev_y >= col_top
                    and self.player_y <= col_top
                ):
                    self.player_y = float(col_top)
                    self.vel_y = 0.0
                    self.on_ground = True
                    break

        if not self.on_ground and self.player_y <= GROUND_HEIGHT:
            self.player_y = float(GROUND_HEIGHT)
            self.vel_y = 0.0
            self.on_ground = True

        px = self.player_x
        py = self.player_y
        pw = PLAYER_SIZE
        ph = PLAYER_SIZE

        for sx in self.spikes:
            if rects_overlap(
                px,
                py,
                pw,
                ph,
                sx,
                GROUND_HEIGHT,
                self.spike_width,
                self.spike_height,
            ):
                self.reset()
                return

        gx, gy, gw, gh = self.goal
        if rects_overlap(px, py, pw, ph, gx, gy, gw, gh):
            self.win = True
            self.set_caption("Rhythm Cube - Victory!")

        if px > self.level_width + 200:
            self.reset()
            return

        self.camera_x = self.player_x - SCREEN_WIDTH * 0.35
        if self.camera_x < 0:
            self.camera_x = 0.0
        max_x = self.level_width - SCREEN_WIDTH
        if self.camera_x > max_x:
            self.camera_x = float(max_x)

    def on_draw(self):
        if hasattr(self, "clear"):
            self.clear()
        else:
            arcade.start_render()

        offset_x = int(self.camera_x)

        arcade.draw_lrbt_rectangle_filled(
            0 - offset_x,
            self.level_width - offset_x,
            0,
            GROUND_HEIGHT,
            COLORS["platform"],
        )

        for sx in self.spikes:
            left = (sx - offset_x, GROUND_HEIGHT)
            right = (sx + self.spike_width - offset_x, GROUND_HEIGHT)
            apex = (
                sx + self.spike_width / 2.0 - offset_x,
                GROUND_HEIGHT + self.spike_height,
            )
            arcade.draw_polygon_filled([left, apex, right], COLORS["spike"])

        for cx, ch in self.columns:
            arcade.draw_lrbt_rectangle_filled(
                cx - offset_x,
                cx + self.column_width - offset_x,
                GROUND_HEIGHT,
                GROUND_HEIGHT + ch,
                COLORS["platform"],
            )

        gx, gy, gw, gh = self.goal
        arcade.draw_lrbt_rectangle_filled(
            gx - offset_x,
            gx + gw - offset_x,
            gy,
            gy + gh,
            COLORS["goal"],
        )

        if self.player_texture:
            arcade.draw_texture_rectangle(
                self.player_x + PLAYER_SIZE / 2.0 - offset_x,
                self.player_y + PLAYER_SIZE / 2.0,
                PLAYER_SIZE,
                PLAYER_SIZE,
                self.player_texture,
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                self.player_x - offset_x,
                self.player_x + PLAYER_SIZE - offset_x,
                self.player_y,
                self.player_y + PLAYER_SIZE,
                COLORS["player"],
            )

        if self.win:
            arcade.draw_text(
                "WIN",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                COLORS["player"],
                24,
                anchor_x="center",
                anchor_y="center",
            )


def main():
    RhythmCube()
    arcade.run()


if __name__ == "__main__":
    main()
