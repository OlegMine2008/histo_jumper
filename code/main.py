import arcade
import menu as me


def main():
    window = arcade.Window(1200, 600, "Just A Jumper")
    menu_view = me.GameMenu()
    window.show_view(menu_view)
    arcade.run()

if __name__ == '__main__':
    main()