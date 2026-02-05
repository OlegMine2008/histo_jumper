import arcade
import menu
import time

from arcade.gui import UIManager, UIFlatButton
from arcade.gui.widgets.layout import UIAnchorLayout


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
    def __init__(self, level="data/materials/level1.json"):
        super().__init__()
        if 'level2' in level:
            arcade.set_background_color(arcade.color.BLACK)
        elif 'level1' in level:
            arcade.set_background_color(arcade.color.ASH_GREY)
        elif 'level3' in level:
            arcade.set_background_color(arcade.color.OCEAN_BOAT_BLUE)
        elif 'level4' in level:
            arcade.set_background_color(arcade.color.LIGHT_CORAL)
        elif 'level5' in level:
            arcade.set_background_color(arcade.color.LIGHT_BLUE)
        self.level = level
        self.darkness_alpha = 0
        self.is_darkening = False
        self.is_lightening = False
        self.darkness_speed = 100
        self.lightening_speed = 0.5

        # Время для проверки звука
        self.last_sound_time = 0
        self.sound_cooldown = 0.1

        # Инициализируем player здесь, чтобы он был доступен во всех методах
        self.player = None
        self.lvl_player = None
        self.setup()  # Вызываем setup сразу после инициализации

    def return_to_menu(self) -> None:
        men = menu.GameMenu()
        men.window = self.window  # Добавляем ссылку на окно
        if self.lvl_player:
            self.lvl_player.pause()
        self.window.show_view(men)

    def setup(self):
        # Спрайт игрока.
        # На 3/4 уровнях делаем шар чуть меньше, чтобы он проходил через узкие места 1x1.
        player_scale = 2
        if ('level4' in self.level) or ('level5' in self.level):
            player_scale = 1.8
        self.player = arcade.Sprite("data/materials/character_test.png", scale=player_scale)
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.world_camera = arcade.camera.Camera2D()  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D()
        # Чтобы GUI рисовался в координатах окна, а не мира.
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

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
        self.lvl = None
        if 'level1' in self.level:
            self.lvl = arcade.load_sound('data/music/Jumper-lvl1.mp3')
        elif 'level2' in self.level:
            self.lvl = arcade.load_sound('data/music/ComputerAmbience-lvl2.mp3')
        elif 'level3' in self.level:
            self.lvl = arcade.load_sound('data/music/SneakySnitch-lvl3.mp3')
        elif 'level4' in self.level or 'level5' in self.level:
            self.lvl = arcade.load_sound('data/music/Last.mp3')
        self.playing = False

        # Звуки(удар об препятствие, прыжок, батут или орб)
        self.breaki = arcade.load_sound('data/audio/death.mp3')
        self.jump = arcade.load_sound('data/audio/jump.mp3')
        self.orb = arcade.load_sound('data/audio/orb.mp3')

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.scene['platform']
        )

        # Если улетели далеко вниз — считаем смертью.
        self.fall_death_y = -SCREEN_HEIGHT

        # Кнопка "В меню" (в игре).
        if hasattr(self, "ui_manager") and self.ui_manager:
            self.ui_manager.disable()
        self.ui_manager = UIManager()
        self.ui_manager.enable()
        self.ui_anchor = UIAnchorLayout()
        self.ui_manager.add(self.ui_anchor)

        self.menu_button = UIFlatButton(
            text="В меню",
            width=160,
            height=40,
            color=arcade.color.DARK_GRAY,
        )
        self.menu_button.on_click = lambda event: self.return_to_menu()
        self.ui_anchor.add(
            self.menu_button,
            anchor_x="left",
            anchor_y="top",
            align_x=20,
            align_y=-20,
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

        self.gui_camera.use()
        if hasattr(self, "ui_manager") and self.ui_manager:
            self.ui_manager.draw()

    def on_update(self, delta_time):
        current_time = time.time()

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
                if current_time - self.last_sound_time >= self.sound_cooldown:
                    self.play_sound('jump')

        if arcade.check_for_collision_with_list(self.player, self.jumppads):
            self.engine.jump(JUMP_SPEED + 2)
            self.jump_buffer_timer = 0
            if current_time - self.last_sound_time >= self.sound_cooldown:
                self.play_sound('orb')
        elif arcade.check_for_collision_with_list(self.player, self.orbs) and self.jump_buffer_timer > 0:
            self.engine.jump(JUMP_SPEED + 2)
            self.jump_buffer_timer = 0
            if current_time - self.last_sound_time >= self.sound_cooldown:
                self.play_sound('orb')

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
            if current_time - self.last_sound_time >= self.sound_cooldown:
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
            self.return_to_menu()

        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()

        if self.player.center_y < self.fall_death_y:
            self.is_darkening = True
            self.is_lightening = False
            # Возвращаем игрока на спавн
            self.player.center_x = self.spawn_x
            self.player.center_y = self.spawn_y
            if current_time - self.last_sound_time >= self.sound_cooldown:
                self.breaki.play()

        if (not self.playing) and (self.lvl is not None):
            self.lvl_player = arcade.play_sound(self.lvl, loop=True, volume=0.7)
            self.playing = True

    def play_sound(self, sound):
        if sound == 'orb':
            self.orb.play(volume=0.5)
        elif sound == 'jump':
            self.jump.play(volume=0.5)
        elif sound == 'death':
            self.breaki.play(volume=0.5)
        self.last_sound_time = time.time()

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

    def on_show_view(self):
        if hasattr(self, "ui_manager") and self.ui_manager:
            self.ui_manager.enable()

    def on_hide_view(self):
        if hasattr(self, "ui_manager") and self.ui_manager:
            self.ui_manager.disable()


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

