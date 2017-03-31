"""Utilities for managing Rules.

This module contains classes and functions for generating rules for
searching and replacing text using regex.

Classes:
    * `ConfigElement` - Base class. Others derive from this one
    * `RuleTree` - Tree containing `ConfigElement` objects
    * `Rule` - A single rule defined using regex
    * `RuleVLen` - Like `Rule` but of variable length
    * `Section` - Section of file to isolate from the rest
"""


import logging
import regex
logger = logging.getLogger('Systhemer.Progs.common')
Settings = None


def get_home_dir():
    """Get home directory for the user.
    """
    from os.path import expanduser
    return expanduser('~')


class utils(object):
    """Namespace for basic utilities.
    """
    @staticmethod
    def is_excluded(exclude_rule, check_range):
        """ Check if the given range is within the exclude rule.

        * `exclude_rule`: (depth, startpos, endpos)
        * `check_range`:  (startpos, endpos)

        Returns:

        * **1** if range is completely in the exclude range
        * **2** if range is partially in the exclude range
        * **0** if range is not at all in the exclude range
        """
        if check_range[0] > check_range[1]:
            logger = logging.getLogger('Systhemer.common.utils')
            logger.critical('Range makes no sense!'
                            ' Startpos is bigger than endpos!')
            exit(1)
        if (check_range[0] in range(exclude_rule[1], exclude_rule[2]+1)) and \
           (check_range[1] in range(exclude_rule[1], exclude_rule[2]+1)):
            return 1
        if (check_range[0] in range(exclude_rule[1], exclude_rule[2]+1)) or \
           (check_range[1] in range(exclude_rule[1], exclude_rule[2]+1)):
            return 2
        return 0


class ConfigElement(object):
    parent = None
    tree = None

    def build_hierarchy_tree(self):
        """Generate hierarchy tree for Rule object.
        """

        assert isinstance(self.parent, ConfigElement) or self.parent is None
        self.tree = [e for e in self.parent.get_tree()] if self.parent else []
        self.tree.append(self)
        logger.log(Settings.VDEBUG, 'tree generated: %s', self.tree)
        return self.tree

    def get_tree(self, force_rebuild=False):
        """Generate hierarchy tree if needed and return it
        """
        if self.tree:
            logger.debug('hierarchy tree already exists...')
            if force_rebuild:
                logger.debug('force_rebuild was true, '
                             'rebuilding hierarchy tree...')
                return self.build_hierarchy_tree()
            return self.tree
        else:
            logger.debug('initializing hierarchy tree...')
            return self.build_hierarchy_tree()


class RuleTree(ConfigElement):
    """Tree for any subclass of `ConfigElement`.

    This class is used to build a tree for defining complex rules. It's
    essentially possible to include itself, as `RuleTree` is also a
    subclass of `ConfigElement`.
    """
    def __init__(self, *args):
        """Build the rule tree from `*args`.

        * `*args` - Comma separated `ConfigElement` types
        """

        self.logger = logger
        self.leaves = None
        self.rules = args
        for r in self.rules:
            r.parent = self

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, key):
        return self.rules[key]

    def _get_leaves(self, section_obj):
        out = []
        for ro in section_obj:
            if isinstance(ro, Section):
                out.extend(self._get_leaves(ro))
            elif isinstance(ro, Rule):
                out.append(ro)
            # invalid type
            else:
                self.logger.critical('Member or descendant of self.config'
                                     ' has invalid type: \'%s\'',
                                     ro.__class__)
                exit(1)
        return out

    def build_leaves_list(self):
        self.leaves = self._get_leaves(self)
        self.logger.log(Settings.VDEBUG, 'leaves list generated: %s',
                        self.leaves)
        return self.leaves

    def get_leaves(self, force_rebuild=False):
        """Build the array of leaves if not already built and return it.
        """

        if self.leaves:
            self.logger.debug('leaves array already exists...')
            if force_rebuild:
                self.logger.debug('force_rebuild was true, '
                                  'rebuilding leaves array...')
                return self.build_leaves_list()
            return self.leaves
        else:
            self.logger.debug('initializing leaves array...')
            return self.build_leaves_list()


class Rule(ConfigElement):
    """A simple configuration line to search for.

    This `Rule` only works if the line of the regex is fixed.
    If not, use the `RuleVLen` class.
    """
    def __init__(self, rule, keys):
        """Build the `Rule` object.

        Example::

            border_color 'foo' 'bar'

        * `rule`: regex to search for
                In this case:
                r'border_color' + r'([ \t]+(\S+))'*2

        * `keys`: dictionary specifying what to set in the config file
                - Key: variable from global config file to be used
                - Value: number specifying the capture group
        """
        self.rule = rule
        self.keys = keys
        self.logger = logging.getLogger('Systhemer.Progs.common.'
                                        + self.__class__.__name__)

    def _set(self, key, value, _buffer, scope_range, exclude_ranges):
        # Construct a list of all matches of 'rule' in the proper scope that
        # aren't excluded by any of the rules in exclude_ranges
        print(self.rule)
        matches = []
        for m in regex.finditer(self.rule,
                                _buffer[scope_range[0]:scope_range[1]]):
            excs = [utils.is_excluded(r, (m.start()+scope_range[0],
                                          m.end()+scope_range[0])) != 0
                    for r in exclude_ranges]
            if not (True in excs):
                matches.append(m)

        # check if empty list
        if matches:
            # for now, we only apply the value to the first key match
            match = matches[0]
        else:
            self.logger.warning('Found rule \'%s\' in program definition'
                                ' but not in configuration file!',
                                key)
            return None

        # replace the value in the buffer and return it
        sub_id = self.keys[key]
        out_buffer = _buffer[:scope_range[0]+match.start(sub_id)] \
            + value \
            + _buffer[scope_range[0]+match.end(sub_id):]
        self.logger.debug('Value set: %s <- %s', key, value)
        return out_buffer


class RuleVLen(Rule):
    """Similar to the `Rule` class, supports variable length matching
    """
    def __init__(self, rule, keys):
        """Build a `RuleVLen` object

        Example::

            border_color 'foo' 'bar' 'baz'

        * `rule`: regex to search for
                In this case:
                r'border_color(?:[ \t]+(\S+)){1,3}'

                In this case, the capture group '(\S+)' can be
                captured many times (from 1 to 3 times)

        * `keys`: dictionary specifying what to set in the config file
                - Key: variable from global config file to be used
                - Value:
                    - tuple of :
                        - number specifying the capture group
                        - number specifying the capture id of that group
                        - string specifying default value
                          (yes this is necessary)
        """
        self.rule = rule
        self.keys = keys
        self.logger = logging.getLogger('Systhemer.Progs.common.'
                                        + self.__class__.__name__)

    def _set(self, key, value, _buffer, scope_range, exclude_ranges):
        # Construct a list of all matches of 'rule' in the proper scope that
        # aren't excluded by any of the rules in exclude_ranges
        print(self.rule)
        matches = []
        for m in regex.finditer(self.rule,
                                _buffer[scope_range[0]:scope_range[1]]):

            excs = [utils.is_excluded(r, (m.start()+scope_range[0],
                                          m.end()+scope_range[0])) != 0
                    for r in exclude_ranges]

            if not (True in excs):
                matches.append(m)

        # check if empty list
        if matches:
            # for now, we only apply the value to the first key match
            match = matches[0]
        else:
            self.logger.warning('Found rule \'%s\' in program definition'
                                ' but not in configuration file!',
                                key)
            return None

        # replace the value in the buffer and return it
        sub_id = self.keys[key][0]
        # -1 for consistency with sub_id 1-based numbering
        sub_sub_id = self.keys[key][1]-1
        out_buffer \
            = _buffer[:scope_range[0]+match.starts(sub_id)[sub_sub_id]] \
            + value \
            + _buffer[scope_range[0]+match.ends(sub_id)[sub_sub_id]:]
        self.logger.debug('Value set: %s <- %s', key, value)
        return out_buffer


class Section(ConfigElement):
    """This defines a subsection in your configuration file.

    Example::

       Keyword1, Keyword2
       sub {
           Keyword1, Keyword2
       }

    "sub { }" is the subsection, to isolate the keywords
    """
    def __init__(self, name, startchar, endchar, *rules,
                 separator=r'[ \t\n]*'):
        """Build a `Section` object

        Example::

            foo, bar

            sub_name {
                foo, bar
            }

        * name: 'sub_name'. Can be empty.
        * startchar: '{'
        * endchar: '}'
        * *rules: same structure as a RuleTree, defined above
        * separator: whatever is between sub_name and { (" " in this case)
        """

        self.name = name
        self.startchar = startchar
        self.rules = rules
        self.endchar = endchar
        self.separator = separator
        for rule in self.rules:
            rule.parent = self

    def __iter__(self):
        return iter(self.rules)

    def __getitem__(self, key):
        return self.rules[key]
