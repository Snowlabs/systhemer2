"""Utilities and types for the value system.

Values to be parsed by configuration files have to be somehow defined.
That is the purpose of the types contained in this module. Each
subclass of Value defines a certain configuration value to be parsed.

e.g. Color, Keybind, etc.
"""

from enum import Enum
import logging
import regex as re


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

        conversions = {'x': lambda v, l: int(v, 16)/((16**l)-1)}
        keys_types = {}
        keys_lengths = {}

        def subfn(m):
            print(m.group(1))
            keys_types[m.group(1)[1]] = m.group(1)[0]
            keys_lengths[m.group(1)[1]] = len(m.group(1)[1:])
            return '(?P<%s>%s)' % (m.group(1)[1], (r'.'*len(m.group(1)[1:])))

        color_format_re = re.sub(r'\{((?:[^}]|\\\})*)\}', subfn, color_format)
        match = re.search(color_format_re, color)
        print(match.groupdict())
        for k in match.groupdict():
            if k in 'RGBA':
                setattr(self, k,
                        conversions[keys_types[k]](
                            match.groupdict()[k],
                            keys_lengths[k]))
        print(self)

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
