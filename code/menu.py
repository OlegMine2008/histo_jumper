import arcade
import platformer as plat
# import runner as run

from arcade.gui import UIManager, UIFlatButton, UIDropdown
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout


class GameMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture('materials/menu_background.png')
        
        self.logo = arcade.Sprite('materials/Logo1.png', center_x=600, center_y=460)
        self.menu_list = arcade.SpriteList()
        self.menu_list.append(self.logo)

        # Переменная выбора уровня - храним путь к файлу
        self.level = 'materials/level1.json'
        
        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали
        
        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=20)  # Вертикальный стек
        
        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже
        
        self.manager.add(self.anchor_layout)  # Всё в manager
    
    def on_draw(self):
        self.clear()
    
        # Рисуем фон
        arcade.draw_texture_rect(
            texture=self.background,
            rect=arcade.Rect(
                (self.window.width // 2) if self.window else 600,
                (self.window.height // 2) if self.window else 300,
                self.window.width if self.window else 1200,
                self.window.height if self.window else 600,
                1200,
                600,
                600, 300
            )
        )
    
        self.menu_list.draw()
        self.manager.draw()

    
    def setup_widgets(self):
        level_map = {
            "Геометрия": 'materials/level1.json',
            "Машинный код": 'materials/level2.json',
            "Корзина": 'materials/level3.json',
            "Файлы": 'materials/level4.json'
        }
        
        dropdown = UIDropdown(
            options=["Геометрия", "Машинный код", "Корзина", "Файлы"], 
            width=600
        )
        dropdown.on_change = lambda event: self.on_dropdown_change(event.new_value, level_map)
        self.box_layout.add(dropdown)
        
        flat_button = UIFlatButton(
            text="Играть", 
            width=600, 
            height=50, 
            color=arcade.color.RED
        )
        flat_button.on_click = lambda event: self.start_game()
        self.box_layout.add(flat_button)
        
        self.anchor_layout.add(self.box_layout,
            anchor_x="center_x", 
            anchor_y="bottom", 
            align_y=150
        )
    
    def on_dropdown_change(self, value, level_map):
        self.level = level_map.get(value, 'materials/level1.json')

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def start_game(self):
        if isinstance(self.level, str) and not self.level.endswith('.json'):
            # Если это просто название уровня, преобразуем в путь
            level_map = {
                "Геометрия": 'materials/level1.json',
                "Машинный код": 'materials/level2.json',
                "Корзина": 'materials/level3.json',
                "Файлы": 'materials/level4.json'
            }
            level_path = level_map.get(self.level, 'materials/level1.json')
        else:
            level_path = self.level
            
        if 'level4.json' in level_path:
            pass
        else:
            game_view = plat.MyGame(level=level_path)
            
        if self.window and 'game_view' in locals():
            self.window.show_view(game_view)
    
    def on_show_view(self):
        self.manager.enable()
    
    def on_hide_view(self):
        self.manager.disable()


if __name__ == '__main__':
    window = arcade.Window(1200, 600, "Just A Jumper")
    menu_view = GameMenu()
    window.show_view(menu_view)
    arcade.run()