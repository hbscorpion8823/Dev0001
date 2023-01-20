from kivy.uix.scatter import Scatter
from kivy.properties import ObjectProperty
from textureutil import TextureUtil
from kivy.uix.widget import Widget


class BaseObj(Widget):
    texture = ObjectProperty(None)

    def spawn(self, img):
        t01 = TextureUtil.getTexture(img, self.region)
        self.texture = t01


class Obj01(BaseObj):
    pass


class Obj02(BaseObj):
    pass
