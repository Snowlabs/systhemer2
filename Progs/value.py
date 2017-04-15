"""Utilities and types for the value system.

Values to be parsed by configuration files have to be somehow defined.
That is the purpose of the types contained in this module. Each
subclass of Value defines a certain configuration value to be parsed.

e.g. Color, Keybind, etc.
"""

from enum import Enum
import logging


class Value(object):

    def get(self, format):
        raise NotImplementedError()


# TO BE DECIDED
# This may be removed
# ColorFormat may also be a subclass of a more varied
# format class.
class ColorFormat(object):
    class formats:
        """Enum of supported color formats."""

        hexRGB = '#{xR}{xG}{xB}'
        hexRRGGBB = '#{xRR}{xGG}{xBB}'
        hexAARRGGBB = '#{xAA}{xRR}{xGG}{xBB}'
        hexRRGGBBAA = '#{xRR}{xGG}{xBB}{xAA}'

    def __init__(self, fmat):
        self.logger = logging.getLogger('Systhemer.value.ColorFormat')
        self.fmat = fmat

    def __repr__(self):
        return self.__class__.__name__ + '(\'%s\')' % self.fmat

    def format(self, value):
        """Return color according to color_format."""
        values = {}
        for val in 'RGBA':
            values.update({
                'x'+val:     '{:x}'.format(round(value[val] * 16)),
                'X'+val:     '{:X}'.format(round(value[val] * 16)),
                'x'+(val*2): '{:0>2x}'.format(round(value[val] * 255)),
                'X'+(val*2): '{:0>2X}'.format(round(value[val] * 255)),
                })

        return self.fmat.format(**values)


# TODO: logging?
# TODO: Figure out a better way of parsing the values (better than hardcoding)
class Color(Value):
    """Value subclass for colors.

    Stores red, green, blue and alpha channels in separate attributes.
    Range from 0 - 1 each. By default, they are 0, 0, 0 and 1
    respectively.
    """

    R = 0
    G = 0
    B = 0
    A = 1

    def __init__(self, color, color_format):
        """Convert color according to color_format."""

        self.color = color
        self.color_format = color_format

        # Check for every supported color format and store accordingly
        # TODO: implement regex?... maybe...???
        if color_format is ColorFormat.formats.hexRGB:
            self.R = int(color[1], 16) / 15
            self.G = int(color[2], 16) / 15
            self.B = int(color[3], 16) / 15

        elif color_format is ColorFormat.formats.hexRRGGBB:
            self.R = int(color[1:3], 16) / 255
            self.G = int(color[3:5], 16) / 255
            self.B = int(color[5:7], 16) / 255

        elif color_format is ColorFormat.formats.hexAARRGGBB:
            self.A = int(color[1:3], 16) / 255
            self.R = int(color[3:5], 16) / 255
            self.G = int(color[5:7], 16) / 255
            self.B = int(color[7:9], 16) / 255

        elif color_format is ColorFormat.formats.hexRRGGBBAA:
            self.R = int(color[1:3], 16) / 255
            self.G = int(color[3:5], 16) / 255
            self.B = int(color[5:7], 16) / 255
            self.A = int(color[7:9], 16) / 255

    def __getitem__(self, key):
        if key in 'RGBA':
            return getattr(self, key)
        else:
            raise KeyError()

    def __repr__(self):
        return self.__class__.__name__ + '(\'%s\', \'%s\')' \
                % (self.color, self.color_format)

    def __str__(self):
        return self.__class__.__name__ + '(%f, %f, %f, %f)' \
                % (self.R, self.G, self.B, self.A)
