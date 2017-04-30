"""Templates for configuring program function

Every program definition must inherit from the :class:`ProgDef` class
"""
import logging
import re
from .common import Rule, Section, utils
from . import common


class ProgDef(object):
    """Template for program definitions.

    Program definitions should inherit from this class
    and should define settings in the config dictionary
    (see already written definitions for example implementation).

    If a program definition needs special handling, you may
    override the :meth:`set` method.
    """

    def __init__(self, Settings, *args, **kwargs):
        """Build a `ProgDef` object.
        """
        self.name = self.__class__.__name__
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.filebuff = None
        self.config = common.RuleTree()  # add definitions here
        self.special_excludes = []
        self.init(*args, **kwargs)

    def init(self):
        """Define rules for configuration.

        This method must set the `self.config` variable, which must
        be of type `common.ConfigElement`. Usage is defined under the
        `Common` and `Example` sections.

        This method must be overridden.
        """
        raise NotImplementedError()

    def is_installed(self):
        """Check if the program is installed on the target system.

        Returns a boolean.

        This method must be overridden.
        """
        raise NotImplementedError()

    def get_default_path(self):
        """Return the path to use for configuration.

        This method must be overridden.
        """
        raise NotImplementedError()

    def get_name(self):
        """Returns the name of the program. Class name by default.

        Can be overridden if necessary
        """
        return self.name

    def get_config(self):
        """Returns the config rule tree.

        Can be overridden if necessary
        """
        return self.config

    def get_setting(self, setting, default=None, critical=True, msg=None):
        """Get a setting from self.Settings.
        NOTE: probably should get moved to common module..."""
        value = getattr(self.Settings, setting, None)
        if value is None:
            msg = msg if msg is not None else \
                  'Setting \'%s\' not set!' % setting
            if critical:
                self.logger.critical(msg)
                exit(1)
            else:
                self.logger.error(msg + ' Returning \'None\'.', setting)
                return default
        return value

    def get_key_type(self, key):
        try:
            return self.find_rules(key, self.config)[0].get_key_type(key)
        except IndexError:
            pass

    def get_file_buffer(self):
        """Check if filebuffer exists. If not, one is created."""
        # if filebuffer doesn't exist
        if self.filebuff is None:
            # get file path from Settings if file is not foudn in default path
            file_path = self.get_setting(self.name + '_file_path',
                                         self.get_default_path(),
                                         msg='File path for: \'%s\' not set!'
                                         ' Please set a value for option: %s'
                                         % (self.name,
                                            self.name + '_file_path'),
                                         critical=True)
            if not file_path:
                file_path = self.get_default_path()

            with open(file_path) as configfile:
                self.filebuff = configfile.read()
                self.logger.debug('Created filebuffer from %s', file_path)
        return self.filebuff

    def find_rules(self, key, rules):
        """Return an array of rule objects that contain `key`.
        """
        return [l for l in rules.get_leaves() if key in l.keys]

    def narrow_buffer(self, section_obj, initial_buffer,
                      recur=False, recpos=0, recdepth=0, excludes=None):
        """Return a tuple for the start and end of the scope.

        Returns a tuple the start and end positions of the scope
        within the initial_buffer: (startpos, endpos).

        Exclude rule format: (depth, startpos, endpos).
        """
        excludes = [] if excludes is None else excludes

        # main function
        if not recur:
            count = 0
            for start_char in re.finditer(section_obj.name
                                          + section_obj.separator
                                          + section_obj.startchar,
                                          initial_buffer):
                self.logger.log(common.Settings.VDEBUG,
                                'found start char for name: \'%s\'',
                                section_obj.name)
                start_pos = start_char.end()
                (end_pos, exclusions) = self.narrow_buffer(
                    section_obj, initial_buffer, recur=True,
                    recpos=start_pos)
                end_char = re.search(section_obj.endchar,
                                     initial_buffer[end_pos:])
                continue_parent = False
                for e in excludes:
                    # print(e, (start_char.start(), end_pos+end_char.end()))
                    if utils.is_excluded(e, (start_char.start(),
                                             end_pos+end_char.end())):
                        self.logger.error('section \'%s\' found but'
                                          ' in wrong scope!'
                                          ' returning None)',
                                          section_obj.name)
                        count += 1
                        continue_parent = True
                        break
                if continue_parent:
                    continue
                return (start_pos, end_pos, exclusions)
            self.logger.warning('section \'%s\' not found!'
                                ' (returning None)', section_obj.name)
            return None

        # this recursive portion gets the position of the ending delimiter
        # NOTE: the recursion here could technically be replaced with a loop
        # DONE: it is no longer unnecessarily recursive!
        else:
            depth = 0
            for end_or_start_char in re.finditer('(%s|%s)' %
                                                 (section_obj.startchar,
                                                  section_obj.endchar),
                                                 initial_buffer[recpos:]):
                is_startchar = re.search(section_obj.startchar,
                                         initial_buffer[recpos:]
                                         [end_or_start_char.start():
                                          end_or_start_char.end()])
                # if it's a start character
                if is_startchar is not None:
                    depth += 1
                    self.logger.log(common.Settings.VDEBUG, 'found start char')
                    # append a new exclude with None as end position
                    excludes.append((depth,
                                     recpos + end_or_start_char.end(),
                                     None))

                # if it's an end character
                else:
                    self.logger.log(common.Settings.VDEBUG, 'found end char')
                    if depth == 0:
                        return (recpos+end_or_start_char.start(), excludes)
                    # find the first exclude tuple that has the same depth as
                    # the current depth and a value of None for the end
                    # position and set the end position for that exclude tuple
                    for i in range(len(excludes)):
                        if excludes[i][0] == depth and \
                           excludes[i][2] is None:
                            excludes[i] = (excludes[i][0],
                                           excludes[i][1],
                                           recpos + end_or_start_char.start())
                            break
                    depth -= 1

    def get_proper_buffer(self, initial_buffer, rule_obj):
        """Return rule_objs scope portion of initial_buffer."""

        # hierarchy tree for rule_obj
        scope_tree = rule_obj.get_tree()

        scope_tree.pop(0)
        out_buffer = initial_buffer
        exclude_ranges = []
        start = 0
        start_offset = 0
        is_in_root = True

        for ce in scope_tree:
            if isinstance(ce, Section):
                is_in_root = False

                for er in range(len(exclude_ranges)):
                    exclude_ranges[er] \
                        = (exclude_ranges[er][0],
                           exclude_ranges[er][1]-start,
                           exclude_ranges[er][2]-start)

                buffer_exists = self.narrow_buffer(ce, out_buffer,
                                                   excludes=exclude_ranges)
                if buffer_exists:
                    start, end, exclude_ranges = buffer_exists
                else:
                    return None

                out_buffer = out_buffer[start:end]
                start_offset += start

        # print(exclude_ranges)

        if is_in_root:
            return (0, len(initial_buffer)), exclude_ranges

        return (start_offset, (end-start)+start_offset), exclude_ranges

    def _set(self, rule_obj, key, value, _buffer):
        """Set a `value` to `key` according to `rule_obj`.

        Internal function.
        """

        section_exists = self.get_proper_buffer(_buffer, rule_obj)
        if section_exists:
            scope_range, exclude_ranges = section_exists
        else:
            return None

        return rule_obj._set(key, value, _buffer, scope_range, exclude_ranges)
        # # Construct a list of all matches of 'rule' in the proper scope that
        # # aren't excluded by any of the rules in exclude_ranges
        # print(rule_obj.rule)
        # matches = []
        # for m in re.finditer(rule_obj.rule,
        #                      _buffer[scope_range[0]:scope_range[1]]):
        #     excs = [self.is_excluded(r, (m.start()+scope_range[0],
        #                                  m.end()+scope_range[0])) != 0
        #             for r in exclude_ranges]
        #     if not (True in excs):
        #         matches.append(m)

        # # matches = [m
        # #            for m
        # #            in re.finditer(rule_obj.rule,
        # #                           _buffer[scope_range[0]:scope_range[1]])
        # #            if not (True in [
        # #                    self.is_excluded(r, (m.start()+scope_range[0],
        # #                                         m.end()+scope_range[0])) != 0
        # #                    for r in exclude_ranges
        # #                    ])]

        # # check if empty list
        # if matches:
        #     # for now, we only apply the value to the first key match
        #     match = matches[0]
        # else:
        #     self.logger.warning('Found rule \'%s\' in program definition'
        #                         ' but not in configuration file!',
        #                         key)
        #     return None

        # # replace the value in the buffer and return it
        # sub_id = rule_obj.keys[key]
        # out_buffer = _buffer[:scope_range[0]+match.start(sub_id)] \
        #     + value \
        #     + _buffer[scope_range[0]+match.end(sub_id):]
        # self.logger.debug('Value set: %s <- %s', key, value)
        # return out_buffer

    def set(self, key, value, section):
        """Set `value` to `key`.

        Can be overridden if there are specific needs.
        """
        # Check if filebuffer exists. If not, create one
        self.get_file_buffer()

        # get array of rules that contain 'key'
        rules = self.find_rules(key, self.config)
        if rules:
            self.logger.debug('Key: \'%s\' Found! (found %s times)',
                              key, len(rules))
        else:
            self.logger.debug('Key: \'%s\' Not found', key)

        # go through rules applying 'value' for 'key'
        for rule_obj in rules:
            self.filebuff = self._set(rule_obj, key, value, self.filebuff)

    def save(self):
        """Save the file.

        This method must be overridden.
        """
        raise NotImplementedError()
