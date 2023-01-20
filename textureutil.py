from kivy.uix.image import Image


class TextureUtil:
    @staticmethod
    def getTexture(img, region):
        tex = img.texture
        return tex.get_region(region[0], region[1], region[2], region[3])
