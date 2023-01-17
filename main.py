from kivy.app import App
from kivy.uix.widget import Widget


class MainGame(Widget):
    pass


class MainApp(App):

    def build(self):
        mc = MainGame()
        return mc


if __name__ == '__main__':
    MainApp().run()
