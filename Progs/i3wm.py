from .template import ProgDef
from .common import RuleTree, Rule, RuleVLen, Section
from . import value


class i3wm(ProgDef):
    """describes i3wm"""

    def init(self):
        space = r'[ \t]+'
        fmat = value.Color.Formatter(value.Color.formats.hexRRGGBB)
        def_val = '#ffffff'
        self.config = RuleTree(
            # client.focused key key key key key
            #                ^1  ^2  ^3  ^4  ^5
            RuleVLen([r'client\.focused(?:', space, fmat, r'){1,5}'], {
                'focused.border':       (1, 1, def_val),
                'titlebar':             (1, 1, def_val),
                'focused.background':   (1, 2, def_val),
                'focused.text':         (1, 3, def_val),
                'focused.indicator':    (1, 4, def_val),
                'focused.child_border': (1, 5, def_val)}),
            Section(r'([ \t\n]+|^)bar', '{', '}',
                    Rule([r'test', space, fmat], {
                        'testval': 1}),
                    Rule([r'test2', space, fmat], {
                        'testval2': 1}),
                    Section(r'([ \t\n]+|^)subbar', '{', '}',
                            Rule([r'test3', space, fmat], {
                                'testval3': 1}))),
            Rule([r'client\.focused_inactive'] + [space, fmat]*5, {
                'focused_inactive.border':       1,
                'focused_inactive.background':   2,
                'focused_inactive.text':         3,
                'focused_inactive.indicator':    4,
                'focused_inactive.child_border': 5}),
            Rule([r'client\.unfocused'] + [space, fmat]*5, {
                'unfocused.border':       1,
                'unfocused.background':   2,
                'unfocused.text':         3,
                'unfocused.indicator':    4,
                'unfocused.child_border': 5}),
            Rule([r'client\.urgent'] + [space, fmat]*5, {
                'urgent.border':       1,
                'urgent.background':   2,
                'urgent.text':         3,
                'urgent.indicator':    4,
                'urgent.child_border': 5}),
            Rule([r'client\.placeholder'] + [space, fmat]*5, {
                'placeholder.border':       1,
                'placeholder.background':   2,
                'placeholder.text':         3,
                'placeholder.indicator':    4,
                'placeholder.child_border': 5}),
            Rule([r'client\.background', space, fmat], {
                'background': 1}),
            Section(r'([ \t\n]+|^)bar', '{', '}',
                    Rule([r'test', space, fmat], {
                        'testval': 1}),
                    Rule([r'test2', space, fmat], {
                        'testval2': 1}),
                    Section(r'([ \t\n]+|^)subbar', '{', '}',
                            Rule([r'test3', space, fmat], {
                                'testval3': 1})))
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
