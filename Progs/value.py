"""Utilities and types for the value system.

Values to be parsed by configuration files have to be somehow defined.
That is the purpose of the types contained in this module. Each
subclass of Value defines a certain configuration value to be parsed.

e.g. Color, Keybind, etc.
"""

import itertools
from enum import Enum
from . import common
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
    bases = {'x': 16, 'X': 16, 'd': 10}
    max_digits = 2

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

        # return max value possible for number of `base` and of `length` digits
        def getmax(base, length):
            return (base**length)-1

        values = {}

        keys = 'RGBA'
        range_digits = range(1, self.max_digits+1)

        for val, bchar, num_digits in itertools.product(keys,
                                                        self.bases,
                                                        range_digits):
            # key
            k = bchar + (val * num_digits)

            # generate format and apply it with values from `value`
            fmat = '{:0>%s%s}' % (num_digits, bchar)
            mult = getmax(self.bases[bchar], num_digits)
            v = fmat.format(round(value[val] * mult))

            # save pair in `values`
            values[k] = v

        # apply format with pre-formatted values
        return self.fmat.format(**values)

    def parse(self, string):
        """Parse `string` with format and extract rgba values"""
        def convert(string, base):
            return int(string, base)/((base**len(string))-1)

        def subfn(m):
            key_type = m.group(1)[0].lower()
            key = m.group(1)[1]
            digits = len(m.group(1)[1:])

            keys_types[key] = key_type
            return '(?P<%s>%s)' % (key, (r'.'*digits))

        # dict of shorthands for getting values of different bases
        conversions = {}
        for bchar, base in self.bases.items():
            conversions[bchar] = lambda v, b=base: convert(v, b)

        keys_types = {}

        # generate regular expression
        # looking for groups delimited by `{}`
        # and passing the match objs to subfn
        color_format_re = re.sub(r'\{((?:[^}]|\\\})*)\}', subfn, self.fmat)

        # extract values from `color` string using generated regexpr
        match = re.search(color_format_re, string)
        self.logger.log(common.Settings.VDEBUG, match.groupdict())

        # construct out_obj Color object
        out_obj = Color()

        for k, value in match.groupdict().items():
            if k in 'RGBA':
                k_type = keys_types[k]

                convert_fun = conversions[k_type]
                attr_val = convert_fun(value)

                out_obj[k] = attr_val  # set value to out_obj.{KEY}
        self.logger.log(common.Settings.VDEBUG, out_obj)

        return out_obj


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

    def __init__(self, *args, **kwargs):
        """Set RGBA values according to tuple of floats from 0 to 1
        can take in a tuple/list of rgb/rgba values
        and/or keyword arguments of rgba values: R=0.1, g=0.7
        """
        # get logger
        self.logger = logging.getLogger('Systhemer.value.ColorFormat')

        # save values
        valid_arguments = True

        if len(args) == 1:
            if type(args[0]) in (tuple, list):
                if len(args[0]) == 3:
                    self.R, self.G, self.B = args[0]
                elif len(args[0]) == 4:
                    self.R, self.G, self.B, self.A = args[0]
                else:
                    valid_arguments = False
        elif len(args) == 3:
            self.R, self.G, self.B = args
        elif len(args) == 4:
            self.R, self.G, self.B, self.A = args
        elif len(args) != 0:
            valid_arguments = False

        for kwarg in kwargs:
            self[kwarg.upper()] = kwargs[kwarg]

        if not valid_arguments:
            self.logger.critical('Invalid arguments passed to constructor!')
            exit(1)

        # validate attributes
        for attr in 'RGBA':
            if self[attr] > 1 or self[attr] < 0:
                self.logger.critical('RGBA values not all from 0 to 1!: %s',
                                     self)
                exit(1)

    def __getitem__(self, key):
        if key in 'RGBA':
            return getattr(self, key)
        else:
            raise KeyError()

    def __setitem__(self, key, value):
        if key in 'RGBA':
            if value is str:
                if value[0] in ['x', '0x', 'X', '0X']:
                    value = int(value, 16)
                elif value == 'nan':
                    raise ValueError('float value `nan` not supported')

            value = float(value)
            if value < 0 or value > 1:
                raise ValueError('Value must be beetween 0 and 1!')

            setattr(self, key, value)

        else:
            raise KeyError()

    def __repr__(self):
        return self.__class__.__name__ + '(%f, %f, %f, %f)' \
                % (self.R, self.G, self.B, self.A)

    def __str__(self):
        return repr(self)

    def format(self, fmat):
        """Calls formatter.format to allow pipeline structured code.

        Essentially reverses the fmatter.format(value_obj)
                              to value_obj.format(fmatter)

        the `fmat` parameter can be a string from which the formatter object
        will be generated or it can be a formatter object directly
        """
        if type(fmat) is str:
            return ColorFormat(fmat).format(self)
        elif isinstance(fmat, ColorFormat):
            return fmat.format(self)
