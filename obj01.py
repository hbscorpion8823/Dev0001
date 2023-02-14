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
            self.pos[1] = 0

        # 速度を加算
        self.v = (self.v[0], self.v[1] - dt * self.g)  # 下向きに重力加速度による速度加算が行われる


class Obj02(BaseObj):
    def affect(self, _obj01):
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
            Logger.info('Hoge: player=({},{})'.format(
                _obj01.pos[0], _obj01.pos[1]))
            # 地に足つける判定
            if obj02_top >= obj01_bottom and obj01_top > obj02_top and (self.center_x - 0.5 * _obj01.width - 0.5 * self.width < _obj01.center_x and self.center_x + 0.5 * _obj01.width + 0.5 * self.width > _obj01.center_x):
                if obj02_top >= obj01_bottom:
                    Logger.info('Hoge: case1-1')
                elif obj01_top > obj02_top:
                    Logger.info('Hoge: case1-2')
                elif obj01_right > obj02_left or obj01_left < obj02_right:
                    Logger.info('Hoge: case1-3')

                _obj01.pos[1] = obj02_top
                _obj01.v = (_obj01.v[0], 0)
            # 天井に頭ぶつける判定
            elif obj02_bottom <= obj01_top and obj01_bottom < obj02_bottom and (self.center_x - 0.5 * _obj01.width - 0.5 * self.width < _obj01.center_x and self.center_x + 0.5 * _obj01.width + 0.5 * self.width > _obj01.center_x):
                Logger.info('Hoge: case2')
                _obj01.pos[1] = obj02_bottom - _obj01.height
                _obj01.v = (_obj01.v[0], -1 * _obj01.v[1])
                print(_obj01.pos[1])

            # 右にブロックがあるとき判定
            if obj02_left < obj01_right and obj01_left < obj02_left and (self.center_y - 0.5 * _obj01.height - 0.5 * self.height < _obj01.center_y and self.center_y + 0.5 * _obj01.height + 0.5 * self.height > _obj01.center_y):
                Logger.info('Hoge: case3')
                _obj01.pos[0] = obj02_left - _obj01.width
                _obj01.v = (0, _obj01.v[1])
            # 左にブロックがあるとき判定
            elif obj02_right > obj01_left and obj01_right > obj02_right and (self.center_y - 0.5 * _obj01.height - 0.5 * self.height < _obj01.center_y and self.center_y + 0.5 * _obj01.height + 0.5 * self.height > _obj01.center_y):
                Logger.info('Hoge: case4')
                _obj01.pos[0] = obj02_right
                _obj01.v = (0, _obj01.v[1])
