from .template import ProgDef
from .common import Rule, Section


class i3wm(ProgDef):
    """describes i3wm"""

    def init(self):
        space = r'[ \t]+'
        key = r'(\S+)'
        self.config = [
            # client.focused key key key key key
            #                ^1  ^2  ^3  ^4  ^5
            Rule(r'client\.focused' + (space+key)*5, {
                'focused.border':       1,
                'titlebar':             1,
                'focused.background':   2,
                'focused.text':         3,
                'focused.indicator':    4,
                'focused.child_border': 5}),
            Rule(r'client\.focused_inactive' + (space+key)*5, {
                'focused_inactive.border':       1,
                'focused_inactive.background':   2,
                'focused_inactive.text':         3,
                'focused_inactive.indicator':    4,
                'focused_inactive.child_border': 5}),
            Rule(r'client\.unfocused' + (space+key)*5, {
                'unfocused.border':       1,
                'unfocused.background':   2,
                'unfocused.text':         3,
                'unfocused.indicator':    4,
                'unfocused.child_border': 5}),
            Rule(r'client\.urgent' + (space+key)*5, {
                'urgent.border':       1,
                'urgent.background':   2,
                'urgent.text':         3,
                'urgent.indicator':    4,
                'urgent.child_border': 5}),
            Rule(r'client\.placeholder' + (space+key)*5, {
                'placeholder.border':       1,
                'placeholder.background':   2,
                'placeholder.text':         3,
                'placeholder.indicator':    4,
                'placeholder.child_border': 5}),
            Rule(r'client\.background' + space + key, {
                'background': 1}),
            Section('bar', '{', [
                Rule(r'test' + space + key, {
                    'testval': 1}),
                Rule(r'test2' + space + key, {
                    'testval2': 1}),
                Section(r'subbar', '{', [
                    Rule(r'test3' + space + key, {
                        'testval3': 1}),
                ], '}')
            ], '}'),
        ]

    def save(self):  # saves in a new file for testing purposes
        # self.logger.debug(
        #     self.get_proper_buffer(self.filebuff,
        #                            self.config[1]))
        # self.logger.debug(
        #     self.get_proper_buffer(self.filebuff,
        #                            self.config[-1].rules[2].rules[0]))
        # self.logger.debug(self._set(self.config[-1].rules[2].rules[0], 'testval3', 'test_value',
        #                             self.filebuff))
        """save file"""
        outfile = self.get_setting('i3wm_out_file_path')
        self.logger.info('Saving...')
        with open(outfile, 'w') as newfile:
            newfile.write(self.filebuff)
