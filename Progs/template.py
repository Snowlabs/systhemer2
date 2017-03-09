"""Template module fro program definitions"""
import logging
import re
from .common import Rule, Section


class ProgDef(object):
    """
    Template for program definitions:
        program definitions should inherit from this class
        and should define settings in the config dictionary
        (see already written definitions for example implementation)

        if a program definition needs special handling,
        you can override the set method
    """

    def __init__(self, Settings):
        self.name = self.__class__.__name__
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.filebuff = None
        self.config = {}  # add definitions here
        self.init()

    def init(self):
        """this method must be implemented"""
        raise NotImplementedError()

    def get_setting(self, setting, critical=True, msg=None):
        """Get a setting from self.Settings"""
        value = getattr(self.Settings, setting, None)
        if value is None:
            msg = msg if msg is not None else \
                  'Setting \'%s\' not set!' % setting
            if critical:
                self.logger.critical(msg)
                exit(1)
            else:
                self.logger.error(msg + ' Returning \'None\'.', setting)
                return None
        return value

    def get_file_buffer(self):
        """Checks if filebuffer exists. If not, one is created."""
        # if filebuffer doesn't exist
        if self.filebuff is None:
            # get file path from Settings
            file_path = getattr(self.Settings, self.name + '_file_path', None)
            file_path = self.get_setting(self.name + '_file_path',
                                         msg='File path for: \'%s\' not set!'
                                         ' Please set a value for option: %s'
                                         % (self.name,
                                            self.name + '_file_path'),
                                         critical=True)

            with open(file_path) as configfile:
                self.filebuff = configfile.read()

    def find_rules(self, key, rules):
        """
        recursive function that returns an
        array of all rules that contain 'key'
        """
        out = []
        # scan rules for key and when found add key to output array
        for rule_obj in rules:
            # calls itself for scanning section rules for key
            if isinstance(rule_obj, Section):
                out.extend(self.find_rules(key, rule_obj.rules))
            # check if rule_obj contains key
            elif isinstance(rule_obj, Rule):
                if key in rule_obj.keys:
                    out.append(rule_obj)
            # invalid type
            else:
                self.logger.critical('Member or descendant of self.config'
                                     ' has invalid type: \'%s\'',
                                     rule_obj.__class__)
                exit(1)
        return out

    def is_excluded(self, exclude_rule, check_range):
        """ check is the given range is within the exclude rule:
            args: exclude_rule: (depth, startpos, endpos)
                  check_range:  (startpos, endpos)
            returns: 1 if range is completely in the exclude range
                     2 if range is partially in the exclude range
                     0 if range is not at all in the exclude range
        """
        if check_range[0] >= exclude_rule[1] and \
           check_range[1] <= exclude_rule[2]:
            return 1
        if (check_range[0] in range(exclude_rule[1], exclude_rule[2]+1)) or \
           (check_range[1] in range(exclude_rule[1], exclude_rule[2]+1)):
            return 2
        return 0

    def narrow_buffer(self, section_obj, initial_buffer,
                      recur=False, recpos=0, recdepth=0, excludes=[]):
        """
        returns a tuple the start and end positions of the scope
        within the initial_buffer: (startpos, endpos)

        exclude rule format: (depth, startpos, endpos)
        """
        # main function
        if not recur:
            count = 0
            for start_char in re.finditer(section_obj.name
                                          + section_obj.separator
                                          + section_obj.startchar,
                                          initial_buffer):
                self.logger.debug('found start char for name: \'%s\'',
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
                    if self.is_excluded(e, (start_char.start(),
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
            self.logger.error('section \'%s\' not found!'
                              ' (returning None)', section_obj.name)
            return None

        # this recursive portion gets the position of the ending delimiter
        # NOTE: the recursion here could technically be replaced with a loop
        else:
            # look for start or end charcter
            end_or_start_char = re.search('(%s|%s)' %
                                          (section_obj.startchar,
                                           section_obj.endchar),
                                          initial_buffer[recpos:])
            # if either start or end character found
            if end_or_start_char is not None:
                is_startchar = re.search(section_obj.startchar,
                                         initial_buffer[recpos:]
                                         [end_or_start_char.start():
                                          end_or_start_char.end()])
                # if it's a start character
                if is_startchar is not None:
                    self.logger.debug('found start char')
                    # append a new exclude with None as end position
                    excludes.append((recdepth+1,
                                     recpos + end_or_start_char.end(),
                                     None))
                    return self.narrow_buffer(section_obj, initial_buffer,
                                              recur=True,
                                              recpos=recpos
                                              + end_or_start_char.end(),
                                              recdepth=recdepth+1,
                                              excludes=excludes)
                # if it's an end character
                else:
                    self.logger.debug('found endchar')
                    if recdepth == 0:
                        return (recpos+end_or_start_char.start(), excludes)
                    # find the first exclude tuple that has the same depth as
                    # the current depth and a value of None for the end
                    # position and set the end position for that exclude tuple
                    for i in range(len(excludes)):
                        if excludes[i][0] == recdepth and \
                           excludes[i][2] is None:
                            excludes[i] = (excludes[i][0],
                                           excludes[i][1],
                                           recpos + end_or_start_char.start())
                            break
                    return self.narrow_buffer(section_obj, initial_buffer,
                                              recur=True,
                                              recpos=recpos
                                              + end_or_start_char.end(),
                                              recdepth=recdepth-1,
                                              excludes=excludes)

    def get_proper_buffer(self, initial_buffer, rule_obj):
        """returns rule_objs scope portion of initial_buffer"""

        # generate hierarchy tree for rule_obj
        scope_tree = [rule_obj]
        for i in scope_tree:
            if i is None:
                break
            scope_tree.append(i.parent)
        scope_tree.reverse()
        if scope_tree[0] is not None:
            self.logger.error('root is not None! Something is wrong'
                              ' in rule hierarchy!')

        self.logger.debug('tree: %s', scope_tree)
        # hierarchy tree generated

        scope_tree.pop(0)
        out_buffer = initial_buffer
        exclude_ranges = []
        start = 0
        start_offset = 0
        is_in_root = True

        for i in scope_tree:
            if isinstance(i, Section):
                is_in_root = False

                for er in range(len(exclude_ranges)):
                    exclude_ranges[er] \
                        = (exclude_ranges[er][0],
                           exclude_ranges[er][1]-start,
                           exclude_ranges[er][2]-start)

                start, end, exclude_ranges \
                    = self.narrow_buffer(i, out_buffer,
                                         excludes=exclude_ranges)
                out_buffer = out_buffer[start:end]
                start_offset += start

        if is_in_root:
            return (0, len(initial_buffer))

        return (start_offset, (end-start)+start_offset)

    def _set(self, rule_obj, key, value, _buffer):
        """
        set a value to a certain key for
        a certain rule in the proper scope
        """
        scope_range = self.get_proper_buffer(_buffer, rule_obj)
        match = re.search(rule_obj.rule,
                          _buffer[scope_range[0]:scope_range[1]])
        sub_id = rule_obj.keys[key]
        out_buffer = _buffer[:scope_range[0]+match.start(sub_id)] \
            + value \
            + _buffer[scope_range[0]+match.end(sub_id):]
        self.logger.debug('Value set: %s <- %s', key, value)
        return out_buffer

    def set(self, key, value, section):
        """set a value to a certain key"""
        # Check if filebuffer exists. If not, create one
        self.get_file_buffer()

        # get array of rules that contain 'key'
        rules = self.find_rules(key, self.config)
        if rules != []:
            self.logger.debug('Key: \'%s\' Found! (found %s times)',
                              key, len(rules))
        else:
            self.logger.debug('Key: \'%s\' Not found', key)

        # go through rules applying 'value' for 'key'
        for rule_obj in rules:
            self.filebuff = self._set(rule_obj, key, value, self.filebuff)
            # match = re.search(rule_obj.rule, self.filebuff)
            # sub_id = rule_obj.keys[key]
            # self.filebuff = self.filebuff[:match.start(sub_id)] \
            #     + value \
            #     + self.filebuff[match.end(sub_id):]
            # self.logger.debug('Value set: %s <- %s', key, value)

    def save(self):
        """this method must be implemented"""
        raise NotImplementedError()
