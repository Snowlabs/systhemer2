#! /usr/bin/env python3
"""Systhemer2.0 (Now in python!)"""
from logger import setup_logger
import toml
import Progs


class Settings:
    theme_file_path = './files/theme.toml'


def convert_toml(path):
    """Takes path to toml file and return dictionary"""
    with open(path) as toml_file:
        return toml.loads(toml_file.read())


def run():
    """run program"""
    # initialize
    logger = setup_logger()
    Progs.setup(Settings)

    # load toml file
    logger.info('Loading theme/config file at: \'%s\'...',
                Settings.theme_file_path)
    try:
        theme = convert_toml(Settings.theme_file_path)
    except toml.TomlDecodeError as e:
        logger.critical('Syntax error in %s: %s',
                        Settings.theme_file_path, e)
        exit(1)

        logger.debug('Theme file data: %s', theme)
    # toml file loaded
    # initialized

    # Apply theme
    # loop though program definitions
    for prog_def in Progs.prog_defs:
        # apply theme to curent program
        logger.info('Applying theme for program: \'%s\'',
                    prog_def.name)

        # loop through sections
        for section in theme:
            logger.debug('Applying section: %s', section)
            # loop through keys in current section
            for key in theme[section]:
                # set(key, value)
                prog_def.set(key, theme[section][key], section)

        # save theme for current program
        logger.info('Writing to config file for program: \'%s\'',
                    prog_def.name)
        prog_def.save()
    # theme applied


if __name__ == '__main__':
    run()
                    
