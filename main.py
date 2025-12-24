import arcade


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 960
# Физика и движение
GRAVITY = 2  # Пикс/с^2
MOVE_SPEED = 6  # Пикс/с
JUMP_SPEED = 40  # Начальный импульс прыжка, пикс/с
# Качество жизни прыжка
COYOTE_TIME = 0.08  # Сколько после схода с платформы можно ещё прыгнуть
JUMP_BUFFER = 0.12  # Если нажали прыжок чуть раньше приземления, мы его «запомним» (тоже лайфхак для улучшения качества жизни игрока)
MAX_JUMPS = 1  # С двойным прыжком всё лучше, но не сегодня
SCREEN_TITLE = "Real Jump"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        # Спрайт игрока
        self.player = arcade.Sprite(
            "Новый проект.png", scale=0.5)
        self.player.center_x = 50
        self.player.center_y = 50
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.tile_map = arcade.load_tilemap("testmap.json",
                                            scaling=0.5)  # Во встроенных ресурсах есть даже уровни!
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Ввод
        self.left = self.right = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.scene['platform']
        )

    def on_draw(self):
        self.clear()
        self.player_spritelist.draw()
        self.scene.draw()

    def on_update(self, delta_time):
        # Гравитация (если хочешь)
        self.player.change_y -= GRAVITY

        # Обработка горизонтального движения
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
        self.player.change_x = move

        # Прыжок: can_jump() + койот + буфер
        grounded = self.engine.can_jump(y_distance=6)  # Есть пол под ногами?
        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
        else:
            self.time_since_ground += delta_time

        # Учтём «запомненный» пробел
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= delta_time
        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        # Можно прыгать, если стоим на земле или в пределах койот-времени;
        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                # Просим движок прыгнуть: он корректно задаст начальную вертикальную скорость
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.45


def setup_game(width=960, height=640, title="Real Jump"):
    game = MyGame(width, height, title)
    game.setup()
    return game

def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()