import re
import logging
from .template import ProgDef

class i3wm(ProgDef):
    """describes i3wm"""
    def init(self):
        self.config = {
            r'client\.focused[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)' : {
                'focused.border':       1,
                'titlebar':             1,
                'focused.background':   2,
                'focused.text':         3,
                'focused.indicator':    4,
                'focused.child_border': 5},
            r'client\.focused_inactive[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)' : {
                'focused_inactive.border':       1,
                'focused_inactive.background':   2,
                'focused_inactive.text':         3,
                'focused_inactive.indicator':    4,
                'focused_inactive.child_border': 5},
            r'client\.unfocused[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)' : {
                'unfocused.border':       1,
                'unfocused.background':   2,
                'unfocused.text':         3,
                'unfocused.indicator':    4,
                'unfocused.child_border': 5},
            r'client\.urgent[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)' : {
                'urgent.border':       1,
                'urgent.background':   2,
                'urgent.text':         3,
                'urgent.indicator':    4,
                'urgent.child_border': 5},
            r'client\.placeholder[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)[ \t]+(\S+)' \
            r'[ \t]+(\S+)' : {
                'placeholder.border':       1,
                'placeholder.background':   2,
                'placeholder.text':         3,
                'placeholder.indicator':    4,
                'placeholder.child_border': 5},
            r'client\.background[ \t]+(\S+)': {
                'background': 1},
        }

    def save(self):
        newfile = open('./files/i3_dummy.out', 'w')
        newfile.write(self.filebuff)
        newfile.close()
