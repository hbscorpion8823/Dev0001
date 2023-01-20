from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from textureutil import TextureUtil
from obj01 import Obj01, Obj02


class MyImages(Image):
    pass


class MainGame(Widget):
    def __init__(self, **kwargs):
        super(MainGame, self).__init__()

        # イメージをまとめた画像を読み込み
        imgs = MyImages()

        # obj01を初期化し、メインのWidgetに追加
        self.obj01 = Obj01()
        self.obj01.spawn(imgs)
        self.add_widget(self.obj01)

        # obj01を初期化し、メインのWidgetに追加
        self.obj02 = Obj02()
        self.obj02.spawn(imgs)
        self.add_widget(self.obj02)

        Clock.schedule_interval(self.update, 1 / 60.0)

    def update(self, td):
        v = 7
        tmpY = self.obj01.pos[1]
        self.obj01.pos = (self.obj01.pos[0], self.obj01.pos[1] - v)
        if self.obj01.collide_widget(self.obj02):
            self.obj01.pos = (self.obj01.pos[0], tmpY)


class MainApp(App):

    def build(self):
        mc = MainGame()
        return mc


if __name__ == '__main__':
    MainApp().run()
