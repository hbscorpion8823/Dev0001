from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty, BooleanProperty
from textureutil import TextureUtil
from kivy.uix.widget import Widget
from kivy.logger import Logger


class BaseObj(Widget):
    texture = ObjectProperty(None)
    alive = BooleanProperty(True)

    def spawn(self, img):
        t01 = TextureUtil.getTexture(img, self.region)
        self.texture = t01

    def update(self, dt):
        pass


class Obj01(BaseObj):

    v = (0, 0)

    g = 9.8 * 200

    def update(self, dt):

        # 落ちたら生存フラグをFalseにする
        if self.pos[1] + self.height < 0:
            self.alive = False

        # 速度を加算
        self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる


class Obj02(BaseObj):
    def affect(self, _obj01, dt):
        # 床 left, bottom, right, top
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
            # 地に足つける判定
            if obj02_top > obj01_bottom and obj01_bottom - _obj01.v[1] * dt >= obj02_top and (obj01_right != obj02_left and obj01_left != obj02_right):
                _obj01.pos[1] = obj02_top
                _obj01.v = (_obj01.v[0], 0)
            # 天井に頭ぶつける判定
            elif obj02_bottom < obj01_top and obj01_top - _obj01.v[1] * dt <= obj02_bottom and (obj01_right != obj02_left and obj01_left != obj02_right):
                _obj01.pos[1] = obj02_bottom - _obj01.height
                _obj01.v = (_obj01.v[0], -1 * _obj01.v[1])
                print(_obj01.pos[1])
            # 地に足つけてるときは横衝突判定はチェックしない（実は重なり部分がない状態でも接していればcollide_widgetがtrueになるらしいので）
            if _obj01.pos[1] != obj02_top:
                # 右にブロックがあるとき判定
                if obj02_left < obj01_right and obj01_right - _obj01.v[0] * dt <= obj02_left:
                    _obj01.pos[0] = obj02_left - _obj01.width
                    _obj01.v = (0, _obj01.v[1])
                # 左にブロックがあるとき判定
                elif obj02_right > obj01_left and obj01_left - _obj01.v[0] * dt >= obj02_right:
                    _obj01.pos[0] = obj02_right
                    _obj01.v = (0, _obj01.v[1])
