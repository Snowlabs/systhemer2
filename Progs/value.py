"""Utilities and types for the value system.

Values to be parsed by configuration files have to be somehow defined.
That is the purpose of the types contained in this module. Each
subclass of Value defines a certain configuration value to be parsed.

e.g. Color, Keybind, etc.
"""

from enum import Enum


# TO BE DECIDED
# This may be removed
# ColorFormat may also be a subclass of a more varied
# format class.
class ColorFormat(Enum):
    """Enum of supported color formats."""

    hexRGB = 1
    hexRRGGBB = 2
    hexAARRGGBB = 3
    hexRRGGBBAA = 4


class Value(object):

    def get(self, format):
        raise NotImplementedError()


# TODO: logging?
class Color(Value):
    """Value subclass for colors.

    Stores red, green, blue and alpha channels in separate variables.
    Range from 0 - 1 each. By default, they are 0, 0, 0 and 1
    respectively.
    """

    R = 0
    G = 0
    B = 0
    A = 1

    def __init__(self, color, color_format):
        """Convert color according to color_format."""

        # Check for every supported color format and store accordingly
        # TODO: implement regex?
        if color_format is ColorFormat.hexRGB:
            self.R = int(color[1], 16) / 15
            self.G = int(color[2], 16) / 15
            self.B = int(color[3], 16) / 15

        elif color_format is ColorFormat.hexRRGGBB:
            self.R = int(color[1:3], 16) / 255
            self.G = int(color[3:5], 16) / 255
            self.B = int(color[5:7], 16) / 255

        elif color_format is ColorFormat.hexAARRGGBB:
            self.A = int(color[1:3], 16) / 255
            self.R = int(color[3:5], 16) / 255
            self.G = int(color[5:7], 16) / 255
            self.B = int(color[7:9], 16) / 255

        elif color_format is ColorFormat.hexRRGGBBAA:
            self.R = int(color[1:3], 16) / 255
            self.G = int(color[3:5], 16) / 255
            self.B = int(color[5:7], 16) / 255
            self.A = int(color[7:9], 16) / 255

    def __getitem__(self, key):
        if key is 'R':
            return self.R

        elif key is 'G':
            return self.G

        elif key is 'B':
            return self.B

        elif key is 'A':
            return self.A

    def get(self, color_format):
        """Return color according to color_format."""

        r = ''

        if color_format is ColorFormat.hexRGB:
            r = '#'

            for c in [self.R, self.G, self.B]:
                r += hex(round(c * 16))[2:]

        elif color_format is ColorFormat.hexRRGGBB:
            r = '#'

            for c in [self.R, self.G, self.B]:
                r += '0' if round(c * 255) < 16 else ''
                r += hex(round(c * 255))[2:]

        elif color_format is ColorFormat.hexAARRGGBB:
            r = '#'

            for c in [self.A, self.R, self.G, self.B]:
                r += '0' if round(c * 255) < 16 else ''
                r += hex(round(c * 255))[2:]

        elif color_format is ColorFormat.hexRRGGBBAA:
            r = '#'

            for c in [self.R, self.G, self.B, self.A]:
                r += '0' if round(c * 255) < 16 else ''
                r += hex(round(c * 255))[2:]

        return r
