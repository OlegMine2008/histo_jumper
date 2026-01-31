import arcade
import platformer as plat

from pyglet.graphics import Batch


class GameMenu(arcade.View):
    def __init__(self):
        super().__init__()
        
        self.batch = Batch()
        self.logo = arcade.load_texture('materials/Logo1.png')
    
    def on_draw(self):
        self.clear()
        self.batch.draw()
        arcade.draw_texture_rect(self.logo, rect=[600, 162])


if __name__ == '__main__':
    window = arcade.Window(1200, 600, "Just A Jumper")
    menu_view = GameMenu()
    window.show_view(menu_view)
    arcade.run()