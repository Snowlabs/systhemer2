#! /usr/bin/env python3
"""Systhemer2.0 (Now in python!)"""
import sys
from logger import setup_logger
import toml
import Progs

THEME_FILE_PATH = './files/theme.toml'
VERBOSE_MODE = True

def convert_toml(path):
    """takes path to toml file and return dictionary"""
    with open(path) as toml_file:
        return toml.loads(toml_file.read())

class Main(object):
    """main object class"""
    def __init__(self):
        self.logger = setup_logger()
        self.theme = None
    def run(self):
        """run program"""
        self.logger.info('loading theme file at: \'%s\'...', THEME_FILE_PATH)

        try:
            self.theme = convert_toml(THEME_FILE_PATH)
        except toml.TomlDecodeError as e:
            self.logger.critical('Syntax error in %s: %s', THEME_FILE_PATH, e)
            exit(1)

        self.logger.debug('theme file data: %s', self.theme)

        for prog_def in Progs.prog_defs:
            self.logger.info('applying theme for program: \'%s\'', prog_def.name)
            for key in self.theme['theme']:
                prog_def.set(key, self.theme['theme'][key])
            self.logger.info('writing to config file for program: \'%s\'', prog_def.name)
            prog_def.save()



if __name__ == '__main__':
    Main().run()

