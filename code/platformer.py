import arcade
import menu


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
# Физика и движение
GRAVITY = 0.1  # Пикс/с^2
MOVE_SPEED = 9  # Пикс/с
JUMP_SPEED = 8  # Начальный импульс прыжка, пикс/с
ROTATION_SPEED = 9 # Скорость вращения шара
# Качество жизни прыжка
COYOTE_TIME = 0.08  # Сколько после схода с платформы можно ещё прыгнуть
JUMP_BUFFER = 0.12  # Если нажали прыжок чуть раньше приземления, мы его «запомним» (тоже лайфхак для улучшения качества жизни игрока)
MAX_JUMPS = 1
SCREEN_TITLE = "Just A Jumper"


class MyGame(arcade.View):
    def __init__(self, level="materials/level1.json"):
        super().__init__()
        if 'level2' in level:
            arcade.set_background_color(arcade.color.BLACK)
        else:
            arcade.set_background_color(arcade.color.ASH_GREY)
        self.level = level
        self.darkness_alpha = 0
        self.is_darkening = False
        self.is_lightening = False
        self.darkness_speed = 100
        self.lightening_speed = 0.5
        
        # Инициализируем player здесь, чтобы он был доступен во всех методах
        self.player = None
        self.setup()  # Вызываем setup сразу после инициализации

    def setup(self):
        # Спрайт игрока
        self.player = arcade.Sprite(
            "materials/character_test.png", scale=2)
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()

        self.tile_map = arcade.load_tilemap(self.level,
                                            scaling=2)  # Во встроенных ресурсах есть даже уровни!
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.orbs = self.tile_map.sprite_lists['orbs']
        self.jumppads = self.tile_map.sprite_lists['jumppads']
        self.danger = self.tile_map.sprite_lists['danger']
        self.end = self.tile_map.sprite_lists['end']
        self.spawn_x = self.tile_map.sprite_lists['spawn']._get_center()[0]
        self.spawn_y = self.tile_map.sprite_lists['spawn']._get_center()[1]
        self.player.center_x = self.spawn_x
        self.player.center_y = self.spawn_y
        # Ввод
        self.left = self.right = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        
        # Эффект затемнения
        self.darkness_alpha = 0
        self.is_darkening = False
        self.is_lightening = False

        # Музыка уровней
        if 'level1' in self.level:
            self.lvl = arcade.load_sound('music/Jumper-lvl1.mp3')
        elif 'level2' in self.level:
            self.lvl = arcade.load_sound('music/ComputerAmbience-lvl2.mp3')
        elif 'level3' in self.level:
            self.lvl = arcade.load_sound('music/SneakySnitch-lvl3.mp3')
        self.playing = False

        # Звуки(удар об препятствие, прыжок, батут или орб)
        self.breaki = arcade.load_sound('audio/death.mp3')
        self.jump = arcade.load_sound('audio/jump.mp3')
        self.orb = arcade.load_sound('audio/orb.mp3')

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.scene['platform']
        )

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        if self.player:  # Проверяем, что player существует
            self.player_spritelist.draw()
        self.scene.draw()
        
        if self.darkness_alpha > 0:
            arcade.draw_lbwh_rectangle_filled(
                left=-SCREEN_WIDTH,
                bottom=0,
                width=(SCREEN_WIDTH * 4),
                height=(SCREEN_HEIGHT * 4),
                color=(0, 0, 0, int(self.darkness_alpha))
            )

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
                self.jump.play()
        
        if arcade.check_for_collision_with_list(self.player, self.jumppads):
            self.engine.jump(JUMP_SPEED + 2)
            self.jump_buffer_timer = 0
            self.orb.play(volume=0.5)
        elif arcade.check_for_collision_with_list(self.player, self.orbs) and self.jump_pressed and want_jump:
            self.engine.jump(JUMP_SPEED + 2)
            self.jump_buffer_timer = 0
            self.orb.play(volume=0.5)
        
        position = (
            self.player.center_x,
            self.player.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
            self.world_camera.position,
            position,
            0.1
        )

        # Заставляем шар кататься если change_angle истиннен и движение на земле
        if self.player.change_angle and grounded:
            if self.left and not self.right:
                self.player.angle -= ROTATION_SPEED
            elif self.right and not self.left:
                self.player.angle += ROTATION_SPEED
        elif self.player.change_angle and not grounded:
            if self.left and not self.right:
                self.player.angle -= ROTATION_SPEED // 2
            elif self.right and not self.left:
                self.player.angle += ROTATION_SPEED // 2
        
        # Шипы и прочая угроза
        if arcade.check_for_collision_with_list(self.player, self.danger):
            self.is_darkening = True
            self.is_lightening = False
            # Возвращаем игрока на спавн
            self.player.center_x = self.spawn_x
            self.player.center_y = self.spawn_y
            self.breaki.play()

        # Обновление эффекта затемнения
        if self.darkness_alpha > 0:
            self.darkness_alpha -= self.darkness_speed * delta_time
            if self.darkness_alpha < 0:
                self.darkness_alpha = 0
                self.is_darkening = False
        
        # Эффект смерти
        if self.is_darkening:
            self.darkness_alpha += self.darkness_speed
            if self.darkness_alpha >= 255:
                self.darkness_alpha = 255
                self.is_darkening = False
                self.is_lightening = True
        elif self.is_lightening:
            self.darkness_alpha -= self.lightening_speed
            if self.darkness_alpha <= 0:
                self.darkness_alpha = 0
                self.is_lightening = False

        # Теперь финиш - если доходит до финиша, то игра переключается в меню(и сохраняет прогресс для звездочки)
        if arcade.check_for_collision_with_list(self.player, self.end):
            men = menu.GameMenu()
            men.window = self.window  # Добавляем ссылку на окно
            self.playing = False
            arcade.stop_sound(self.lvl)
            self.window.show_view(men)

        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()
        if not self.playing:
            arcade.play_sound(self.lvl, loop=True)
            self.playing = True

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
            self.player.change_angle = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
            self.player.change_angle = True
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
            self.player.change_angle = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
            self.player.change_angle = False
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.45


def setup_game(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE):
    window = arcade.Window(width, height, title)
    game = MyGame()
    game.setup()
    window.show_view(game)
    return window

def main():
    window = setup_game()
    arcade.run()


if __name__ == "__main__":
    main()
