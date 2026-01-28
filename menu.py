import arcade

from pyglet.graphics import Batch


class GameMenu(arcade.View):
    def __init__(self, widht, height, background_color=None):
        super().__init__(widht, height)
        
        self.batch = Batch()
        self.logo = arcade.load_texture('materials/Logo1.png', 600, 162)
    
    def on_draw(self):
        self.clear()
        self.batch.draw()
        arcade.draw_texture_rect(self.logo)


window = arcade.Window(1200, 600, "Учимся ставить на паузу")
menu_view = GameMenu(1200, 600)
window.show_view(menu_view)
arcade.run()