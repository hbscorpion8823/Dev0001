from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from obj01 import Obj01, Obj02
from kivy.config import Config
from kivy.properties import ObjectProperty
from postime import PosTime, PosTimeUtil
import time
import math

# 勝手にportraitオリエンテーションにするのを防ぐためのおまじない
Config.set('graphics', 'resizable', False)


class MyImages(Image):
    pass


class MainGame(Widget):

    # プレイヤー
    player = ObjectProperty(None)
    # MainGame内のオブジェクト（プレイヤー以外）
    objs = ObjectProperty(None)
    # タッチ座標配列
    touchPosArray = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainGame, self).__init__()

        # ステージ内オブジェクトの配列を初期化
        self.objs = []
        # タッチ座標配列を初期化
        self.touchPosArray = []

        f = open('tile01.txt', 'r', encoding='UTF-8')
        tileLines = f.readlines()
        f.close()

        # イメージをまとめた画像を読み込み
        imgs = MyImages()

        for y in range(0, len(tileLines)):
            tiles = tileLines[len(tileLines) - 1 - y].strip()
            for x in range(0, len(tiles)):
                if tiles[x] == "1":
                    # obj01を初期化し、メインのWidgetに追加
                    self.player = Obj01()
                    self.player.spawn(imgs)
                    self.player.pos = (x * 100, y * 100)
                    self.add_widget(self.player)
                elif tiles[x] == "2":
                    # obj02を初期化し、メインのWidgetに追加
                    obj02 = Obj02()
                    obj02.spawn(imgs)
                    obj02.pos = (x * 100, y * 100)
                    self.objs.append(obj02)
                    self.add_widget(obj02)

        Clock.schedule_interval(self.update, 1 / 60.0)

    def update(self, td):

        # 移動系処理
        self.player.update(td)

        for obj02 in self.objs:
            # 移動系処理
            obj02.update(td)
            # 衝突判定系処理
            obj02.keepoff(self.player, td)

    def on_touch_down(self, touch):
        print(touch)

        if self.player is None:
            pass
        else:
            self.player.center_x = touch.pos[0]
            self.player.center_y = touch.pos[1]

    def on_touch_move(self, touch):
        # move座標を記録（時間もあわせて記録）
        pt = PosTime(touch.pos, time.time())
        self.touchPosArray.append(pt)
        if len(self.touchPosArray) > 5:
            self.touchPosArray.pop(0)

        # 始点と終点の座標と時間をとる
        p1 = self.touchPosArray[0]
        p2 = self.touchPosArray[len(self.touchPosArray) - 1]

        # 角度を算出
        angle = PosTimeUtil.getAngle(p1, p2)
        # 45度超なら上に、45度以下なら横に速度を発生させる
        if angle == None:
            pass
        elif angle > 0.25 * math.pi:
            self.player.v = (self.player.v[0], 5)
        else:
            self.player.v = (5, self.player.v[1])


class MainApp(App):

    def build(self):
        mc = MainGame()
        return mc


if __name__ == '__main__':
    MainApp().run()
