from .template import ProgDef
from .common import RuleTree, Rule, RuleVLen, Section
from . import value


class i3wm(ProgDef):
    """describes i3wm"""

    def init(self):
        space = r'[ \t]+'
        key = r'(\S+)'
        fmat = value.Color.Formatter(value.Color.formats.hexRRGGBB)
        def_val = '#ffffff'
        self.config = RuleTree(
            # client.focused key key key key key
            #                ^1  ^2  ^3  ^4  ^5
            RuleVLen(r'client\.focused(?:' + space + key + r'){1,5}', {
                'focused.border':       (1, 1, def_val, fmat),
                'titlebar':             (1, 1, def_val, fmat),
                'focused.background':   (1, 2, def_val, fmat),
                'focused.text':         (1, 3, def_val, fmat),
                'focused.indicator':    (1, 4, def_val, fmat),
                'focused.child_border': (1, 5, def_val, fmat)}),
            Section(r'([ \t\n]+|^)bar', '{', '}',
                    Rule(r'test' + space + key, {
                        'testval': (1, fmat)}),
                    Rule(r'test2' + space + key, {
                        'testval2': (1, fmat)}),
                    Section(r'([ \t\n]+|^)subbar', '{', '}',
                            Rule(r'test3' + space + key, {
                                'testval3': (1, fmat)}))),
            Rule(r'client\.focused_inactive' + (space+key)*5, {
                'focused_inactive.border':       (1, fmat),
                'focused_inactive.background':   (2, fmat),
                'focused_inactive.text':         (3, fmat),
                'focused_inactive.indicator':    (4, fmat),
                'focused_inactive.child_border': (5, fmat)}),
            Rule(r'client\.unfocused' + (space+key)*5, {
                'unfocused.border':       (1, fmat),
                'unfocused.background':   (2, fmat),
                'unfocused.text':         (3, fmat),
                'unfocused.indicator':    (4, fmat),
                'unfocused.child_border': (5, fmat)}),
            Rule(r'client\.urgent' + (space+key)*5, {
                'urgent.border':       (1, fmat),
                'urgent.background':   (2, fmat),
                'urgent.text':         (3, fmat),
                'urgent.indicator':    (4, fmat),
                'urgent.child_border': (5, fmat)}),
            Rule(r'client\.placeholder' + (space+key)*5, {
                'placeholder.border':       (1, fmat),
                'placeholder.background':   (2, fmat),
                'placeholder.text':         (3, fmat),
                'placeholder.indicator':    (4, fmat),
                'placeholder.child_border': (5, fmat)}),
            Rule(r'client\.background' + space + key, {
                'background': (1, fmat)}),
            Section(r'([ \t\n]+|^)bar', '{', '}',
                    Rule(r'test' + space + key, {
                        'testval': (1, fmat)}),
                    Rule(r'test2' + space + key, {
                        'testval2': (1, fmat)}),
                    Section(r'([ \t\n]+|^)subbar', '{', '}',
                            Rule(r'test3' + space + key, {
                                'testval3': (1, fmat)})))
        )

    def is_installed(self):
        # TODO figure out a better way of doing this that actually works
        import os

        for p in os.getenv('PATH').split(':'):
            if os.path.isfile(p + '/i3'):
                return True

        return False

    def get_default_path(self):
        from . import common
        import os
        xdg_home = os.environ.get('XDG_CONFIG_HOME')
        dirs = [xdg_home + '/i3/config' if xdg_home else None,
                common.get_home_dir() + '/.i3/config']

        for p in [d for d in dirs if d]:
            if os.path.isfile(p):
                return p

        return None

    def save(self):  # saves in a new file for testing purposes
        """save file"""
        outfile = self.get_setting('i3wm_out_file_path',
                                   self.get_setting('i3wm_file_path'))
        self.logger.info('Saving to %s...', outfile)
        with open(outfile, 'w') as newfile:
            newfile.write(self.get_file_buffer())
