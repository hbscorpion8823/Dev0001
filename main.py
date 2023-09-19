from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.image import Image
from obj01 import Obj01, Obj02, Obj03, Obj04, Obj05, BaseEnemyObj
from kivy.config import Config
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from postime import PosTime, PosTimeUtil
import time
import random
from kivy.core.window import Window
from kivy.uix.button import Button
import math
import sys

# 勝手にportraitオリエンテーションにするのを防ぐためのおまじない
# kivy.core.window を使用すると端末の方向によってはportraitオリエンテーションになってしまう
Config.set('graphics', 'resizable', 0)

""" タイトル画面 """
class TitleScreen(Widget):
    def pressStartButton(self):
        # 画面遷移： 次画面を生成後、自身をWindowから消し次画面をWindowに追加する
        mg = MainGame()
        Window.remove_widget(self)
        Window.add_widget(mg)

""" タイトル画面遷移ボタン """
class TitleButton(Button):
    pass

""" ゲームで使用する画像をまとめた1枚画像 """
class MyImages(Image):
    pass

""" メインのゲームウィジェット """
class MainGame(Widget):
    
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
    # 得点
    score = NumericProperty(None)
    # 描画したカラムインデックス左端
    leftIdx = NumericProperty(None)
    # 描画したカラムインデックス右端
    rightIdx = NumericProperty(None)
    # 描画エリア左端X座標
    leftX = NumericProperty(None)
    # 描画エリア右端X座標
    rightX = NumericProperty(None)
    # 観測用のオブジェクト TODO: いずれ削除する
    something = ObjectProperty(None)

    """ 初期化処理 """
    def __init__(self, **kwargs):

        # 上位クラスの初期化処理
        super(MainGame, self).__init__()

        # デバイスの画面解像度
        self.screenWidth = Window.width
        # 画面の位置座標を初期化
        self.currentX = 0
        # スコアを初期化
        self.score = 0
        self.drawScore()

        # ステージ内オブジェクトの配列を初期化
        self.objs = []
        # タッチ座標配列を初期化
        self.touchPosArray = []
        # 敵配列を初期化
        self.enemies = []
        # イメージをまとめた画像を読み込み
        self.imgs = MyImages()

        # ステージのタイルを読み込む
        with open('tile01.txt', 'r', encoding='UTF-8') as f:
            self.stageRows = f.readlines()

        if self.setStageWidth() is False:
            print("tile file is invalid. column length is different")
            sys.exit(1)

        self.drawStage()

        # 毎秒60回更新処理を実行する
        self.updateEvent = Clock.schedule_interval(self.update, 1 / 60.0)

    """ ゲームオブジェクト生成 """
    def createGameObj(self, objectType, imgs, posX, posY):
        obj = None

        if objectType == "1":
            if self.player is None: # プレイヤーが設定されていない場合のみ実行
                obj = Obj01()
                self.player = obj
                self.player.bind(lifePoint=self.drawPlayerLife)
                self.drawPlayerLife(self.player, self.player.lifePoint) # 最初の1回のライフゲージ描画
        elif objectType == "2":
            obj = Obj02()
            if self.something is None: # 最初の1オブジェクトを観測対象に指定
                self.something = obj
            self.objs.append(obj)
        elif objectType == "3":
            obj = Obj03()
            self.objs.append(obj)
        elif objectType == "4":
            obj = Obj04()
            self.objs.append(obj)
        elif objectType == "5":
            obj = Obj05()
            self.objs.append(obj)
        
        if obj is not None:
            obj.spawn(imgs, posX, posY)
            if isinstance(obj, BaseEnemyObj):
                obj.bind(alive=self.getReward)
            elif isinstance(obj, Obj04):
                obj.bind(alive=self.gameClear)
            self.objectLayer.add_widget(obj)

        return obj

    """ 秒間60回実行されるメイン処理 """
    def update(self, dt):
        
        # 移動系処理メイン
        self.moveMain(dt)
        # 更新系処理メイン
        self.updateMain(dt)

    """ 各オブジェクトの移動系処理 """
    def moveMain(self, dt):

        if self.player is None:
            return

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
                playerDx = 0.5 * self.screenWidth - self.player.pos[0]
                relativeDx = dx * -1
                self.currentX = self.currentX + dx  # 右スクロール中、現在座標は加算される
            elif self.player.pos[0] <= 0.5 * self.screenWidth and self.player.v[0] < 0 and self.currentX > 0:
                playerDx = 0.5 * self.screenWidth - self.player.pos[0]
                relativeDx = dx * -1
                self.currentX = self.currentX + dx  # 左スクロール中、現在座標は減算される
            else:
                playerDx = dx
                relativeDx = 0
            # プレイヤーの移動
            self.player.pos = (self.player.pos[0] + playerDx,
                            self.player.pos[1] + self.player.v[1] * dt)
        # プレイヤーの移動制限
        if self.player.pos[0] < 0: # playerは0より左へ移動できない
            self.player.pos = (0, self.player.pos[1])
        elif self.player.pos[0] > self.screenWidth - self.player.width: # 画面右端より先へは移動できない
            self.player.pos = (self.screenWidth - self.player.width, self.player.pos[1])
        # オブジェクトの移動(相対速度的なもの)
        for obj in self.objs:
            obj.pos = (obj.pos[0] + relativeDx, obj.pos[1]) # 相対速度的な移動
            obj.move(dt)

        # self.printIdx() # インデックスを標準出力
        self.drawStage()

    """ 各オブジェクトの状態更新系処理 """
    def updateMain(self, dt):

        if self.player is not None:
            self.player.jumping = True # プレイヤーのジャンプ中フラグをTrueにする。床からの作用を受けなかった場合はTrueのままになる

        for obj in self.objs:
            # ジャンプフラグ制御
            if isinstance(obj, BaseEnemyObj): # 敵インスタンスである場合
                obj.jumping = True # 敵のジャンプ中フラグをTrueにする

            # 作用系処理
            if obj.isOK(): # オブジェクトが生存中かつ爆発していない場合のみ実行
                obj.affect(self.player) # プレイヤーに対する作用（万物共通）
                if not isinstance(obj, BaseEnemyObj): # 敵ではないオブジェクトの場合、敵に対して作用する（床が敵を押し返すような作用）
                    for something in self.objs: # ループの中にループを入れる実装、あまり良くない気はしている
                        if isinstance(something, BaseEnemyObj): # somethingが敵である場合のみ実行
                            obj.affect(something) # 床 --> 敵への作用
                else: # objが敵である場合
                    obj.watch(self.player, self.screenWidth) # 敵がプレイヤーを確認して行動パターンを決定したりする処理

            # 生存判定
            if obj.alive:
                obj.update(dt)
            else:
                self.objectLayer.remove_widget(obj)
                self.objs.remove(obj)

            # 描画エリアからはみ出したオブジェクトの削除
            if self.currentX + obj.pos[0] + obj.width < self.leftX:
                self.objectLayer.remove_widget(obj)
                self.objs.remove(obj)
            elif self.currentX + obj.pos[0] > self.rightX:
                self.objectLayer.remove_widget(obj)
                self.objs.remove(obj)
        
        if self.player is None:
            return

        # プレイヤー状態更新系処理
        if self.player.alive:
            self.player.update(dt)
        else:
            self.finishGame('GAME OVER')
            self.objectLayer.remove_widget(self.player)

    """ タイトルボタン押下処理(self=メインのゲームウィジェット, instance=ボタンインスタンス) """
    def pressTitleButton(self, instance):
        # 画面遷移： 次画面を生成後、自身をWindowから消し次画面をWindowに追加する
        ts = TitleScreen()
        Window.remove_widget(self)
        Window.add_widget(ts)

    """ ゲームオーバー/クリア処理 """
    def finishGame(self, text):
        self.txtGameOver.text = str(text)
        self.isGameOver = True
        button = TitleButton()
        button.bind(on_press=self.pressTitleButton)
        self.objectLayer.add_widget(button)
        Clock.unschedule(self.updateEvent)

    """ タップ時処理 """
    def on_touch_down(self, touch):
        super(MainGame, self).on_touch_down(touch) # FloatLayout内でボタンを押すのに必要な処理

        if self.player is not None and self.player.collide_point(touch.x, touch.y):
            self.player.v = (0, 0) # プレイヤーをタップしたら止まる

    """ ドラッグ（スワイプ？）時処理 """
    def on_touch_move(self, touch):
        # move座標を記録（時間もあわせて記録）
        pt = PosTime(touch.pos, time.time())
        self.touchPosArray.append(pt)
        if len(self.touchPosArray) > 5:
            self.touchPosArray.pop(0)
        # 始点と終点の座標と時間をとる
        # 直近最大5点の始点と終点をp1、p2とする
        p1 = self.touchPosArray[0]
        p2 = self.touchPosArray[len(self.touchPosArray) - 1]
        # プレイヤーの速度を算出する
        self.player.v = (PosTimeUtil.getVx(p1, p2), PosTimeUtil.getVy(p1, p2))

    """ プレイヤーのライフゲージを描画する処理。プレイヤーのライフの増減をトリガーに呼ばれたりする """
    def drawPlayerLife(self, playerObj, playerLife):
        txt = ""
        for x in range(0, playerLife):
            txt += "P"
        self.txtPlayerLife.text = str(txt)

    """ スコアを描画する処理 """
    def drawScore(self):
        self.txtScore.text = str(self.score)

    """ 敵を倒したときの報酬を受け取る処理 """
    def getReward(self, enemyObj, alive):
        # スコアを加算
        self.score += enemyObj.score
        self.drawScore()
        # ドロップ処理
        rand = random.randint(0, 100) # 乱数がドロップ率以下ならばドロップ
        if rand <= enemyObj.dropRate:
            self.createGameObj(enemyObj.drop, self.imgs, enemyObj.pos[0], enemyObj.pos[1])

    """ ゲームクリア処理 """
    def gameClear(self, obj04, alive):
        self.finishGame('Congraturations!')

    """ 左端X座標とステージタイルから1画面分の画面描写を行う。いずれも変数として保持しているので、selfのみを引数に指定 """
    def drawStage(self):
        # 現在座標から画面左から-20%(or0)の座標と画面右から+20%(orMAX)の座標を決定する
        leftX = max(0, self.currentX - self.screenWidth * 0.2) # when 0, idx = 0
        rightX = min(self.currentX + self.screenWidth * 1.2, self.stageWidth) # when 5400, idx = 53

        # 上記座標のタイルインデックスを取得する
        leftIdx = math.floor(leftX / 100.0)
        rightIdx = math.ceil(rightX / 100.0) - 1

        # インデックスが変わらない場合は処理を終了
        if self.leftIdx is not None and self.rightIdx is not None and self.leftIdx == leftIdx and self.rightIdx == rightIdx:
            return

        for xIdx in range(leftIdx, rightIdx + 1):
            drawFlg = False
            if self.leftIdx is None or  xIdx < self.leftIdx: # 描画済み左インデックスが指定されていないケース または 現在インデックスが描画済み左インデックスよりも左の場合
                drawFlg = True
            if self.rightIdx is None or xIdx > self.rightIdx: # 描画済み右インデックスが指定されていないケース または 現在インデックスが描画済み右インデックスよりも右の場合
                drawFlg = True
            if drawFlg is True: # 描画フラグがTrueの場合のときのみ
                for yIdx in range(0, len(self.stageRows)):
                    tiles = self.stageRows[len(self.stageRows) - 1 - yIdx].strip()
                    self.createGameObj(tiles[xIdx], self.imgs, 100 * xIdx - self.currentX, 100 * yIdx) # tiles[x]の値ごとに適切なオブジェクトを画面に配置する

        # 描画後、インデックスおよび描画エリアX座標を上書きする
        self.leftIdx = leftIdx
        self.rightIdx = rightIdx
        self.leftX = leftX
        self.rightX = rightX

    def setStageWidth(self):
        for y in range(0, len(self.stageRows)):
            tiles = self.stageRows[len(self.stageRows) - 1 - y].strip()
            stageWidth = len(tiles) * 100
            if self.stageWidth == None:
                self.stageWidth = stageWidth
            elif self.stageWidth != stageWidth:
                return False # Not all ok, return False
        # all ok, return True
        return True

    """ インデックスを出力 TODO: この関数はいずれ消すこと """
    def printIdx(self):
        # 現在座標から画面左から-20%(or0)の座標と画面右から+20%(orMAX)の座標を決定する
        leftX = max(0, self.currentX - self.screenWidth * 0.2) # when 0, idx = 0
        rightX = min(self.currentX + self.screenWidth * 1.2, self.stageWidth) # when 5400, idx = 53

        # 上記座標のタイルインデックスを取得する
        leftIdx = math.floor(leftX / 100.0)
        rightIdx = math.ceil(rightX / 100.0) - 1
        print("Hoge currentX=" + str(self.currentX) 
              + ", screenWidth=" + str(self.screenWidth)
              + ", leftIdx=" + str(leftIdx) 
              + ", rightIdx=" + str(rightIdx)
              + ", something.X=" + str(self.something.pos[0]))


""" メインのクラス(Androidプログラムで言うところのActivity) """
class MainApp(App):

    def build(self):
        # タイトル画面をアプリケーションに設定する
        ts = TitleScreen()
        return ts

if __name__ == '__main__':
    MainApp().run()
