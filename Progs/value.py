"""Utilities and types for the value system.

Values to be parsed by configuration files have to be somehow defined.
That is the purpose of the types contained in this module. Each
subclass of Value defines a certain configuration value to be parsed.

e.g. Color, Keybind, etc.
"""

import itertools
# from enum import Enum
# from . import common
# from .common import utils
from .common import utils
import logging
import regex as re


class PipelineableObject(object):
    def __init__(self, fmat_obj, obj):
        self.obj = obj
        self.fmat = fmat_obj

    def __str__(self):
        return 'pipelineable_object ' + str(self.obj)

    def __repr__(self):
        # imperfect repr function...
        return 'pipelineable_object(' + repr(self.obj) + ')'

    def non_existant(self, meth_name):
        raise AttributeError('This PipelineableObject object does '
                             'not contain method: \'%s()\'!' % meth_name)

    def format(self, pipeline=False):
        if isinstance(self.obj, Value):
            return self.fmat.format(self.obj, pipeline=pipeline)
        else:
            self.non_existant('format')

    def parse(self, pipeline=False):
        if isinstance(self.obj, str):
            return self.fmat.parse(self.obj, pipeline=pipeline)
        else:
            self.non_existant('parse')


class Value(object):
    class Formats:
        """Implementation not necessary but makes code more readable"""
        pass

    class Formatter(object):
        @staticmethod
        def get_type():
            """Must be implemented"""
            raise NotImplementedError()

        def __init__(self, fmat):
            # For now, (until i can figure it out,) it displays logger class
            # as Systhemer.value.Value.Formatter instead of actual
            # instance parent class name :(
            # TODO: fix issue explained above
            self.logger = logging.getLogger('Systhemer.value.%s.%s'
                                            % ('Value',  # fix this!
                                               self.__class__.__name__))
            self.fmat = fmat

        def __repr__(self):
            return self.__class__.__name__ + '(\'%s\')' % self.fmat

        def format(self, value, pipeline=False):
            """Must be implemented"""
            raise NotImplementedError()

        def parse(self, string, pipeline=False):
            """Must be implemented"""
            raise NotImplementedError()

        def get_rgx(self):
            return r'(\S+)'

        @staticmethod
        def get_format(s):
            """Must be implemented"""
            raise NotImplementedError()

        @staticmethod
        def auto_parse(s, pipeline=False):
            """Must be implemented"""
            raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        """Must be implemented"""
        raise NotImplementedError()

    def __getitem__(self, key):
        """Must be implemented"""
        raise NotImplementedError()

    def __setitem__(self, key, value):
        """Must be implemented"""
        raise NotImplementedError()

    def __repr__(self):
        """Must be implemented"""
        raise NotImplementedError()

    def __str__(self):
        """Must be implemented"""
        raise NotImplementedError()

    def format(self, fmat, pipeline=False):
        """Must be implemented"""
        raise NotImplementedError()


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

    class formats:
        """Enum of supported color formats."""

        hexRGB = '#{xR}{xG}{xB}'
        hexRRGGBB = '#{xRR}{xGG}{xBB}'
        hexAARRGGBB = '#{xAA}{xRR}{xGG}{xBB}'
        hexRRGGBBAA = '#{xRR}{xGG}{xBB}{xAA}'

        floRGB = 'rgb.f({fR_n},{fG_n},{fB_n})'
        decRGB = 'rgb({dRR},{dGG},{dBB})'

    class Formatter(Value.Formatter):
        @staticmethod
        def get_type():
            return Color

        bases = {'x': 16, 'X': 16, 'd': 10, 'f': 10}
        max_digits = 2

        def __init__(self, *args, **kwargs):
            def float_gen(value):
                out = {}
                for val in 'RGBA':
                    out['f%s_n' % val] = value[val]
                return out

            def float_sub(m):
                if m.group(1)[0] == 'f' and m.group(1)[2:] == '\_n':
                    return '(?P<%s>[+-]?(?:[0-9]*[.])?[0-9]+)' % m.group(1)[1]

            def float_conv(bchar):
                if bchar == 'f':
                    return lambda v: float(v)

            super(self.__class__, self).__init__(*args, **kwargs)
            self.extra_val_gens = [float_gen]
            self.extra_val_subs = [float_sub]
            self.extra_val_convs = [float_conv]

        def format(self, value, pipeline=False):
            """Return color according to color_format."""

            # return max value possible for number of `base`
            # and of `length` digits
            def getmax(base, length):
                return (base**length)-1

            values = {}

            keys = 'RGBA'
            range_digits = range(1, self.max_digits+1)

            for val, bchar, num_digits in itertools.product(keys,
                                                            self.bases.keys(),
                                                            range_digits):
                # key
                k = bchar + (val * num_digits)

                # generate format and apply it with values from `value`
                fmat = '{:0>%s%s}' % (num_digits, bchar)
                mult = getmax(self.bases[bchar], num_digits)
                v = fmat.format(round(value[val] * mult))

                # save pair in `values`
                values[k] = v

            for func in self.extra_val_gens:
                values.update(func(value))

            # print(values)

            # apply format with pre-formatted values
            out_str = self.fmat.format(**values)

            if pipeline:
                return PipelineableObject(self, out_str)
            return out_str

        def parse(self, string, pipeline=False):
            """Parse `string` with format and extract rgba values"""

            def convert(string, base):
                return int(string, base)/((base**len(string))-1)

            def subfn(m):
                _fmat = m.group(1)

                key_type = _fmat[0].lower()
                key = _fmat[1]
                keys_types[key] = key_type
                digits = len(_fmat[1:])

                for func in self.extra_val_subs:
                    o = func(m)
                    if o is not None:
                        return o

                return '(?P<%s>%s)' % (key, (r'.'*digits))

            # dict of shorthands for getting values of different bases
            conversions = {}
            for bchar, base in self.bases.items():
                for func in self.extra_val_convs:
                    conv = func(bchar)
                    if conv is not None:
                        conversions[bchar] = conv
                        break
                else:
                    conversions[bchar] = lambda v, b=base: convert(v, b)

            # escape fmat and unescape '{' '}' chars afterwards
            fmat = re.escape(self.fmat)
            fmat = re.sub(r'(\\\{|\\\})',
                          lambda m: '{' if m.group() == r'\{' else '}', fmat)

            # generate regular expression
            # looking for groups delimited by `{}`
            # and passing the match objs to subfn
            # NOTE: subfn side effect: modifies keys_types
            keys_types = {}
            color_format_re = re.sub(r'\{((?:[^}]|\\\})*)\}', subfn, fmat)
            # print(self.fmat, color_format_re)

            # extract values from `color` string using generated regexpr
            match = re.search(color_format_re, string)
            self.logger.log(utils.get_setting('VDEBUG'), match.groupdict())

            # construct out_obj Color object
            out_obj = Color()

            for k, value in match.groupdict().items():
                if k in 'RGBA':
                    k_type = keys_types[k]

                    convert_fun = conversions[k_type]
                    attr_val = convert_fun(value)

                    out_obj[k] = attr_val  # set value to out_obj.{KEY}
            self.logger.log(utils.get_setting('VDEBUG'), out_obj)

            if pipeline:
                return PipelineableObject(self, out_obj)
            return out_obj

        @staticmethod
        def get_format(s):
            fmat = ''
            if s[0] == '#':
                body_len = len(s[1:])
                if body_len == 3:
                    fmat = Color.formats.hexRGB
                elif body_len == 6:
                    fmat = Color.formats.hexRRGGBB
                elif body_len == 8:
                    fmat = Color.formats.hexRRGGBBAA
            elif s[:3] == 'rgb' and s[-1] == ')':
                if s[3:6] == '.f(':
                    fmat = Color.formats.floRGB
                elif s[3:4] == '(':
                    fmat = Color.formats.decRGB

            if fmat:
                return Color.Formatter(fmat)
            else:
                logging.getLogger('Systhemer.Color.Formatter').critical(
                        'Format not found for \'%s\'', s)

        @staticmethod
        def auto_parse(s, pipeline=False):
            return Color.Formatter.get_format(s).parse(s, pipeline=pipeline)

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

    # NOTE: this method is NOT obsolete even with the new `pipeline` option
    def format(self, fmat, pipeline=False):
        """Calls formatter.format to allow pipeline structured code.

        Essentially reverses the fmatter.format(value_obj)
                              to value_obj.format(fmatter)

        the `fmat` parameter can be a string from which the formatter object
        will be generated or it can be a formatter object directly
        """

        if type(fmat) is str:
            return self.Formatter(fmat).format(self, pipeline=pipeline)
        elif isinstance(fmat, Value.Formatter):
            return fmat.format(self, pipeline=pipeline)


class Litteral(Value):
    class Formatter(Value.Formatter):
        @staticmethod
        def get_type():
            return Litteral

        def __init__(self):
            """String litteral value type"""
            # For now, (until i can figure it out,) it displays logger class
            # as Systhemer.value.Value.Formatter instead of actual
            # instance parent class name :(
            # TODO: fix issue explained above
            self.logger = logging.getLogger('Systhemer.value.%s.%s'
                                            % ('Value',  # fix this!
                                               self.__class__.__name__))

        def __repr__(self):
            return self.__class__.__name__ + '()'

        def format(self, value, pipeline=False):
            out_str = value.s
            if pipeline:
                return PipelineableObject(self, out_str)
            return out_str

        def parse(self, string, pipeline=False):
            out_obj = Litteral(string)
            if pipeline:
                return PipelineableObject(self, out_obj)
            return out_obj

        @staticmethod
        def auto_parse(s, pipeline=False):
            return Litteral.Formatter().parse(s, pipeline=pipeline)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'Litteral(\'%s\')' % self.s

    def __str__(self):
        return repr(self)

    def format(self, pipeline=False):
        """Useless and only for modularity sake"""
        return self.Formatter().format(self, pipeline=pipeline)
