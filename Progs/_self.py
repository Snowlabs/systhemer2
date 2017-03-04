from .template import ProgDef
import logging


class _self(ProgDef):
    """describes self"""
    def __init__(self, prog_name, Settings):
        self.name = prog_name
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.Progs.' + self.name)
        self.config = {}  # add definitions here

    def set(self, key, value, section):
        if section == 'self':
            self.logger.debug('%s<- %s', key, value)
            setattr(self.Settings, key, value)

    def save(self):
        return
