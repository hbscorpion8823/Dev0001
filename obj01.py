from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty, BooleanProperty
from textureutil import TextureUtil
from kivy.uix.widget import Widget
from kivy.logger import Logger
from postime import PosTime, PosTimeUtil
import math
from kivy.animation import Animation


class BaseObj(Widget):
    texture = ObjectProperty(None)
    alive = BooleanProperty(True)
    SQRT2 = math.sqrt(2) # よく使うsqrt2は定数として持たせて都度計算するのを回避させる
    explode = BooleanProperty(False)

    def spawn(self, img):
        t01 = TextureUtil.getTexture(img, self.region)
        self.texture = t01

    def move(self, dt):
        pass

    def update(self, dt):
        pass

    def affect(self, _obj01):
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

        # 衝突判定(現在の衝突状態と直前の座標の両面から勘案)
        if self.collide_widget(_obj01):

            # 対象のオブジェクトとプレイヤーleftBottom座標(pos)を直線で結び、x軸に対しての角度を考える
            # 上記ベクトルのcosとsinを取得する
            cosX = PosTimeUtil.getCosTheta(PosTime(self.pos), PosTime(_obj01.pos))
            sinX = PosTimeUtil.getSinTheta(PosTime(self.pos), PosTime(_obj01.pos))

            Logger.info('Hoge: player1=({},{})'.format(_obj01.pos[0], _obj01.pos[1]))
            # 地に足つける判定（物体から見て上にプレイヤーがいる状態）
            # 0.25 PI ≦ X ≦ 0.75 PI
            if obj02_top >= obj01_bottom and (sinX >= 0.5 * self.SQRT2 and cosX >= -0.5 * self.SQRT2 and cosX <= 0.5 * self.SQRT2):
                Logger.info('Hoge: case1')
                self.upAffect(_obj01)
            # 天井に頭ぶつける判定（物体から見て下にプレイヤーがいる状態）
            # 1.25 PI ≦ X ≦ 1.75 PI
            elif obj02_bottom <= obj01_top and (sinX <= -0.5 * self.SQRT2 and cosX >= -0.5 * self.SQRT2 and cosX <= 0.5 * self.SQRT2):
                Logger.info('Hoge: case2')
                self.downAffect(_obj01)
            # 右にオブジェクトがあるとき判定（物体から見て左にプレイヤーがいる状態）
            # 0.75 PI ＜ X ＜ 1.25 PI
            elif obj02_left < obj01_right and (cosX < -0.5 * self.SQRT2 and sinX > -0.5 * self.SQRT2 and sinX < 0.5 * self.SQRT2):
                Logger.info('Hoge: case3')
                self.leftAffect(_obj01)
            # 左にオブジェクトがあるとき判定（物体から見て右にプレイヤーがいる状態）
            # 1.75 PI ＜ X ＜ 2.25 PI
            elif obj02_right > obj01_left and (cosX > 0.5 * self.SQRT2 and sinX > -0.5 * self.SQRT2 and sinX < 0.5 * self.SQRT2):
                Logger.info('Hoge: case4')
                self.rightAffect(_obj01)

            Logger.info('Hoge: player2=({},{})'.format(_obj01.pos[0], _obj01.pos[1])) 

    def upAffect(self, _obj01):
        """ 対象がオブジェクト上方にある場合の処理 """
        pass

    def downAffect(self, _obj01):
        """ 対象がオブジェクト下方にある場合の処理 """
        pass

    def leftAffect(self, _obj01):
        """ 対象がオブジェクト左方にある場合の処理 """
        pass

    def rightAffect(self, _obj01):
        """ 対象がオブジェクト右方にある場合の処理 """
        pass

    def finish(self):
        self.alive = False

class Obj01(BaseObj):

    v = (0, 0)

    g = 9.8 * 200

    def move(self, dt):
        """ 移動処理
            プレイヤーの移動処理はステージ全体の移動処理と連動しているため、ここには実装しない
        """ 
        pass


    def update(self, dt):

        # 落ちたら生存フラグをFalseにする
        if self.pos[1] + self.height < 0:
            self.alive = False

        # 速度を加算
        self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる


class Obj02(BaseObj):
    def upAffect(self, _obj01):
        """ 対象がオブジェクト上方にある場合の処理 """
        _obj01.pos[1] = self.pos[1] + self.height
        _obj01.v = (_obj01.v[0], 0)  # 床突き抜け回避処理

    def downAffect(self, _obj01):
        """ 対象がオブジェクト下方にある場合の処理 """
        _obj01.pos[1] = self.pos[1] - _obj01.height
        _obj01.v = (_obj01.v[0], -1 * _obj01.v[1]) # 頭をぶつけたので速度反転

    def leftAffect(self, _obj01):
        """ 対象がオブジェクト左方にある場合の処理 """
        _obj01.pos[0] = self.pos[0] - _obj01.width
        _obj01.v = (0, _obj01.v[1]) # 壁登り回避処理

    def rightAffect(self, _obj01):
        """ 対象がオブジェクト右方にある場合の処理 """
        _obj01.pos[0] = self.pos[0] + self.width
        _obj01.v = (0, _obj01.v[1]) # 壁登り回避処理


class Obj03(BaseObj):

    v = (0, 0)

    g = 9.8 * 200

    def move(self, dt):
        """ 移動処理 """ 
        pass


    def update(self, dt):

        # 落ちたら生存フラグをFalseにする
        if self.pos[1] + self.height < 0:
            self.alive = False

        # 速度を加算
        self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる

    def upAffect(self, _obj01):
        """ 対象がオブジェクト上方にある場合の処理 """
        self.alive = False

    def downAffect(self, _obj01):
        """ 対象がオブジェクト下方にある場合の処理 """
        self.alive = False

    def leftAffect(self, _obj01):
        """ 対象がオブジェクト左方にある場合の処理 """
        _obj01.alive = False

    def rightAffect(self, _obj01):
        """ 対象がオブジェクト右方にある場合の処理 """
        _obj01.alive = False
