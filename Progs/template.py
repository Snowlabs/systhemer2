import logging
import re


class ProgDef(object):
    """
    Template for program definitions:
        program definitions should inherit from this class
        and should define settings in the config dictionary
        (see already written definitions for example implementation)

        if a program deifinition needs special handling,
        you can override the set method
    """
    def __init__(self, conf_file, prog_name):
        self.name = prog_name
        self.logger = logging.getLogger('Systhemer.Progs.'+self.name)
        self.filebuff = open(conf_file).read()
        self.config = {} #add definitions here
        self.init()

    def init(self):
        """this method must be implemented"""
        raise NotImplementedError()

    def set(self, key, value):
        """set a value to a certain key"""
        key_found = False
        for regex in self.config:
            if key in self.config[regex]:
                key_found = True
                self.logger.debug('key: \'%s\' Found!', key)
                match = re.search(regex, self.filebuff)
                sub_id = self.config[regex][key]
                self.filebuff = self.filebuff[:match.start(sub_id)] + \
                                value + self.filebuff[match.end(sub_id):]
                self.logger.debug('value set: %s <- %s', key, value)

        if not key_found:
            self.logger.debug('key: \'%s\' Not found', key)

    def save(self):
        """this method must be implemented"""
        raise NotImplementedError()
