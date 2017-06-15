"""Templates for configuring program function

Every program definition must inherit from the :class:`ProgDef` class
"""
import logging
import re
from .common import utils
from .config import RuleTree, Section
from . import common


class ProgDef(object):
    """Template for program definitions.

    Program definitions should inherit from this class
    and should define settings in the config dictionary
    (see already written definitions for example implementation).

    If a program definition needs special handling, you may
    override the :meth:`set` method.
    """

    def pre_init(self):
        """Pre-init defaults.
        If you absolutely have to override __init__
        then you must at least include pre_init in __init__.
        """
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.filebuff = None
        self.config = RuleTree()  # add definitions here
        self.special_excludes = []
        self.presave_hooks = []
        self.postsave_hooks = []

    def __init__(self, *args, **kwargs):
        """Build a `ProgDef` object.
        """
        self.pre_init()

        if utils.get_setting('show_diff'):
            self.presave_hooks.append(self.gen_diff)
        if utils.get_setting('make_backup'):
            self.presave_hooks.append(self.mk_backup)

        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
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

    def get_key_type(self, key):
        try:
            return self.find_rules(key, self.config)[0].get_key_type(key)
        except IndexError:
            pass

    def get_file_path(self):
        """Get file path from Settings.
        If not found there, get from default path."""

        setting_name = self.name + '_file_path'
        fallback = self.get_default_path()
        msg = "File path for: '{}' not set! Please set a value for option: {}"
        msg = msg.format(self.name, setting_name)

        file_path = utils.get_setting(setting_name, fallback,
                                      msg=msg, critical=True)
        return file_path

    def get_file_buffer(self):
        """Check if filebuffer exists. If not, one is created."""
        # if filebuffer doesn't exist
        if self.filebuff is None:
            # get file path from Settings if file is not foudn in default path
            file_path = self.get_file_path()

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
                # continue_parent = False
                for e in excludes:
                    # print(e, (start_char.start(), end_pos+end_char.end()))
                    if utils.is_excluded(e, (start_char.start(),
                                             end_pos+end_char.end())):
                        self.logger.error('section \'%s\' found but'
                                          ' in wrong scope!'
                                          ' returning None)',
                                          section_obj.name)
                        count += 1
                        break

                # if loop executes with no `break`
                else:
                    return (start_pos, end_pos, exclusions)

            # if falls through...
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

    def gen_diff(self):
        """Generate and print a diff of the change in config file."""

        file_path = self.get_file_path()

        with open(file_path) as fbefore:
            before = fbefore.read()
        after = self.get_file_buffer()
        import difflib

        before = before.splitlines(keepends=True)
        after = after.splitlines(keepends=True)

        ffile = file_path
        tfile = file_path

        if not utils.get_setting('no_colorlog'):
            esc = '\x1b[{}m'
            red, green, cyan, none = 31, 32, 36, 0
            reset = esc.format(0)
        else:
            esc = '{}'
            red = green = cyan = none = ''
            reset = ''

        # === git-like diff ===
        if not utils.get_setting('alt_diff'):
            for l in difflib.unified_diff(before, after,
                                          fromfile=ffile, tofile=tfile):
                his = {'+': green, '-': red, ' ': none, '@': cyan}
                hi = esc.format(his[l[0]])
                print('{hi}{line}'.format(hi=hi, line=l), end=reset)

        # === alternative intuitive diff ===
        else:
            prev_line = ''
            for l in difflib.ndiff(before, after):
                if not prev_line:
                    prev_line = l
                    continue

                his = {'+': green, '-': red, ' ': none, '?': cyan}
                hi = esc.format(his[prev_line[0]])
                if l[0] == '?':
                    offset = 0
                    lout = hi+prev_line[0]+reset
                    prev_line = prev_line[1:]
                    for m in re.finditer(r'(\^)+', l):
                        lout += '{lb}{hi}{ch}{reset}'.format(
                            lb=prev_line[offset:m.start()-1],
                            ch=prev_line[m.start()-1:m.end()-1],
                            hi=hi,
                            reset=reset
                        )
                        offset = m.end()-1
                    lout += prev_line[offset:]
                    print(lout, end=reset)
                else:
                    print('{hi}{line}'.format(hi=hi, line=prev_line),
                          end=reset)

                prev_line = l

    def mk_backup(self):
        """Save the old contents to a backup file"""
        self.logger.info('Writing backup file for program: `%s`...',
                         self.get_name())

        file_path = self.get_file_path()

        import shutil
        shutil.copy(file_path, file_path+'.bak', follow_symlinks=True)

    def do_save(self):
        """Save the file and run pre/post-save hooks."""

        # Pre-save
        self.logger.debug('Running pre-save hooks...')
        [h() for h in self.presave_hooks]

        # save
        self.logger.debug('Saving to config file...')
        if not utils.get_setting('no_save'):
            self.save()

        # Post-save
        self.logger.debug('Running post-save hooks...')
        [h() for h in self.postsave_hooks]

    def save(self):
        """Save the file.

        This method must be overridden.
        """
        raise NotImplementedError()
