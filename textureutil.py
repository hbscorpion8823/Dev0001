from kivy.uix.image import Image
from decimal import Decimal


class TextureUtil:
    @staticmethod
    def getTexture(img, region):
        tex = img.texture
        return tex.get_region(Decimal(str(region[0])), Decimal(str(region[1])), Decimal(str(region[2])), Decimal(str(region[3])))
