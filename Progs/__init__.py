from . import common
from . import template
prog_defs = []


def setup(Settings):
    """initializes the prog_defs array"""
    import os
    import logging
    global prog_defs

    prog_defs = []
    logger = logging.getLogger('Systhemer.Progs')

    for pf in filter(lambda p: p[-3:] == '.py' and
                     p[:-3] not in ['__init__', 'template', 'common'],
                     os.listdir('Progs')):
        logger.debug('found ProgDef: %s', pf)
        exec('from .' + pf[:-3] + ' import ' + pf[:-3])
        prog_defs.append(eval(pf[:-3] + '(Settings)'))
        if not isinstance(prog_defs[-1], template.ProgDef):
            logger.critical('Prog def \'%s\' does not inherit'
                            'from template.ProgDef!', pf[:-3])
            exit(1)

    common.Settings = Settings
