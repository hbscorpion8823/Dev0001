from kivy.properties import ObjectProperty
import math
from dataclasses import dataclass


@dataclass
class PosTime:
    pos: tuple
    currentTime: float


class PosTimeUtil:
    @staticmethod
    def getDeltaX(p1, p2):
        return p2.pos[0] - p1.pos[0]

    @staticmethod
    def getDeltaY(p1, p2):
        return p2.pos[1] - p1.pos[1]

    @staticmethod
    def getAngle(p1, p2):
        # x, yの差分を出す
        dx = PosTimeUtil.getDeltaX(p1, p2)
        dy = PosTimeUtil.getDeltaY(p1, p2)
        if dx == 0 and dy == 0:
            return None
        # 差分ベクトルからsin(正弦)を算出
        sinTheta = dy / math.sqrt(dx * dx + dy * dy)
        # 逆正弦をとって、角度を算出（ラジアン単位）
        return math.asin(sinTheta)

    @staticmethod
    def getSinTheta(p1, p2):
        # x, yの差分を出す
        dx = PosTimeUtil.getDeltaX(p1, p2)
        dy = PosTimeUtil.getDeltaY(p1, p2)
        if dx == 0 and dy == 0:
            return None
        # 差分ベクトルからsin(正弦)を算出
        return dy / math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def getVx(p1, p2):
        dx = p2.pos[0] - p1.pos[0]
        dt = p2.currentTime - p1.currentTime
        v = dx / dt
        if abs(v) > 1200:
            if v < 0:
                return -1200
            else:
                return 1200
        else:
            return v

    @staticmethod
    def getVy(p1, p2):
        dy = p2.pos[1] - p1.pos[1]
        dt = p2.currentTime - p1.currentTime
        v = dy / dt
        if v > 1200:
            return 1200
        else:
            return v
