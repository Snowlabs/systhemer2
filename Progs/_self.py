from .template import ProgDef
from . import common
from . import value
import logging


class _self(ProgDef):
    """describes self"""
    def __init__(self, Settings):
        self.pre_init(Settings)

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
