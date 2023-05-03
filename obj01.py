from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty, StringProperty
from textureutil import TextureUtil
from kivy.uix.widget import Widget
from kivy.logger import Logger
from postime import PosTime, PosTimeUtil
import math
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader

# SE
missSound = SoundLoader.load('./sounds/miss.mp3')
explosionSound = SoundLoader.load('./sounds/explosion.mp3')
shout1Sound = SoundLoader.load('./sounds/shout1.mp3')
damagedSound = SoundLoader.load('./sounds/shout2.mp3')
healSound = SoundLoader.load('./sounds/heal.mp3')
clearSound = SoundLoader.load('./sounds/clear.mp3')

SQRT2 = math.sqrt(2) # よく使うsqrt2は定数として持たせて都度計算するのを回避させる

class ExplosionImage(Image):
    pass

""" ゲームオブジェクト共通クラス """
class BaseObj(Widget):
    # data
    texture = ObjectProperty(None)

    # param
    lifePoint = NumericProperty(None) # ライフポイント
    v = (0, 0) # x方向、y方向の速度(px/s)
    duration = 0 # オブジェクトの作業時間（爆発時間や停止時間等に使用）
    g = NumericProperty(None) # 重力加速度

    # flags
    alive = BooleanProperty(True) # 生存フラグ
    explode = BooleanProperty(False) # 爆発フラグ(Trueになったとき、実質的にしんでいる)
    jumping = BooleanProperty(True) # ジャンプフラグ。床と接触するまでは原則的にTrueとする

    def spawn(self, img, posX, posY):
        t01 = TextureUtil.getTexture(img, self.region)
        self.texture = t01
        self.pos = (posX, posY)

    def move(self, dt):
        pass

    def update(self, dt):
        if self.explode:
            self.duration += dt

        if self.duration > 0.3:
            self.alive = False
    
    """ オブジェクトの中央座標を取得する処理 """
    def centerPos(self):
        return (self.center_x, self.center_y)

    def affect(self, _obj01):

        if self is None or _obj01 is None:
            return # Noneに対しては処理を行わない(NullPointer対策)

        # オブジェクト left, bottom, right, top
        obj02_left = self.pos[0]
        obj02_bottom = self.pos[1]
        obj02_right = self.pos[0] + self.width
        obj02_top = self.pos[1] + self.height

        # 人 left, bottom, right, top
        obj01_left = _obj01.pos[0]
        obj01_bottom = _obj01.pos[1]
        obj01_right = _obj01.pos[0] + self.width
        obj01_top = _obj01.pos[1] + self.height

        # obj01の横座標がobj02の横座標に対し、接触を考慮しなくて良い状態の場合、以下の処理をスキップする  
        if (obj01_left > obj02_right) or (obj01_right < obj02_left):
            return

        # 衝突判定(相対ベクトルの角度を用いて判断。大きさが違う場合は判定方法を見直す必要があると思われる)
        if self.collide_widget(_obj01):

            centerPos0 = self.centerPos()
            centerPos1 = _obj01.centerPos()

            # 対象のオブジェクトとプレイヤーleftBottom座標(pos)を直線で結び、x軸に対しての角度を考える
            # 上記ベクトルのcosとsinを取得する
            cosX = PosTimeUtil.getCosTheta(PosTime(centerPos0), PosTime(centerPos1))
            sinX = PosTimeUtil.getSinTheta(PosTime(centerPos0), PosTime(centerPos1))

            # 地に足つける判定（物体から見て上にプレイヤーがいる状態）
            # 0.25 PI ≦ X ≦ 0.75 PI
            if obj02_top >= obj01_bottom and (sinX >= 0.5 * SQRT2 and cosX >= -0.5 * SQRT2 and cosX <= 0.5 * SQRT2):
                self.upAffect(_obj01)
            # 天井に頭ぶつける判定（物体から見て下にプレイヤーがいる状態）
            # 1.25 PI ≦ X ≦ 1.75 PI
            elif obj02_bottom <= obj01_top and (sinX <= -0.5 * SQRT2 and cosX >= -0.5 * SQRT2 and cosX <= 0.5 * SQRT2):
                self.downAffect(_obj01)
            # 右にオブジェクトがあるとき判定（物体から見て左にプレイヤーがいる状態）
            # 0.75 PI ＜ X ＜ 1.25 PI
            elif obj02_left < obj01_right and (cosX < -0.5 * SQRT2 and sinX > -0.5 * SQRT2 and sinX < 0.5 * SQRT2):
                self.leftAffect(_obj01)
            # 左にオブジェクトがあるとき判定（物体から見て右にプレイヤーがいる状態）
            # 1.75 PI ＜ X ＜ 2.25 PI(0.25PI)
            elif obj02_right > obj01_left and (cosX > 0.5 * SQRT2 and sinX > -0.5 * SQRT2 and sinX < 0.5 * SQRT2):
                self.rightAffect(_obj01)

    """ 対象がオブジェクト上方にある場合の処理 """
    def upAffect(self, _obj01):
        pass

    """ 対象がオブジェクト下方にある場合の処理 """
    def downAffect(self, _obj01):
        pass

    """ 対象がオブジェクト左方にある場合の処理 """
    def leftAffect(self, _obj01):
        pass

    """ 対象がオブジェクト右方にある場合の処理 """
    def rightAffect(self, _obj01):
        pass

    """ 生存状態かつ爆発状態(実質死んでいる)でない、活動可能な状態 """
    def isOK(self):
        return self.alive and not self.explode

    """ ダメージを受けた場合の処理。ライフポイントが尽きたらしぬ """
    def damaged(self):
        self.lifePoint -= 1
        if self.lifePoint <= 0 and self.isOK(): # ライフポイントが尽きた場合
            eximg = ExplosionImage() # 爆発アニメーションを初期化
            eximg.pos = self.pos # 爆発アニメーションをキャラクターの座標に配置
            eximg.size = self.size # サイズを設定
            self.add_widget(eximg) # 爆発アニメを追加する
            self.explode = True # 爆発フラグを立てる(アニメーション後、生存フラグoff)
            self.duration = 0 # アニメーション時間を初期化する
            explosionSound.play() # 爆発音を再生
        else: # ライフポイントが残っている場合
            damagedSound.play() # ダメージボイスを再生

    """ 敵がプレイヤーの座標を見て行動パターンを決定するための処理。何画面離れたところに来たら、等のチェックのために画面サイズを引数に使用する """
    def watch(self, target, screenWidth):
        pass # 敵用の処理ではあるけれど、実装改善のためにBaseObjに実装する

class Obj01(BaseObj):

    maxLifePoint = NumericProperty(None)

    """ 移動処理
        プレイヤーの移動処理はステージ全体の移動処理と連動しているため、ここには実装しない
    """ 
    def move(self, dt):
        pass

    """ 更新処理 """
    def update(self, dt):
        super(Obj01, self).update(dt)
        # 落ちたら生存フラグをFalseにする
        if self.pos[1] + self.height < 0:
            missSound.play()
            self.alive = False
        # 速度を加算
        if self.jumping:
            self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる

class Obj02(BaseObj):
    """ 対象がオブジェクト上方にある場合の処理 """
    def upAffect(self, target):
        target.pos[1] = self.pos[1] + self.height
        target.v = (target.v[0], 0)  # 床突き抜け回避処理
        target.jumping = False

    """ 対象がオブジェクト下方にある場合の処理 """
    def downAffect(self, target):
        target.pos[1] = self.pos[1] - target.height
        target.v = (target.v[0], -1 * target.v[1]) # 頭をぶつけたので速度反転

    """ 対象がオブジェクト左方にある場合の処理 """
    def leftAffect(self, target):
        target.pos[0] = self.pos[0] - target.width
        target.v = (0, target.v[1]) # 壁登り回避処理

    """ 対象がオブジェクト右方にある場合の処理 """
    def rightAffect(self, target):
        target.pos[0] = self.pos[0] + self.width
        target.v = (0, target.v[1]) # 壁登り回避処理

class BaseEnemyObj(BaseObj):
    pattern = 0
    score = NumericProperty(None) # 倒したときのスコア
    dropRate = NumericProperty(None) # アイテムのドロップ率
    drop = StringProperty(None) # ドロップするアイテム
    """ 移動処理 """
    def move(self, dt):
        self.pos = (self.pos[0] + self.v[0] * dt, self.pos[1] + self.v[1] * dt)

    """ 何らかの理由(敵からダメージを受けた等)で敵を倒した場合のドロップを無くす処理 """
    def clearReward(self):
        self.score = 0
        self.dropRate = 0
        self.drop = "0"


class Obj03(BaseEnemyObj):

    """ 更新処理 """
    def update(self, dt):
        super(Obj03, self).update(dt)

        # 落ちたら生存フラグをFalseにする
        if self.pos[1] + self.height < 0:
            self.alive = False

        # 速度を加算
        if self.jumping:
            self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる

    """ 敵がプレイヤーの座標を見て行動パターンを決定するための処理。何画面離れたところに来たら、等のチェックのために画面サイズを引数に使用する """
    def watch(self, target, screenWidth):
        if self.pattern == 0 and self.pos[0] > target.pos[0] and self.pos[0] - target.pos[0] < screenWidth:
            self.pattern = 1
            shout1Sound.play()
            self.v = (-160, self.v[1])

        if self.pattern % 2 == 1 and self.pos[0] < target.pos[0] - target.width * 3:
            self.v = (self.v[0] * -1, self.v[1])
            self.texture.flip_horizontal() # テクスチャ水平反転(希望)
            self.pattern = 2

        if self.pattern == 2 and self.pos[0] > target.pos[0] + target.width * 3:
            self.v = (self.v[0] * -1, self.v[1])
            self.texture.flip_horizontal() # テクスチャ反転
            self.pattern = 3

    """ 対象がオブジェクト上方にある場合の処理 """
    def upAffect(self, target):
        if self.isOK():
            target.v = (target.v[0], min(target.v[1] * -0.5, 1200))
            self.damaged() # ふんだら倒せる

    """ 対象がオブジェクト下方にある場合の処理 """
    def downAffect(self, target):
        if self.isOK():
            self.damaged() # 頭突きで倒せる

    """ 対象がオブジェクト左方にある場合の処理 """
    def leftAffect(self, target):
        if self.isOK():
            target.damaged() # やられる
            self.clearReward() # ドロップなくす
            self.alive = False # 敵も消える

    """ 対象がオブジェクト右方にある場合の処理 """
    def rightAffect(self, target):
        if self.isOK():
            target.damaged() # やられる
            self.clearReward() # ドロップなくす
            self.alive = False # 敵も消える

class Obj04(BaseObj):
    def affect(self, target):
        if self.isOK() and self.collide_widget(target):
            clearSound.play()
            self.alive = False

class Obj05(BaseObj):
    def affect(self, target):
        if self.isOK() and self.collide_widget(target):
            healSound.play()
            if hasattr(target, "maxLifePoint") and target.maxLifePoint > target.lifePoint:
                target.lifePoint += 1
            self.alive = False