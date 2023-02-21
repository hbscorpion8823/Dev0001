from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from obj01 import Obj01, Obj02, Obj03
from kivy.config import Config
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from postime import PosTime, PosTimeUtil
import time
import math
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

# 勝手にportraitオリエンテーションにするのを防ぐためのおまじない
# kivy.core.window を使用すると端末の方向によってはportraitオリエンテーションになってしまう
Config.set('graphics', 'resizable', 0)


class MyImages(Image):
    """ ゲームで使用する画像をまとめた1枚画像 """
    pass


class MainGame(Widget):
    """ メインのゲームウィジェット """

    # プレイヤー
    player = ObjectProperty(None)
    # MainGame内のオブジェクト（プレイヤー以外）
    objs = ObjectProperty(None)
    # タッチ座標配列
    touchPosArray = ObjectProperty(None)
    # 現在のX座標
    currentX = NumericProperty(None)
    # 画面横幅
    screenWidth = NumericProperty(None)
    # ステージ横幅
    stageWidth = NumericProperty(None)
    # ゲームオーバーフラグ
    isGameOver = BooleanProperty(False)

    def __init__(self, **kwargs):
        """ 初期化処理 """

        # 上位クラスの初期化処理
        super(MainGame, self).__init__()

        # デバイスの画面解像度
        Logger.info('Hoge: Window.width={}'.format(Window.width))
        self.screenWidth = Window.width

        # 画面の位置座標を初期化
        self.currentX = 0

        # ステージ内オブジェクトの配列を初期化
        self.objs = []
        # タッチ座標配列を初期化
        self.touchPosArray = []
        # 敵配列を初期化
        self.enemies = []

        # ステージのタイルを読み込む
        with open('testtile.txt', 'r', encoding='UTF-8') as f:
            tileLines = f.readlines()

        # イメージをまとめた画像を読み込み
        imgs = MyImages()

        for y in range(0, len(tileLines)):
            tiles = tileLines[len(tileLines) - 1 - y].strip()
            self.stageWidth = len(tiles) * 100
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
                elif tiles[x] == "3":
                    # obj02を初期化し、メインのWidgetに追加
                    obj03 = Obj03()
                    obj03.spawn(imgs)
                    obj03.pos = (x * 100, y * 100)
                    self.enemies.append(obj03)
                    self.add_widget(obj03)


        # 毎秒60回更新処理を実行する
        Clock.schedule_interval(self.update, 1 / 60.0)

    def update(self, dt):
        """ 秒間60回実行されるメイン処理

        :type dt: float(time.time()で取得される値)
        :param dt: 微分積分でよく使用される⊿t的なパラメータ

        """
        if self.isGameOver:
            return

        # 移動系処理メイン
        self.moveMain(dt)
        # 更新系処理メイン
        self.updateMain(dt)

    def moveMain(self, dt):
        """ 各オブジェクトの移動系処理 """

        # x変化量を出す
        dx = self.player.v[0] * dt
        playerDx = 0  # プレイヤー自身のx増分
        relativeDx = 0  # 相対的x増分

        # player系移動処理
        if self.player.isOK(): # プレイヤーが健在なときのみ発生する移動
            # スクロール処理
            # player座標 >= 中央 && 速度>0 && ステージに右側がある: プレイヤーは動かず、プレイヤー以外が左へ移動する
            # player < 中央 - プレイヤー横幅 && 速度<0 && ステージに左側がある: プレイヤーは動かず、プレイヤー以外が右へ移動する
            # それ以外: プレイヤーの速度 * 時間 でプレイヤーを移動する
            if self.player.pos[0] >= 0.5 * self.screenWidth and self.player.v[0] > 0 and self.currentX + self.screenWidth < self.stageWidth:
                playerDx = 0
                relativeDx = dx * -1
                self.currentX = self.currentX + dx  # 右スクロール中、現在座標は加算される
            elif self.player.pos[0] < 0.5 * self.screenWidth - self.player.size[0] and self.player.v[0] < 0 and self.currentX > 0:
                playerDx = 0
                relativeDx = dx * -1
                self.currentX = self.currentX + dx  # 左スクロール中、現在座標は減算される
            else:
                playerDx = dx
                relativeDx = 0
        # プレイヤーの移動
        self.player.pos = (self.player.pos[0] + playerDx,
                           self.player.pos[1] + self.player.v[1] * dt)
        Logger.info('Hoge: player.x={}, screenWidth={}'.format(
            self.player.pos[0], self.screenWidth))
        # プレイヤーの移動制限
        if self.player.pos[0] < 0: # playerは0より左へ移動できない
            self.player.pos = (0, self.player.pos[1])
        elif self.player.pos[0] > self.screenWidth - self.player.width: # 画面右端より先へは移動できない
            self.player.pos = (self.screenWidth - self.player.width, self.player.pos[1])
        # オブジェクトの移動(相対速度的なもの)
        for obj02 in self.objs:
            obj02.pos = (obj02.pos[0] + relativeDx, obj02.pos[1])
        # 敵の移動(相対速度的なもの＋敵自身の移動)
        for enemy in self.enemies:
            enemy.pos = (enemy.pos[0] + relativeDx, enemy.pos[1])
            enemy.move(dt)

    def updateMain(self, dt):
        """ 各オブジェクトの状態更新系処理 """

        # 作用系処理
        for obj02 in self.objs:
            # 床がプレイヤーを排他する処理
            obj02.affect(self.player)
        for enemy in self.enemies:
            # 敵がプレイヤーを排他する処理
            enemy.affect(self.player)

        # プレイヤー状態更新系処理
        if self.player.alive:
            self.player.update(dt)
        else:
            self.isGameOver = True
            self.remove_widget(self.player)

        # 敵状態更新系処理
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt)
            else:
                self.remove_widget(enemy)

    """ タップ時処理 """

    def on_touch_down(self, touch):
        """ タップ時処理

        :type touch: tupple
        :param touch: タッチ座標

        """

        if self.player is None:
            pass
        elif self.player.collide_point(touch.x, touch.y):
            self.player.v = (0, 0)

    def on_touch_move(self, touch):
        """ ドラッグ（スワイプ？）時処理 

        :type touch: tupple
        :param touch: タッチ座標

        """

        # move座標を記録（時間もあわせて記録）
        pt = PosTime(touch.pos, time.time())
        self.touchPosArray.append(pt)
        if len(self.touchPosArray) > 5:
            self.touchPosArray.pop(0)

        # 始点と終点の座標と時間をとる
        # 直近最大5点の始点と終点をp1、p2とする
        p1 = self.touchPosArray[0]
        p2 = self.touchPosArray[len(self.touchPosArray) - 1]

        # 角度を算出
        sinTheta = PosTimeUtil.getSinTheta(p1, p2)
        # 45度超なら上に、45度以下なら横に速度を発生させる
        if sinTheta == None:
            pass
        elif math.fabs(sinTheta) > 0.5 * math.sqrt(2):
            self.player.v = (self.player.v[0], PosTimeUtil.getVy(p1, p2))
        else:
            self.player.v = (PosTimeUtil.getVx(p1, p2), self.player.v[1])


class MainApp(App):

    def build(self):
        mc = MainGame()
        return mc


if __name__ == '__main__':
    MainApp().run()
