from kivy.properties import ObjectProperty
import math
from dataclasses import dataclass
from kivy.logger import Logger


@dataclass
class PosTime:
    """ kivyのtouch_moveでは時間を管理していないので、位置とシステム時間を記録するデータクラスによって管理する """
    pos: tuple
    currentTime: float = None


class PosTimeUtil:
    @staticmethod
    def getDeltaX(p1, p2):
        return p2.pos[0] - p1.pos[0]

    @staticmethod
    def getDeltaY(p1, p2):
        return p2.pos[1] - p1.pos[1]

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
    def getCosTheta(p1, p2):
        # x, yの差分を出す
        dx = PosTimeUtil.getDeltaX(p1, p2)
        dy = PosTimeUtil.getDeltaY(p1, p2)
        if dx == 0 and dy == 0:
            return None
        # 差分ベクトルからcos(余弦)を算出
        return dx / math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def getVx(p1, p2):
        dx = p2.pos[0] - p1.pos[0]
        dt = p2.currentTime - p1.currentTime
        if dt == 0:
            return 0 # 0除算阻止

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
        if dt == 0:
            return 0 # 0除算阻止
        v = dy / dt
        if v > 1200:
            return 1200
        else:
            return v
