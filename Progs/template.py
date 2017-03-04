"""Template module fro program definitions"""
import logging
import re


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

    def get_file_buffer(self):
        """Checks if filebuffer exists. If not, one is created."""
        # if filebuffer doesn't exist
        if self.filebuff is None:
            # get file path from Settings
            file_path = getattr(self.Settings, self.name + '_file_path', None)

            # if file path is defined in settings
            if file_path is not None:
                # create the filebuffer
                with open(file_path) as configfile:
                    self.filebuff = configfile.read()
            else:
                self.logger.critical('File path for: \'%s\' not set!'
                                     'Please set a value for option: %s',
                                     self.name, self.name + '_file_path')
                exit(1)

    def set(self, key, value, section):
        """set a value to a certain key"""
        self.get_file_buffer()
        key_found = False

        # cycle through rules
        for regex in self.config:

            # check if key exists in the current rule
            if key in self.config[regex]:

                key_found = True
                self.logger.debug('Key: \'%s\' Found!', key)

                match = re.search(regex, self.filebuff)
                sub_id = self.config[regex][key]
                self.filebuff = self.filebuff[:match.start(sub_id)] \
                    + value \
                    + self.filebuff[match.end(sub_id):]
                self.logger.debug('Value set: %s <- %s', key, value)

        if not key_found:
            self.logger.debug('Key: \'%s\' Not found', key)

    def save(self):
        """this method must be implemented"""
        raise NotImplementedError()
