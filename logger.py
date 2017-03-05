import logging
from colorlog import ColoredFormatter


def setup_logger(Settings):
    fileHandler = logging.FileHandler('systhemer.log', mode='w')
    consHandler = logging.StreamHandler()
    fileFormatter = logging.Formatter(
        '%(levelname)-8s:%(name)-25s: %(message)s')
    llc = '%(line_log_color)s'
    mlc = llc + '%(message_log_color)s'
    lc = llc + '%(log_color)s'
    reset = '%(reset)s'

    consFormatter = ColoredFormatter(
        lc+'%(levelname)-8s'+reset+llc
        + ':%(name)-25s: ' + mlc+'%(message)s'+reset,
        log_colors={
            'DEBUG':    'bold_blue',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'line': {
                'DEBUG':    'bg_bold_black,bold_white'
            },
            'message': {
                'DEBUG':    'bold_blue',
                'ERROR':    'red',
                'CRITICAL': 'red'
            }
        })
    fileHandler.setLevel(logging.DEBUG)
    consHandler.setLevel(Settings.verbose)
    fileHandler.setFormatter(fileFormatter)
    consHandler.setFormatter(consFormatter if not Settings.no_colorlog
                             else fileFormatter)

    logger = logging.getLogger('Systhemer')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)
    logger.addHandler(consHandler)
    return logger
