import arcade
import platformer as plat

from pyglet.graphics import Batch
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT


class GameMenu(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)
        
        self.batch = Batch()
        self.logo = arcade.Sprite('materials/Logo1.png', center_x=600, center_y=450)
        self.menu_list = arcade.SpriteList()
        self.menu_list.append(self.logo)
        
        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали
        
        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек
        
        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже
        
        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager
    
    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.menu_list.draw()
        self.manager.draw()
    
    def setup_widgets(self):
        dropdown = UIDropdown(options=["Геометрия", "Машинный код", "Файлы", "Родная Папка"], width=600)
        dropdown.on_change = lambda value: print(f"Выбрано: {value}")
        self.box_layout.add(dropdown)

    def on_mouse_press(self, x, y, button, modifiers):
        pass


if __name__ == '__main__':
    window = arcade.Window(1200, 600, "Just A Jumper")
    menu_view = GameMenu()
    window.show_view(menu_view)
    arcade.run()