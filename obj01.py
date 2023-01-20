from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty
from textureutil import TextureUtil
from kivy.uix.widget import Widget


class BaseObj(Widget):
    texture = ObjectProperty(None)

    def spawn(self, img):
        t01 = TextureUtil.getTexture(img, self.region)
        self.texture = t01

    def update(self, td):
        pass


class Obj01(BaseObj):

    v = (0, -1)

    def update(self, dt):
        self.pos = (self.pos[0] + self.v[0], self.pos[1] + self.v[1])


class Obj02(BaseObj):
    def keepoff(self, _obj01):
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
        if self.collide_widget(_obj01):
            if obj02_top > obj01_bottom:
                _obj01.pos[1] = obj02_top
