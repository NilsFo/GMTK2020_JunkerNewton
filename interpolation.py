import math
from abc import abstractmethod


# https://github.com/libgdx/libgdx/blob/master/gdx/src/com/badlogic/gdx/math/Interpolation.java
# Thanks, LibGDX!
# <3


########################################################
########################################################

class Interpolation:

    @abstractmethod
    def apply(self, a: float) -> float:
        pass

    def interpolate(self, start: float, end: float, a: float):
        return start + (end - start) * self.apply(a)


########################################################
########################################################

class Linear(Interpolation):
    def apply(self, a: float) -> float:
        return a


class Smooth(Interpolation):
    def apply(self, a: float) -> float:
        return a * a * (3 - 2 * a)


class Smooth2(Interpolation):
    def apply(self, a: float) -> float:
        a = a * a * (3 - 2 * a)
        return a * a * (3 - 2 * a)


class Smoother(Interpolation):
    def apply(self, a: float) -> float:
        return a * a * a * (a * (a * 6 - 15) + 10)


########################################################

class Pow(Interpolation):
    def __init__(self, power: int):
        self.power = power

    def apply(self, a: float) -> float:
        if a <= 0.5:
            return float(pow(a * 2, self.power)) / 2

        div = None
        if self.power % 2 == 0:
            div = -2
        else:
            div = 2
        return float(pow((a - 1) * 2, self.power)) / div + 1


class PowIn(Pow):

    def __init__(self, power: int):
        super().__init__(power)

    def apply(self, a: float) -> float:
        return float(pow(a, self.power))


class PowOut(Pow):
    def __init__(self, power: int):
        super().__init__(power)

    def apply(self, a: float) -> float:
        div = None
        if self.power % 2 == 0:
            div = -1
        else:
            div = 1
        return float(pow(a - 1, self.power)) * div + 1


class Pow2InInverse(Interpolation):

    def apply(self, a: float) -> float:
        return float(math.sqrt(a))


class Pow2OutInInverse(Interpolation):

    def apply(self, a: float) -> float:
        return 1.0 - float(math.sqrt(-(a - 1.0)))


########################################################

class Sine(Interpolation):

    def apply(self, a: float) -> float:
        return (1.0 - math.cos(a * math.pi)) / 2.0


class SineIn(Interpolation):

    def apply(self, a: float) -> float:
        return 1.0 - math.cos(a * math.pi / 2.0)


class SineOut(Interpolation):

    def apply(self, a: float) -> float:
        return math.sin(a * math.pi / 2.0)


########################################################

class Circle(Interpolation):

    def apply(self, a: float) -> float:
        if a <= 0.5:
            a *= 2.0
            return (1.0 - float(math.sqrt(1.0 - a * a))) / 2.0
        a -= 1.0
        a *= 2.0
        return float(math.sqrt(1.0 - a * a) + 1.0) / 2.0


class CircleIn(Interpolation):

    def apply(self, a: float) -> float:
        return 1 - float(math.sqrt(1 - a * a))


class CircleOut(Interpolation):

    def apply(self, a: float) -> float:
        a -= 1.0
        return float(math.sqrt(1 - a * a))


########################################################

class Exp(Interpolation):

    def __init__(self, value: float, power: float):
        self.power = power
        self.value = value
        self.min = float(pow(value, -power))
        self.scale = 1 / (1 - self.min)

    def apply(self, a: float) -> float:
        if a <= 0.5:
            return (float(pow(self.value, self.power * (a * 2 - 1)) - self.min)) * self.scale / 2
        return (2 - (float(pow(self.value, -self.power * (a * 2 - 1)) - self.min)) * self.scale) / 2


class ExpIn(Exp):

    def __init__(self, value: float, power: float):
        super().__init__(value, power)

    def apply(self, a: float) -> float:
        return (float(pow(self.value, self.power * (a - 1)) - self.min)) * self.scale


class ExpOut(Exp):

    def __init__(self, value: float, power: float):
        super().__init__(value, power)

    def apply(self, a: float) -> float:
        return 1 - (float(pow(self.value, -self.power * a) - self.min)) * self.scale


########################################################

class Elastic(Interpolation):
    def __init__(self, value: float, power: float, bounces: int, scale: float):
        self.value = value
        self.power = power
        self.scale = scale

        adds = None
        if bounces % 2 == 0:
            adds = 1
        else:
            adds = -1

        self.bounces = bounces * math.pi * adds

    def apply(self, a: float) -> float:
        if a <= 0.5:
            a *= 2
            return float(pow(self.value, self.power * (a - 1))) * math.sin(a * self.bounces) * self.scale / 2
        return 1 - float(pow(self.value, self.power * (a - 1))) * math.sin(a * self.bounces) * self.scale / 2


class ElasticIn(Elastic):

    def __init__(self, value: float, power: float, bounces: int, scale: float):
        super().__init__(value, power, bounces, scale)

    def apply(self, a: float):
        if a >= 0.99:
            return 1.0
        return float(pow(self.value, self.power * (a - 1.0))) * math.sin(a * self.bounces) * self.scale


class ElasticOut(Elastic):

    def __init__(self, value: float, power: float, bounces: int, scale: float):
        super().__init__(value, power, bounces, scale)

    def apply(self, a: float):
        if a == 0:
            return 0.0
        a = 1 - a
        return 1 - float(pow(self.value, self.power * (a - 1))) * math.sin(a * self.bounces) * self.scale


########################################################


class BounceOut(Interpolation):
    def __init__(self, bounces: int):
        self.widths = [0.0] * bounces
        self.heights = [0.0] * bounces
        self.heights[0] = 1.0

        if bounces == 2:
            self.widths[0] = 0.6
            self.widths[1] = 0.4
            self.heights[1] = 0.33
        elif bounces == 3:
            self.widths[0] = 0.4
            self.widths[1] = 0.4
            self.widths[2] = 0.2
            self.heights[1] = 0.33
            self.heights[2] = 0.1
        elif bounces == 4:
            self.widths[0] = 0.34
            self.widths[1] = 0.34
            self.widths[2] = 0.2
            self.widths[3] = 0.15
            self.heights[1] = 0.26
            self.heights[2] = 0.11
            self.heights[3] = 0.03
        elif bounces == 5:
            self.widths[0] = 0.3
            self.widths[1] = 0.3
            self.widths[2] = 0.2
            self.widths[3] = 0.1
            self.widths[4] = 0.1
            self.heights[1] = 0.45
            self.heights[2] = 0.3
            self.heights[3] = 0.15
            self.heights[4] = 0.06
        else:
            raise ValueError("Number of bounces need to be between 2 and 5")

        self.widths[0] = self.widths[0] * 2

    def apply(self, a: float) -> float:
        if a == 1:
            return 1
        a = a + self.widths[0] / 2
        width = 0.0
        height = 0.0

        for i in range(len(self.widths)):
            width = self.widths[i]
            if a <= width:
                height = self.heights[i]
                break
            a = a - width

        a = a / width
        z = float(4 / width * height * a)
        return 1 - (z - z * a) * width


class BounceIn(BounceOut):
    def __init__(self, bounces: int):
        super().__init__(bounces)

    def apply(self, a: float) -> float:
        return 1.0 - super().apply(1 - a)


class Bounce(BounceOut):
    def __init__(self, bounces: int):
        super().__init__(bounces)

    def out(self, a: float):
        t = float(a + self.widths[0] / 2)
        if t < self.widths[0]:
            return t / (self.widths[0] / 2) - 1
        return super().apply(a)

    def apply(self, a: float) -> float:
        if a <= 0.5:
            return (1 - self.out(1 - a * 2)) / 2
        return self.out(a * 2 - 1) / 2 + 0.5


########################################################

class Swing(Interpolation):
    def __init__(self, scale: float):
        self.scale = scale * 2.0

    def apply(self, a: float):
        if a <= 0.5:
            a = a * 2.0
            return a * a * ((self.scale + 1.0) * a - self.scale) / 2.0

        a = a - 1
        a = a * 2
        return a * a * ((self.scale + 1) * a + self.scale) / 2.0 + 1


class SwingOut(Interpolation):
    def __init__(self, scale: float):
        self.scale = scale

    def apply(self, a: float) -> float:
        a = a - 1
        return a * a * ((self.scale + 1) * a + self.scale) + 1


class SwingIn(Interpolation):
    def __init__(self, scale: float):
        self.scale = scale

    def apply(self, a: float) -> float:
        return a * a * ((self.scale + 1) * a - self.scale)


########################################################
# Custom Class defs
########################################################

# y = -4 (-1 + x) x
class ParabolicLoop(Interpolation):

    def apply(self, a: float) -> float:
        return -4 * (-1 + a) * a


########################################################
# Class defs done. Here are some helper functions
# for default interpolations, according to the webside
########################################################

def elastic():
    return Elastic(2.0, 10.0, 7, 1.0)


def elastic_in():
    return ElasticIn(2.0, 10.0, 6, 1.0)


def elastic_out():
    return ElasticOut(2.0, 10.0, 7, 1.0)


def swing():
    return Swing(1.5)


def swing_in():
    return SwingIn(2.0)


def swing_out():
    return SwingOut(2.0)


def bounce():
    return Bounce(4)


def bounce_in():
    return BounceIn(4)


def bounce_out():
    return BounceOut(4)


def exp10():
    return Exp(2.0, 10.0)


def exp10_in():
    return ExpIn(2.0, 10.0)


def exp10_out():
    return ExpOut(2.0, 10.0)


def exp5():
    return Exp(2.0, 5.0)


def exp5_in():
    return ExpIn(2.0, 5.0)


def exp5_out():
    return ExpOut(2.0, 5.0)


def pow4():
    return Pow(4)


def pow4_in():
    return PowIn(4)


def pow4_out():
    return PowOut(4)


def pow5():
    return Pow(5)


def pow5_in():
    return PowIn(5)


def pow5_out():
    return PowOut(5)


def pow3():
    return Pow(3)


def pow3_in():
    return PowIn(3)


def pow3_out():
    return PowOut(3)


def pow2():
    return Pow(2)


def pow2_in():
    return PowIn(2)


def pow2_out():
    return PowOut(2)
