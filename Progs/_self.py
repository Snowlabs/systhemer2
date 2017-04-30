from .template import ProgDef
from . import common
from . import value
import logging


class _self(ProgDef):
    """describes self"""
    def __init__(self, Settings):
        self.name = self.__class__.__name__
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.config = common.RuleTree()  # add definitions here

    def set(self, key, val, section):
        if section == 'self':
            if isinstance(val, value.Litteral):
                val = val.format()
                self.logger.debug('%s<- %s', key, val)
                setattr(self.Settings, key, val)
            else:
                self.logger.critical('Invalid data type for _self variable!')
                exit(1)

    def is_installed(self):
        return True

    def save(self):
        return
