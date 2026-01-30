import arcade
import game

from pyglet.graphics import Batch


class GameMenu(arcade.View):
    def __init__(self):
        super().__init__()
        
        self.batch = Batch()
        self.logo = arcade.load_texture('materials/Logo1.png', 600, 162)
    
    def on_draw(self):
        self.clear()
        self.batch.draw()
        arcade.draw_texture_rect(self.logo)


if __name__ == '__main__':
    window = arcade.Window(1200, 600, "Учимся ставить на паузу")
    menu_view = GameMenu()
    window.show_view(menu_view)
    arcade.run()